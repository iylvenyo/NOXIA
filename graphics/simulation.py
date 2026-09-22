import math
import random

from .config import (
    ARMS,
    COLORS,
    DEFAULT_HEIGHT,
    DEFAULT_SEED,
    DEFAULT_WIDTH,
    FINPOINTS,
    LINE_WIDTH,
    TWO_PI,
    TURN_DELTA,
    WITHDRAW,
)
from .model import Arm, DrawCommand, Point

class NoxiaSimulation:

    def __init__(self):
        self.width = DEFAULT_WIDTH
        self.height = DEFAULT_HEIGHT
        self.arms_count = ARMS
        self.finpoints = FINPOINTS
        self.line_width = LINE_WIDTH
        self.withdraw = WITHDRAW
        self.turn_delta = TURN_DELTA
        self.mx = self.width - 1
        self.my = self.height - 1
        self.turn = 0.0
        self.frame = 0
        self.seed = DEFAULT_SEED
        self.rng = random.Random(self.seed)
        self.palette = self.make_smooth_palette(COLORS)
        self.arms = []
        self.points = []
        self.commands = []
        self.initialize()

    def rnd(self, limit):
        return self.rng.randrange(limit)

    def make_smooth_palette(self, requested):
        
        palette = []
        count = requested + 3

        for index in range(count):
            fraction = index / count
            phase = fraction * TWO_PI

            red = (128.0 + 127.0 * math.sin(phase)) / 255.0
            green = (
                128.0 + 127.0 * math.sin(phase + TWO_PI / 3.0)
            ) / 255.0
            blue = (
                128.0 + 127.0 * math.sin(phase + 2.0 * TWO_PI / 3.0)
            ) / 255.0

            palette.append((red, green, blue, 1.0))

        return palette

    def arm_start(self, arm_index):
        return arm_index * (self.finpoints + 1)

    def arm_points(self, arm_index):
        start = self.arm_start(arm_index)
        end = start + self.finpoints + 1
        return self.points[start:end]

    def initialize(self):
        
        self.mx = self.width - 1
        self.my = self.height - 1
        self.arms = []
        self.points = []
        self.commands = []
        self.turn = 0.0
        self.frame = 0

        for _arm_index in range(self.arms_count):
            self.initialize_arm()

    def initialize_arm(self):
        color_index = self.rnd(len(self.palette))
        color = self.palette[color_index]

        red = int(color[0] * 255.0 + 0.5)
        green = int(color[1] * 255.0 + 0.5)
        blue = int(color[2] * 255.0 + 0.5)

        pixel = (red << 16) | (green << 8) | blue

        growth = self.finpoints // 2 + self.rnd(self.finpoints // 2)
        rate = self.rnd(11) * self.rnd(11)

        while True:
            x = 1 - self.rnd(1001) // 500
            y = 1 - self.rnd(1001) // 500
            z = 1 - self.rnd(1001) // 500

            distance = x * x + y * y + z * z

            if distance < 1.0:
                break

        x *= 200
        y = self.my // 2 + y * 200
        z *= 200

        sx = int(x / 5)
        sy = int((y - self.my // 2) / 5)
        sz = int(z / 5)

        arm_points = [Point() for _ in range(self.finpoints + 1)]

        arm_points[0] = Point(x, y, z, sx, sy, sz)
        arm_points[1] = Point(x + sx, y + sy, z + sz)

        self.points.extend(arm_points)

        self.arms.append(
            Arm(
                color=color,
                pixel=pixel,
                numpt=1,
                growth=growth,
                rate=rate,
            )
        )

    def reset(self):
        self.rng = random.Random(self.seed)
        self.initialize()

    def create_points(self):
        withdraw_all = self.rnd(self.withdraw)

        for arm_index, arm in enumerate(self.arms):
            points = self.arm_points(arm_index)

            if withdraw_all == 0:
                arm.growth = -self.finpoints
                self.turn_delta = -self.turn_delta

            elif withdraw_all < 11:
                arm.growth = -arm.numpt

            elif self.rnd(100) < arm.rate and arm.growth > 0:
                arm.growth -= 1

                if arm.growth == 0:
                    arm.growth = -self.rnd(self.finpoints) - 1

                current_index = arm.numpt - 1

                if arm.numpt < self.finpoints - 1:
                    next_index = current_index + 1
                    arm.numpt += 1

                    current = points[current_index]
                    next_point = points[next_index]

                    next_point.sx = current.sx + self.rnd(3) - 1
                    next_point.sy = current.sy + self.rnd(3) - 1
                    next_point.sz = current.sz + self.rnd(3) - 1

                    lookahead = points[next_index + 1]

                    lookahead.x = next_point.x + next_point.sx
                    lookahead.y = next_point.y + next_point.sy
                    lookahead.z = next_point.z + next_point.sz

    def emit_arm_commands(self, arm_index, sin_turn, cos_turn):
        
        arm = self.arms[arm_index]

        if arm.numpt == 1:
            return

        points = self.arm_points(arm_index)
        center_x = self.mx // 2

        current = points[0]

        cx = current.x
        cy = current.y
        cz = current.z

        nx = 0.0
        ny = 0.0
        nz = 0.0

        for segment in range(arm.numpt - 1):
            next_point = points[segment + 1]

            nx = next_point.x + 2 - self.rnd(5)
            ny = next_point.y + 2 - self.rnd(5)
            nz = next_point.z + 2 - self.rnd(5)

            x1 = int(center_x + cx * cos_turn - cz * sin_turn)
            y1 = int(cy)

            x2 = int(center_x + nx * cos_turn - nz * sin_turn)
            y2 = int(ny)

            self.commands.append(
                DrawCommand(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    width=self.line_width,
                    color=arm.color,
                )
            )

            cx = nx
            cy = ny
            cz = nz

        x1 = int(self.mx // 2 + cx * cos_turn - cz * sin_turn)
        y1 = int(cy)

        x2 = int(self.mx // 2 + nx * cos_turn - nz * sin_turn)
        y2 = int(ny)

        self.commands.append(
            DrawCommand(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                width=self.line_width * 3,
                color=arm.color,
                is_tip=True,
            )
        )

    def build_frame_commands(self):
        self.commands = []

        sin_turn = math.sin(self.turn)
        cos_turn = math.cos(self.turn)

        for arm_index, arm in enumerate(self.arms):
            if self.rnd(25) < arm.rate and arm.growth < 0:
                if arm.numpt > 1:
                    arm.numpt -= 1

                arm.growth += 1

                if arm.growth == 0:
                    available = self.finpoints - arm.numpt
                    arm.growth = self.rnd(available) + 1

            self.emit_arm_commands(arm_index, sin_turn, cos_turn)

            self.turn += self.turn_delta

        self.create_points()

        if self.turn >= TWO_PI:
            self.turn -= TWO_PI
        elif self.turn <= -TWO_PI:
            self.turn += TWO_PI

    def step(self):
        self.frame += 1
        self.build_frame_commands()
