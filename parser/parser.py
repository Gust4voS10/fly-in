"""Map file parser.

This module reads the custom map description language used by the project
(``nb_drones``, ``start_hub``, ``end_hub``, ``hub`` and ``connection``
lines, with optional ``[key=value]`` metadata) and turns it into a
:class:`core.graph.Graph` populated with :class:`core.zone.Zone` and
:class:`core.connection.Connection` objects.
"""

from core.graph import Graph
from .exceptions import ParserError
from core.zone import Zone
from core.connection import Connection


VALID_ZONE_TYPES = {
    "normal",
    "blocked",
    "restricted",
    "priority"
}


class Parser:
    """Parses a map file into a :class:`core.graph.Graph`.

    Attributes:
        filename: Path to the map file to parse.
        graph: The graph being built while parsing.
        nb_drones: Number of drones declared by the ``nb_drones`` line
            (defaults to 1 if never set).
    """

    def __init__(self, filename: str) -> None:
        """Initialize the parser for a given map file.

        Args:
            filename: Path to the map file to parse.
        """
        self.filename = filename
        self.graph = Graph()
        self.nb_drones = 1

    def parse(self) -> Graph:
        """Read the map file and build the corresponding graph.

        Returns:
            The populated :class:`core.graph.Graph` instance.

        Raises:
            ParserError: If the file cannot be found or contains invalid
                instructions.
        """
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
                if not lines:
                    raise ParserError("Map file is empty")
        except FileNotFoundError as e:
            raise ParserError("Map file not found") from e

        for line_number, line in enumerate(lines, start=1):
            clean_line = line.strip()
            self._parse_line(clean_line, line_number)
        return self.graph

    def _parse_line(self, line: str, line_number: int) -> None:
        """Dispatch a single line to the appropriate parsing routine.

        Args:
            line: The stripped line content.
            line_number: 1-indexed line number, used for error reporting.

        Raises:
            ParserError: If the line does not match any known instruction.
        """
        if not line:
            return
        if line.startswith("#"):
            return
        if line.startswith("nb_drones:"):
            self._parse_nb_drones(line, line_number)
        elif line.startswith("start_hub:"):
            self._parse_zone(line, line_number, "start")
        elif line.startswith("end_hub:"):
            self._parse_zone(line, line_number, "end")
        elif line.startswith("hub:"):
            self._parse_zone(line, line_number, "hub")
        elif line.startswith("connection:"):
            self._parse_connection(line, line_number)
        else:
            pass
            raise ParserError(
                f"Line {line_number}: Invalid instruction"
                f"{line}")

    def _parse_nb_drones(self, line: str, line_number: int) -> None:
        """Parse the ``nb_drones:`` instruction.

        Args:
            line: The raw line containing the instruction.
            line_number: 1-indexed line number, used for error reporting.

        Raises:
            ParserError: If the value is missing, not an integer, or not
                strictly positive.
        """
        try:
            value = line.replace("nb_drones:", "").strip()

            self.nb_drones = int(value)

            if self.nb_drones <= 0:
                raise ParserError(
                    f"Line {line_number}: "
                    "Number of drones must be positive"
                )

        except ValueError as error:
            raise ParserError(
                f"Line {line_number}: Invalid drone number"
            ) from error

    def _parse_zone(
        self,
        line: str,
        line_number: int,
        zone_category: str
    ) -> None:
        """Parse a ``start_hub:``, ``end_hub:`` or ``hub:`` instruction.

        Args:
            line: The raw line containing the instruction.
            line_number: 1-indexed line number, used for error reporting.
            zone_category: One of ``"start"``, ``"end"`` or ``"hub"``,
                indicating which kind of zone is being declared.

        Raises:
            ParserError: If the zone definition is malformed, the
                coordinates are invalid, the name is invalid/duplicated,
                the zone type is unknown, or ``max_drones`` is invalid.
        """
        line = (
            line.replace("start_hub:", "")
            .replace("end_hub:", "")
            .replace("hub:", "")
            .strip()
        )

        parts = line.split()

        if len(parts) < 3:
            raise ParserError(
                f"Line {line_number}: Invalid zone definition"
            )

        try:
            name = parts[0]
            x = int(parts[1])
            y = int(parts[2])

        except ValueError as error:
            raise ParserError(
                f"Line {line_number}: Invalid coordinates"
            ) from error

        if "-" in name or " " in name:
            raise ParserError(
                f"Line {line_number}: "
                "Zone names cannot contain dashes or spaces"
            )

        if name in self.graph.zones:
            raise ParserError(
                f"Line {line_number}: Duplicate zone name '{name}'"
            )

        metadata_string = " ".join(parts[3:])

        metadata = self._parse_metadata(metadata_string)

        zone_type = metadata.get(
            "zone_type",
            metadata.get("zone", metadata.get("type", "normal"))
        )

        if zone_type not in VALID_ZONE_TYPES:
            raise ParserError(
                f"Line {line_number}: Invalid zone type '{zone_type}'"
            )

        try:
            if zone_category in ("start", "end"):
                max_drones = self.nb_drones
            else:
                max_value = (
                    metadata.get("max_drones")
                    or metadata.get("max-drones")
                    or metadata.get("maxdrones")
                    or metadata.get("maxDrone")
                    or "1"
                )
                max_drones = int(max_value)

            if max_drones <= 0:
                raise ParserError(
                    f"Line {line_number}: "
                    "max_drones must be positive"
                )

        except ValueError as error:
            raise ParserError(
                f"Line {line_number}: Invalid max_drones"
            ) from error

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=metadata.get("color", "none"),
            max_drones=max_drones
        )

        self.graph.add_zone(zone)

        if zone_category == "start":
            self.graph.start_zone = name

        elif zone_category == "end":
            self.graph.end_zone = name

    def _parse_connection(
        self,
        line: str,
        line_number: int
    ) -> None:
        """Parse a ``connection:`` instruction.

        Args:
            line: The raw line containing the instruction.
            line_number: 1-indexed line number, used for error reporting.

        Raises:
            ParserError: If the connection format is invalid, references
                an unknown zone, has an invalid ``max_link_capacity``, or
                duplicates an existing connection (in either direction).
        """

        line = line.replace("connection:", "").strip()

        parts = line.split()

        if len(parts) < 1:
            raise ParserError(
                f"Line {line_number}: Invalid connection"
            )

        connection_part = parts[0]

        if "-" not in connection_part:
            raise ParserError(
                f"Line {line_number}: Invalid connection format"
            )

        zone1, zone2 = connection_part.split("-")

        if zone1 not in self.graph.zones:
            raise ParserError(
                f"Line {line_number}: Unknown zone '{zone1}'"
            )

        if zone2 not in self.graph.zones:
            raise ParserError(
                f"Line {line_number}: Unknown zone '{zone2}'"
            )

        metadata_string = " ".join(parts[1:])

        metadata = self._parse_metadata(metadata_string)

        try:
            max_capacity = int(
                metadata.get("max_link_capacity", 1)
            )

            if max_capacity <= 0:
                raise ParserError(
                    f"Line {line_number}: "
                    "max_link_capacity must be positive"
                )

        except ValueError as error:
            raise ParserError(
                f"Line {line_number}: "
                "Invalid max_link_capacity"
            ) from error

        for connection in self.graph.connections:

            same_direction = (
                connection.zone1 == zone1
                and connection.zone2 == zone2
            )

            reverse_direction = (
                connection.zone1 == zone2
                and connection.zone2 == zone1
            )

            if same_direction or reverse_direction:
                raise ParserError(
                    f"Line {line_number}: Duplicate connection"
                )

        connection = Connection(
            zone1=zone1,
            zone2=zone2,
            max_link_capacity=max_capacity
        )

        self.graph.add_connection(connection)

    def _parse_metadata(
        self,
        metadata_string: str
    ) -> dict[str, str]:
        """Parse a ``[key=value key2=value2 ...]`` metadata block.

        Args:
            metadata_string: The raw metadata substring, including the
                surrounding square brackets, or an empty string if no
                metadata is present.

        Returns:
            A dictionary mapping metadata keys to their raw string values.
            Empty if ``metadata_string`` is empty.

        Raises:
            ParserError: If the metadata block is not wrapped in square
                brackets, or an item does not contain an ``=`` sign.
        """

        metadata: dict[str, str] = {}

        if not metadata_string:
            return metadata

        metadata_string = metadata_string.strip()

        if not (
            metadata_string.startswith("[")
            and metadata_string.endswith("]")
        ):
            raise ParserError(
                "Invalid metadata format"
            )

        metadata_string = metadata_string[1:-1]

        if not metadata_string:
            return metadata

        for item in metadata_string.split():

            if "=" not in item:
                raise ParserError(
                    f"Invalid metadata item '{item}'"
                )

            key, value = item.split("=", maxsplit=1)

            metadata[key] = value

        return metadata

    def _validate_required_data(self) -> None:
        """Validate that mandatory map data has been provided.

        Raises:
            ParserError: If ``nb_drones`` is missing/invalid, or if no
                ``start_hub``/``end_hub`` was declared.
        """

        if self.nb_drones <= 0:
            raise ParserError(
                "Missing or invalid nb_drones"
            )

        if not hasattr(self.graph, "start_zone"):
            raise ParserError(
                "Missing start_hub"
            )

        if not hasattr(self.graph, "end_zone"):
            raise ParserError(
                "Missing end_hub"
            )
