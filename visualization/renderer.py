import math
import pygame
from core.graph import Graph
from core.drone import Drone
from simulation.scheduler import Scheduler


class Renderer:
    def __init__(
        self,
        graph: Graph,
        drones: Drone
    ) -> None:

        self.graph = graph
        self.drones = drones
        self.turn = 0
        self.started = False
        self.porcent = 0.10
        self.zoom = 1.0

        pygame.init()

        info = pygame.display.Info()

        self.width = info.current_w
        self.height = info.current_h

        self._calculate_optimal_scale()

        self.screen = pygame.display.set_mode(
            (self.width, self.height))

        self.background = pygame.image.load(
            "visualization/assets/Deus.jpg"
        ).convert()

        self.blocked_image = pygame.image.load(
            "visualization/assets/placa_1.png"
        ).convert_alpha()

        self.blocked_image = pygame.transform.scale(
            self.blocked_image,
            (50, 50)
        )

        self.priority_image = pygame.image.load(
            "visualization/assets/placa_2.png"
            ).convert_alpha()

        self.priority_image = pygame.transform.scale(self.priority_image,
                                                     (40, 35))

        self.restricted_image = pygame.image.load(
            "visualization/assets/placa_3.png"
            ).convert_alpha()

        self.restricted_image = pygame.transform.scale(
            self.restricted_image,
            (60, 60))

        self.background = pygame.transform.scale(
            self.background,
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

    def _calculate_optimal_scale(self) -> None:
        if not self.graph.zones:
            self.base_scale = 80
            return

        min_x = min(zone.x for zone in self.graph.zones.values())
        max_x = max(zone.x for zone in self.graph.zones.values())
        min_y = min(zone.y for zone in self.graph.zones.values())
        max_y = max(zone.y for zone in self.graph.zones.values())

        map_width = max_x - min_x
        map_height = max_y - min_y

        available_width = self.width - 400
        available_height = self.height - 100

        if map_width == 0 or map_height == 0:
            self.base_scale = 80
        else:
            scale_x = available_width / (map_width + 2)
            scale_y = available_height / (map_height + 2)
            self.base_scale = min(scale_x, scale_y, 80)

    def _zoom_in(self) -> None:
        self.zoom = min(self.zoom + 0.2, 2.0)

    def _zoom_out(self) -> None:
        self.zoom = max(self.zoom - 0.2, 0.5)

    def _to_screen_position(
        self,
        x: int,
        y: int
    ) -> tuple[int, int]:

        scale = self.base_scale * self.zoom

        screen_x = x * scale + 100
        screen_y = y * scale + self.height // 2

        return screen_x, screen_y

    def _should_draw_label(self, x: int, y: int) -> bool:
        threshold = max(60, 70 * self.zoom)
        for zone in self.graph.zones.values():
            zone_x, zone_y = self._to_screen_position(zone.x, zone.y)
            if zone_x == x and zone_y == y:
                continue
            if math.hypot(zone_x - x, zone_y - y) < threshold:
                return False
        return True

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
        for drones in self.drones:

            counts[drones.current_zone] = (
                counts.get(
                    drones.current_zone,
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

            if zone.zone_type == "blocked":
                self.screen.blit(
                    self.blocked_image,
                    (
                        x - self.blocked_image.get_width() // 2,
                        y - self.blocked_image.get_height() // 2
                    )
                )

            if zone.zone_type == "restricted":
                self.screen.blit(
                    self.restricted_image,
                    (
                        x - self.restricted_image.get_width() // 2,
                        y - self.restricted_image.get_height() // 2
                    )
                )

            if zone.zone_type == "priority":
                self.screen.blit(
                    self.priority_image,
                    (
                        x - self.priority_image.get_width() // 2,
                        y - self.priority_image.get_height() // 2
                    )
                )

            if zone.zone_type == "":
                self.screen.blit(
                    self.blocked_image,
                    (
                        x - self.blocked_image.get_width() // 2,
                        y - self.blocked_image.get_height() // 2
                    )
                )

            if zone.zone_type == "blocked":
                self.screen.blit(
                    self.blocked_image,
                    (
                        x - self.blocked_image.get_width() // 2,
                        y - self.blocked_image.get_height() // 2
                    )
                )

            text = self.font.render(
                zone.name,
                True,
                (255, 255, 255)
            )

            if self._should_draw_label(x, y):
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
        for drones in self.drones:

            #  zone = self.graph.zones[
            #     drones.current_zone
            #  ]

            x, y = self._to_screen_position(
                drones.visual_x,
                drones.visual_y
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

    def _increase_speed(self) -> None:
        if self.porcent < 0.4:
            self.porcent += 0.1

    def _decrease_speed(self) -> None:
        if self.porcent > 0.1:
            self.porcent -= 0.1

    def _draw_info_panel(self) -> None:
        panel_width = 350
        panel_height = 400
        panel_x = self.width - panel_width - 20
        panel_y = 20

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (panel_x, panel_y, panel_width, panel_height),
            0
        )
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (panel_x, panel_y, panel_width, panel_height),
            2
        )

        font_small = pygame.font.SysFont(None, 24)
        font_title = pygame.font.SysFont(None, 28, bold=True)

        y_offset = panel_y + 15

        title = font_title.render("INFO PANEL", True, (255, 255, 255))
        self.screen.blit(title, (panel_x + 15, y_offset))
        y_offset += 40

        turn_text = font_small.render(f"Turn: {self.turn}", True,
                                      (255, 255, 255))
        self.screen.blit(turn_text, (panel_x + 15, y_offset))
        y_offset += 30

        speed_text = font_small.render(f"Speed: {self.porcent:.2f}", True,
                                       (255, 255, 255))
        self.screen.blit(speed_text, (panel_x + 15, y_offset))
        y_offset += 30

        zoom_text = font_small.render(f"Zoom: {self.zoom:.1f}x", True,
                                      (255, 255, 255))
        self.screen.blit(zoom_text, (panel_x + 15, y_offset))
        y_offset += 40

        self.screen.blit(
            font_small.render("CONTROLS:", True, (255, 200, 0)),
            (panel_x + 15, y_offset)
        )
        y_offset += 30

        controls = [
            "ENTER - Start/Restart",
            "R - Reset position",
            "V - Reverse (when done)",
            "RIGHT - Speed +0.1 (max 0.4)",
            "LEFT - Speed -0.1 (min 0.1)",
            "+ / - - Zoom In/Out",
            "ESC - Exit"
        ]

        for control in controls:
            text = font_small.render(control, True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 15, y_offset))
            y_offset += 25

    def _draw_start_message(self) -> None:
        if not self.started:
            title = self.font.render(
                "Press ENTER to start the simulation",
                True,
                (255, 255, 255)
            )
            reset = self.font.render(
                "Press R to reset the movement anytime",
                True,
                (255, 255, 255)
            )
            reverse = self.font.render(
                "Press V to reverse when all drones have finished",
                True,
                (255, 255, 255)
            )
            self.screen.blit(title, (20, self.height - 110))
            self.screen.blit(reset, (20, self.height - 80))
            self.screen.blit(reverse, (20, self.height - 50))

    def _reset_drones(self) -> None:
        start_zone = self.graph.zones[self.graph.start_zone]
        for drone in self.drones:
            drone.current_zone = self.graph.start_zone
            drone.path_index = 0
            drone.delivered = False
            drone.remaining_turns = 0
            drone.reverse_mode = False
            drone.target_x = start_zone.x
            drone.target_y = start_zone.y
            drone.visual_x = start_zone.x
            drone.visual_y = start_zone.y
        self.turn = 0
        self.started = False

    def _can_reverse(self) -> bool:
        return (
            all(drone.delivered for drone in self.drones)
            and not self._can_restart_from_start()
        )

    def _set_reverse_mode(self) -> None:
        for drone in self.drones:
            drone.delivered = False
            drone.reverse_mode = True
            drone.remaining_turns = 0
        self.started = True
        self.turn = 0

    def _is_simulation_finished(self) -> bool:
        return all(drone.delivered for drone in self.drones)

    def _can_restart_from_start(self) -> bool:
        start_zone = self.graph.start_zone
        return (
            all(drone.delivered for drone in self.drones)
            and not any(drone.reverse_mode for drone in self.drones)
            and all(drone.current_zone == start_zone for drone in self.drones)
            and all(drone.path_index == 0 for drone in self.drones)
        )

    def _restart_forward_from_start(self) -> None:
        for drone in self.drones:
            drone.delivered = False
            drone.remaining_turns = 0
        self.started = True
        self.turn = 0

    def draw(self) -> None:

        self.screen.blit(
            self.background,
            (0, 0)
        )
        self._draw_connections()
        self._draw_zones()
        self._draw_drones()
        self._draw_info_panel()
        self._draw_start_message()

    def run(self,
            scheuduler: Scheduler,
            paths: dict[int, list[str]]
            ) -> None:
        running = True
        last_update = pygame.time.get_ticks()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_ESCAPE
                ):
                    running = False

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_RETURN
                ):
                    if not self.started or self._can_restart_from_start():
                        self._restart_forward_from_start()
                    last_update = pygame.time.get_ticks()

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_r
                ):
                    self._reset_drones()
                    last_update = pygame.time.get_ticks()

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_v
                ):
                    if self._can_reverse():
                        self._set_reverse_mode()
                        last_update = pygame.time.get_ticks()

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_RIGHT
                ):
                    self._increase_speed()

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_LEFT
                ):
                    self._decrease_speed()

                if (
                    event.type == pygame.KEYDOWN and
                    (event.key == pygame.K_PLUS or
                     event.key == pygame.K_EQUALS)
                ):
                    self._zoom_in()

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_MINUS
                ):
                    self._zoom_out()

            current_time = pygame.time.get_ticks()
            if self.started and current_time - last_update >= 1000:
                if not self._is_simulation_finished():
                    scheuduler.execute_turn(self.drones,
                                            paths)
                    self.turn += 1
                last_update = current_time

            for drone in self.drones:
                drone.visual_x += (
                    drone.target_x - drone.visual_x
                ) * self.porcent
                drone.visual_y += (
                    drone.target_y - drone.visual_y
                ) * self.porcent
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
