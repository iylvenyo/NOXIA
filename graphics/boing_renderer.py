import ctypes
import math
import random
import time

import numpy as np
from OpenGL import GL


VERTEX_SHADER = """
#version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;

uniform mat4 u_mvp;
uniform float u_opacity;

out vec3 vertex_color;
out float vertex_opacity;

void main() {
    gl_Position = u_mvp * vec4(a_position, 1.0);
    vertex_color = a_color;
    vertex_opacity = u_opacity;
}
"""

FRAGMENT_SHADER = """
#version 330 core

in vec3 vertex_color;
in float vertex_opacity;
out vec4 fragment_color;

void main() {
    fragment_color = vec4(vertex_color, vertex_opacity);
}
"""


def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(fov / 2.0)
    return np.array(
        [
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far),
             (2 * far * near) / (near - far)],
            [0, 0, -1, 0],
        ],
        dtype=np.float32,
    )


def look_at(eye, target, up):
    eye = np.asarray(eye, dtype=np.float32)
    target = np.asarray(target, dtype=np.float32)
    up = np.asarray(up, dtype=np.float32)

    forward = target - eye
    forward /= np.linalg.norm(forward)
    side = np.cross(forward, up)
    side /= np.linalg.norm(side)
    true_up = np.cross(side, forward)

    view = np.identity(4, dtype=np.float32)
    view[0, :3] = side
    view[1, :3] = true_up
    view[2, :3] = -forward
    view[0, 3] = -np.dot(side, eye)
    view[1, 3] = -np.dot(true_up, eye)
    view[2, 3] = np.dot(forward, eye)
    return view


def translation(x, y, z):
    matrix = np.identity(4, dtype=np.float32)
    matrix[:3, 3] = (x, y, z)
    return matrix


def scaling(value):
    return np.diag([value, value, value, 1.0]).astype(np.float32)


def rotate_y(degrees):
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    return np.array(
        [
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )


def rotate_z(degrees):
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    return np.array(
        [
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )


class BoingRenderer:
    BALL_SIZE = 0.5
    SPEED = 1.0 / 800.0
    FRAME_SECONDS = 1.0 / 30.0
    TILES = 12
    THICKNESS = 0.05

    BACKGROUND = (0x8C / 255, 0x8C / 255, 0x8C / 255)
    GRID_COLOR = (0x99 / 255, 0x19 / 255, 0x99 / 255)
    BALL_RED = (0xCC / 255, 0x19 / 255, 0x19 / 255)
    BALL_WHITE = (0xF2 / 255, 0xF2 / 255, 0xF2 / 255)
    SHADOW_COLOR = (0x30 / 255, 0x30 / 255, 0x30 / 255)

    def __init__(self):
        self.program = self._make_program()
        self.mvp_location = GL.glGetUniformLocation(self.program, "u_mvp")
        self.opacity_location = GL.glGetUniformLocation(
            self.program, "u_opacity"
        )

        self.background = self._upload(self._make_background())
        self.grid = self._upload(self._make_grid())
        self.ball = self._upload(self._make_ball())
        self.shadow = self._upload(self._make_shadow())

        self.scanline_mesh = None
        self.scanline_height = 0

        self.position = np.array(
            [
                0.5 - self.BALL_SIZE / 2
                - random.uniform(0, 1 - self.BALL_SIZE),
                0.2,
                0.0,
            ],
            dtype=np.float32,
        )
        self.velocity = np.array(
            [
                self.SPEED * 6 + random.uniform(-self.SPEED, self.SPEED),
                0.0,
                self.SPEED * 6 + random.uniform(-self.SPEED, self.SPEED),
            ],
            dtype=np.float32,
        )
        self.acceleration = np.array([0.0, -self.SPEED, 0.0], dtype=np.float32)
        self.spin_speed = -self.SPEED * 7 * 360
        self.ball_spin = 0.0
        self.last_time = time.monotonic()

    @staticmethod
    def _compile_shader(shader_type, source):
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            message = GL.glGetShaderInfoLog(shader).decode("utf-8", "replace")
            GL.glDeleteShader(shader)
            raise RuntimeError(f"Boing shader compilation failed:\n{message}")

        return shader

    def _make_program(self):
        vertex = self._compile_shader(GL.GL_VERTEX_SHADER, VERTEX_SHADER)
        fragment = self._compile_shader(GL.GL_FRAGMENT_SHADER, FRAGMENT_SHADER)

        program = GL.glCreateProgram()
        GL.glAttachShader(program, vertex)
        GL.glAttachShader(program, fragment)
        GL.glLinkProgram(program)
        GL.glDeleteShader(vertex)
        GL.glDeleteShader(fragment)

        if not GL.glGetProgramiv(program, GL.GL_LINK_STATUS):
            message = GL.glGetProgramInfoLog(program).decode("utf-8", "replace")
            GL.glDeleteProgram(program)
            raise RuntimeError(f"Boing shader link failed:\n{message}")

        return program

    @staticmethod
    def _upload(vertices):
        data = np.asarray(vertices, dtype=np.float32)
        vao = GL.glGenVertexArrays(1)
        vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_STATIC_DRAW)

        stride = 6 * 4
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.c_void_p(0)
        )
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(
            1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.c_void_p(12)
        )
        GL.glEnableVertexAttribArray(1)
        GL.glBindVertexArray(0)

        return vao, vbo, len(data) // 6

    @staticmethod
    def _vertex(vertices, point, color):
        vertices.extend((*point, *color))

    @classmethod
    def _line(cls, vertices, start, end, color):
        cls._vertex(vertices, start, color)
        cls._vertex(vertices, end, color)

    @classmethod
    def _triangle(cls, vertices, a, b, c, color):
        cls._vertex(vertices, a, color)
        cls._vertex(vertices, b, color)
        cls._vertex(vertices, c, color)

    @classmethod
    def _make_background(cls):
        vertices = []
        color = cls.BACKGROUND
        cls._triangle(vertices, (-1, -1, 0), (1, -1, 0), (1, 1, 0), color)
        cls._triangle(vertices, (-1, -1, 0), (1, 1, 0), (-1, 1, 0), color)
        return vertices

    @classmethod
    def _make_grid(cls):
        vertices = []
        tiles = cls.TILES
        scale = 1.0 / (tiles + cls.THICKNESS)
        half = tiles / 2
        color = cls.GRID_COLOR

        for index in range(tiles + 1):
            value = (index - half) * scale

            # Back wall at z = -0.5.
            cls._line(
                vertices,
                (-half * scale, value, -0.5),
                (half * scale, value, -0.5),
                color,
            )
            cls._line(
                vertices,
                (value, half * scale, -0.5),
                (value, -half * scale, -0.5),
                color,
            )

            # Floor at y = -0.5.
            cls._line(
                vertices,
                (-half * scale, -0.5, value),
                (half * scale, -0.5, value),
                color,
            )
            cls._line(
                vertices,
                (value, -0.5, half * scale),
                (value, -0.5, -half * scale),
                color,
            )

        return vertices

    @classmethod
    def _make_ball(cls):
        vertices = []
        meridians = 16
        parallels = 8

        def point(latitude, longitude):
            return (
                math.cos(latitude) * math.cos(longitude) / 2,
                math.sin(latitude) / 2,
                math.cos(latitude) * math.sin(longitude) / 2,
            )

        for row in range(parallels):
            lat0 = math.pi / 2 + row * math.pi / parallels
            lat1 = math.pi / 2 + (row + 1) * math.pi / parallels

            for column in range(meridians):
                lon0 = column * math.tau / meridians
                lon1 = (column + 1) * math.tau / meridians

                # Source uses white when the two tile coordinates differ.
                color = (
                    cls.BALL_WHITE
                    if ((column & 1) ^ (row & 1))
                    else cls.BALL_RED
                )

                a = point(lat0, lon0)
                b = point(lat1, lon0)
                c = point(lat1, lon1)
                d = point(lat0, lon1)
                cls._triangle(vertices, a, b, c, color)
                cls._triangle(vertices, a, c, d, color)

        return vertices

    @classmethod
    def _make_shadow(cls):
        vertices = []
        color = cls.SHADOW_COLOR
        center = (0.0, 0.0, 0.0)
        segments = 48

        for index in range(segments):
            a0 = math.tau * index / segments
            a1 = math.tau * (index + 1) / segments
            p0 = (0.5 * math.cos(a0), 0.5 * math.sin(a0), 0.0)
            p1 = (0.5 * math.cos(a1), 0.5 * math.sin(a1), 0.0)
            cls._triangle(vertices, center, p0, p1, color)

        return vertices

    @staticmethod
    def _make_scanlines(height):
        vertices = []
        if height <= 300:
            return vertices

        line_height = 4 if height > 500 else 2
        gap = line_height
        color = (0.0, 0.0, 0.0)

        for pixel_y in range(0, height, line_height + gap):
            y = 1.0 - 2.0 * pixel_y / height
            vertices.extend((-1.0, y, 0.0, *color, 1.0, y, 0.0, *color))

        return vertices

    def _ensure_scanlines(self, height):
        if height == self.scanline_height:
            return

        if self.scanline_mesh is not None:
            vao, vbo, _count = self.scanline_mesh
            GL.glDeleteBuffers(1, [vbo])
            GL.glDeleteVertexArrays(1, [vao])

        self.scanline_mesh = self._upload(self._make_scanlines(height))
        self.scanline_height = height

    @staticmethod
    def _camera(width, height):
        # Matches Boing's reshape code: 8-degree FOV and camera at z=8.
        h = (height / max(width, 1)) * (4.0 / 3.0)
        aspect = 1.0 / h
        projection = perspective(math.radians(8.0), aspect, 1.0, 10.0)

        if height > width:
            projection = scaling(width / height) @ projection

        view = look_at(
            (0.0, 0.0, 8.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        return projection, view

    def _update_physics(self):
        now = time.monotonic()
        frames = min((now - self.last_time) / (1.0 / 30.0), 3.0)
        self.last_time = now

        self.ball_spin += self.spin_speed * frames
        self.velocity += self.acceleration * frames
        self.position += self.velocity * frames

        limit = 0.5 - self.BALL_SIZE / 2

        if self.position[0] < -limit or self.position[0] > limit:
            self.position[0] = max(-limit, min(limit, self.position[0]))
            self.velocity[0] = -self.velocity[0]
            self.spin_speed = -self.spin_speed
            self.velocity[0] += random.uniform(-self.SPEED, -self.SPEED / 2)

        for axis in (1, 2):
            if self.position[axis] < -limit or self.position[axis] > limit:
                self.position[axis] = max(
                    -limit, min(limit, self.position[axis])
                )
                self.velocity[axis] = -self.velocity[axis]

    def _draw(self, mesh, mode, mvp, opacity):
        vao, _vbo, count = mesh
        if count == 0:
            return

        GL.glUseProgram(self.program)
        GL.glUniformMatrix4fv(
            self.mvp_location,
            1,
            GL.GL_FALSE,
            np.ascontiguousarray(mvp.T, dtype=np.float32),
        )
        GL.glUniform1f(self.opacity_location, opacity)
        GL.glBindVertexArray(vao)
        GL.glDrawArrays(mode, 0, count)

    def render(self, area, transition_scale=1.0):
        area.make_current()
        if area.get_error() is not None:
            return False

        width = max(1, area.get_allocated_width())
        height = max(1, area.get_allocated_height())
        self._ensure_scanlines(height)
        self._update_physics()

        GL.glViewport(0, 0, width, height)
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glDisable(GL.GL_DEPTH_TEST)

        # Keep geometry at its normal size; fade it instead of shrinking it.
        opacity = max(0.0, min(1.0, transition_scale))
        identity = np.identity(4, dtype=np.float32)

        self._draw(self.background, GL.GL_TRIANGLES, identity, opacity)

        projection, view = self._camera(width, height)
        scene = projection @ view

        GL.glLineWidth(max(1.0, height * 0.06 * self.THICKNESS))
        self._draw(self.grid, GL.GL_LINES, scene, opacity)

        shadow_model = (
            translation(
                self.position[0] + 0.14,
                self.position[1] + 0.07,
                -0.49,
            )
            @ rotate_z(-15)
            @ scaling(self.BALL_SIZE)
        )
        self._draw(
            self.shadow,
            GL.GL_TRIANGLES,
            scene @ shadow_model,
            opacity,
        )

        ball_model = (
            translation(*self.position)
            @ scaling(self.BALL_SIZE)
            @ rotate_z(-15)
            @ rotate_y(self.ball_spin)
        )

        GL.glEnable(GL.GL_DEPTH_TEST)
        self._draw(
            self.ball,
            GL.GL_TRIANGLES,
            scene @ ball_model,
            opacity,
        )

        # Source scanlines: black at 30% opacity, over the completed scene.
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glLineWidth(1.0)
        if height > 500:
            GL.glLineWidth(4.0)
        elif height > 300:
            GL.glLineWidth(2.0)

        self._draw(
            self.scanline_mesh,
            GL.GL_LINES,
            identity,
            opacity * 0.3,
        )

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
        GL.glDisable(GL.GL_BLEND)
        return True

    def dispose(self):
        for mesh in (
            self.background,
            self.grid,
            self.ball,
            self.shadow,
            self.scanline_mesh,
        ):
            if mesh is not None:
                vao, vbo, _count = mesh
                GL.glDeleteBuffers(1, [vbo])
                GL.glDeleteVertexArrays(1, [vao])

        GL.glDeleteProgram(self.program)
