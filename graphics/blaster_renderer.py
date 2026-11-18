import math
import random

NUM_ROBOTS, NUM_LASERS, NUM_STARS = 5, 3, 50
MOVE_STARS, MOVE_STARS_X, MOVE_STARS_Y = True, 2, 1
MOTHER_SHIP_ENABLED = False

ROBOT_COLORS = [
    "#FF00FF", "#FFA500", "#FFFF00", "#FFFFFF", "#0000FF", "#00FFFF"
]
LASER_COLORS = ["#00FF00", "#FF0000"]
STAR_COLOR = "#FFFFFF"
EXPLOSION_COLORS = ["#FFFF00", "#FFA500"]
MOTHER_SHIP_COLOR = "#00008B"
MOTHER_LASER_COLOR = "#FFFFFF"


def rgb(hex_color):
    """Convert #RRGGBB into Cairo's 0.0–1.0 RGB values."""
    return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))


class Laser:
    def __init__(self):
        self.active = False
        self.start_x = self.start_y = self.end_x = self.end_y = 0


class Robot:
    def __init__(self):
        self.alive = False
        self.death = self.move_style = self.target = 0
        self.old_x = self.old_y = self.x = self.y = 0
        self.radius = 10
        self.color, self.laser_color = ROBOT_COLORS[0], LASER_COLORS[0]
        self.lasers = [Laser() for _ in range(NUM_LASERS)]


class BlasterRenderer:
    def __init__(self, width=900, height=650):
        self.width, self.height = max(1, width), max(1, height)
        self.robots = [Robot() for _ in range(NUM_ROBOTS)]
        self.frame = 0
        self.stars = []
        self.initialize_stars()

        self.mother_active = False
        self.mother_death = self.mother_hits = 0
        self.mother_old_x = self.mother_x = self.mother_y = 0
        self.mother_lasers = [Laser() for _ in range(8)]
        self.spawn_all_robots()

    def initialize_stars(self):
        self.stars = [
            [
                random.randrange(max(1, self.width)),
                random.randrange(max(1, self.height)),
                random.randrange(1, 5),
            ]
            for _ in range(NUM_STARS)
        ]

    def spawn_all_robots(self):
        for index in range(NUM_ROBOTS):
            self.spawn_robot(index)

    def spawn_robot(self, index):
        robot = self.robots[index]
        if robot.death or any(laser.active for laser in robot.lasers):
            return

        robot.alive = True
        robot.radius = random.randrange(7, 14)
        robot.move_style = random.randrange(2)
        robot.color = random.choice(ROBOT_COLORS)
        robot.laser_color = random.choice(LASER_COLORS)

        if random.randrange(2) == 0:
            x = random.randrange(max(1, self.width - robot.radius))
            y = 0 if random.randrange(2) == 0 else self.height - robot.radius
        else:
            y = random.randrange(max(1, self.height - robot.radius))
            x = 0 if random.randrange(2) == 0 else self.width - robot.radius

        robot.x = robot.old_x = x
        robot.y = robot.old_y = y
        if NUM_ROBOTS > 1:
            robot.target = random.choice([
                other for other in range(NUM_ROBOTS) if other != index
            ])

    def move_stars(self):
        if not MOVE_STARS:
            return

        for star in self.stars:
            star[0] += MOVE_STARS_X
            star[1] += MOVE_STARS_Y
            if star[0] < 0:
                star[0] += self.width
            elif star[0] > self.width:
                star[0] -= self.width
            if star[1] < 0:
                star[1] += self.height
            elif star[1] > self.height:
                star[1] -= self.height

    def move_robot(self, index):
        robot = self.robots[index]
        if not robot.alive:
            if robot.death == 0:
                self.spawn_robot(index)
            return

        dx, dy = robot.x - robot.old_x, robot.y - robot.old_y
        if robot.move_style == 1:
            dx += random.choice((
                -random.randrange(1, 8), random.randrange(1, 8), 0
            ))
            dy += random.choice((
                -random.randrange(1, 8), random.randrange(1, 8), 0
            ))

        dx, dy = max(-3, min(3, dx)), max(-3, min(3, dy))
        robot.old_x, robot.old_y = robot.x, robot.y
        robot.x += dx
        robot.y += dy
        robot.x = max(0, min(self.width - robot.radius, robot.x))
        robot.y = max(0, min(self.height - robot.radius, robot.y))
        robot.move_style = 1 if random.randrange(10) == 0 else 0

        if NUM_ROBOTS > 1 and random.randrange(2) == 0:
            if random.randrange(200) == 0:
                robot.target = random.choice([
                    other for other in range(NUM_ROBOTS) if other != index
                ])
            laser = next((item for item in robot.lasers if not item.active), None)
            if laser is not None:
                self.fire_laser(robot, laser)

    def fire_laser(self, robot, laser):
        target = self.robots[robot.target]
        dx, dy = target.x - robot.x, target.y - robot.y

        if random.randrange(2) == 0:
            sx, sy = random.choice((-1, 1)), random.choice((-1, 1))
            laser.start_x = robot.x + sx * robot.radius
            laser.start_y = robot.y + sy * robot.radius
            laser.end_x = laser.start_x + sx * 7
            laser.end_y = laser.start_y + sy * 7
        else:
            distance = math.hypot(dx, dy)
            if distance == 0:
                return
            ux, uy = dx / distance, dy / distance
            laser.start_x = int(robot.x + ux * robot.radius)
            laser.start_y = int(robot.y + uy * robot.radius)
            laser.end_x = int(laser.start_x + ux * 7)
            laser.end_y = int(laser.start_y + uy * 7)

        laser.active = True

    def move_laser(self, laser, owner_index):
        if not laser.active:
            return

        for index, robot in enumerate(self.robots):
            if index == owner_index or not robot.alive:
                continue
            for x, y in (
                (laser.start_x, laser.start_y),
                (laser.end_x, laser.end_y),
            ):
                if (
                    abs(x - robot.x) < robot.radius - 1
                    and abs(y - robot.y) < robot.radius - 1
                ):
                    robot.alive = False
                    robot.death = 20
                    laser.active = False
                    return

        dx, dy = laser.start_x - laser.end_x, laser.start_y - laser.end_y
        laser.start_x, laser.start_y = laser.end_x, laser.end_y
        laser.end_x -= dx
        laser.end_y -= dy
        if not (0 <= laser.end_x < self.width and 0 <= laser.end_y < self.height):
            laser.active = False

    def update_mother_ship(self):
        if not MOTHER_SHIP_ENABLED:
            return

        if (
            not self.mother_active
            and self.mother_death == 0
            and random.randrange(150) == 0
        ):
            self.mother_active = True
            self.mother_hits = 10
            self.mother_y = random.randrange(max(1, self.height - 7))
            self.mother_x = 0 if random.randrange(2) == 0 else self.width - 25
            self.mother_old_x = self.mother_x

        if self.mother_active:
            self.mother_old_x = self.mother_x
            direction = 1 if self.mother_x < self.width / 2 else -1
            self.mother_x += direction * 3
            if self.mother_x < -25 or self.mother_x > self.width:
                self.mother_active = False

    def update(self, width, height):
        self.frame += 1
        self.width, self.height = max(1, width), max(1, height)
        self.move_stars()

        for index, robot in enumerate(self.robots):
            self.move_robot(index)
            if robot.death > 0:
                robot.death -= 1
            for laser in robot.lasers:
                if laser.active:
                    self.move_laser(laser, index)

        if self.mother_death > 0:
            self.mother_death -= 1
        self.update_mother_ship()

    @staticmethod
    def draw_circle(cr, x, y, diameter, color):
        cr.set_source_rgb(*rgb(color))
        cr.arc(x + diameter / 2, y + diameter / 2, diameter / 2, 0, math.tau)
        cr.fill()

    def draw_explosion(self, cr, robot):
        frame = robot.death
        if frame in (20, 17, 12, 8, 3):
            color, size = EXPLOSION_COLORS[0], 27
        elif frame in (18, 14, 10, 6):
            color, size = EXPLOSION_COLORS[1], 27 if frame >= 8 else 19
        elif frame in (15, 13, 11, 9, 7, 4):
            color, size = "#000000", 27 if frame >= 7 else 19
        elif frame == 2:
            color, size = EXPLOSION_COLORS[1], 7
        elif frame == 1:
            color, size = "#000000", 7
        else:
            return

        x, y = robot.x + robot.radius / 3, robot.y + robot.radius / 3
        self.draw_circle(cr, x, y, size, color)

    def render(self, cr, width, height):
        self.width, self.height = max(1, width), max(1, height)
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        cr.set_source_rgb(*rgb(STAR_COLOR))

        for x, y, size in self.stars:
            cr.arc(x + size / 2, y + size / 2, size / 2, 0, math.tau)
            cr.fill()

        for robot in self.robots:
            if robot.alive:
                self.draw_circle(cr, robot.x, robot.y, robot.radius, robot.color)
            elif robot.death:
                self.draw_explosion(cr, robot)

        for robot in self.robots:
            cr.set_line_width(1)
            cr.set_source_rgb(*rgb(robot.laser_color))
            for laser in robot.lasers:
                if laser.active:
                    cr.move_to(laser.start_x, laser.start_y)
                    cr.line_to(laser.end_x, laser.end_y)
                    cr.stroke()

        if self.mother_active:
            self.draw_circle(
                cr, self.mother_x, self.mother_y, 25, MOTHER_SHIP_COLOR
            )