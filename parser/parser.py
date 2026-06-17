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
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.graph = Graph()
        self.nb_drones = 1

    def parse(self) -> Graph:
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError as e:
            raise ParserError("Map file not found") from e

        for line_number, line in enumerate(lines, start=1):
            clean_line = line.strip()
            self._parse_line(clean_line, line_number)
        return self.graph

    def _parse_line(self, line: str, line_number: int) -> None:
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

    def _parse_nb_drones(self, line: str, line_number: int):
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

    def _parse_zone(self, line: str, line_number: int, zone_category: str):
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
