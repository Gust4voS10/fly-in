import pygame
from core.graph import Graph
from core.drone import Drone


class Renderer:
    def __init__(
        self,
        graph: Graph,
        drone: Drone
    ) -> None:

        self.graph = graph
        self.drones = drone

        pygame.init()

        info = pygame.display.Info()

        self.width = info.current_w
        self.height = info.current_h

        self.screen = pygame.display.set_mode(
            (self.width, self.height))

        self.drone_image = pygame.image.load(
            "visualization/assets/drone.png").convert_alpha()
        self.drone_image = pygame.transform.scale(
            self.drone_image,
            (32, 32)
            )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            None,
            30
        )

    def _to_screen_position(
        self,
        x: int,
        y: int
    ) -> tuple[int, int]:

        scale = 80

        screen_x = x * scale + 100
        screen_y = y * scale + self.height // 2

        return screen_x, screen_y

    def _get_zone_color(self, color_name: str):
        colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 100, 255),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "white": (255, 255, 255)
        }

        return colors.get(
            color_name.lower(),
            (0, 200, 255)
        )

    def _count_drones_per_zone(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for drone in self.drones:

            counts[drone.current_zone] = (
                counts.get(
                    drone.current_zone,
                    0
                ) + 1
            )
        return counts

    def _draw_zones(self) -> None:

        for zone in self.graph.zones.values():

            x, y = self._to_screen_position(
                zone.x,
                zone.y
            )

            color = self._get_zone_color(zone.color)

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                25)

            text = self.font.render(
                zone.name,
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                text,
                (
                    x - 20,
                    y - 40
                )
            )
            counts = self._count_drones_per_zone()
            count = counts.get(zone.name, 0)
            if count > 0:

                text = self.font.render(
                    str(count),
                    True,
                    (255, 255, 255)
                )

                self.screen.blit(
                    text,
                    (
                        x - 5,
                        y + 30
                    )
                )

    def _draw_drones(self) -> None:
        for drone in self.drones:

            zone = self.graph.zones[
                drone.current_zone
            ]

            x, y = self._to_screen_position(
                zone.x,
                zone.y
            )

            self.screen.blit(
                self.drone_image,
                (
                    x - self.drone_image.get_width() // 2,
                    y - self.drone_image.get_height() // 2
                )
            )

    def _draw_connections(self) -> None:
        for connection in self.graph.connections:

            zone1 = self.graph.zones[
                connection.zone1
            ]

            zone2 = self.graph.zones[
                connection.zone2
            ]

            x1, y1 = self._to_screen_position(
                zone1.x,
                zone1.y
            )

            x2, y2 = self._to_screen_position(
                zone2.x,
                zone2.y
            )

            pygame.draw.line(
                self.screen,
                (255, 50, 255),
                (x1, y1),
                (x2, y2),
                4
            )

    def run(self) -> None:

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            self.screen.fill((30, 30, 30))
            self._draw_connections()
            self._draw_zones()
            self._draw_drones()

            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()
