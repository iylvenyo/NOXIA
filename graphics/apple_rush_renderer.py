import ctypes
import math

import numpy as np
from OpenGL import GL


VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
uniform mat4 u_mvp;
out vec3 v_color;

void main() {
    gl_Position = u_mvp * vec4(position, 1.0);
    v_color = color;
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 v_color;
out vec4 frag_color;

void main() {
    frag_color = vec4(v_color, 1.0);
}
"""


def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(fov / 2.0)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0],
    ], dtype=np.float32)


def look_at(eye, target, up):
    eye, target, up = [
        np.asarray(value, dtype=np.float32) for value in (eye, target, up)
    ]
    forward = target - eye
    forward /= np.linalg.norm(forward)
    side = np.cross(forward, up)
    side /= np.linalg.norm(side)
    true_up = np.cross(side, forward)

    matrix = np.identity(4, dtype=np.float32)
    matrix[0, :3] = side
    matrix[1, :3] = true_up
    matrix[2, :3] = -forward
    matrix[:3, 3] = [
        -np.dot(side, eye), -np.dot(true_up, eye), np.dot(forward, eye)
    ]
    return matrix


class AppleRushRenderer:
    def __init__(self):
        self.width, self.height = 900, 650
        self.program = self._make_program()
        self.mvp_location = GL.glGetUniformLocation(self.program, "u_mvp")
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.vertices = self._make_apple_mesh()

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER, self.vertices.nbytes,
            self.vertices, GL.GL_STATIC_DRAW,
        )
        for location, offset in ((0, 0), (1, 12)):
            GL.glVertexAttribPointer(
                location, 3, GL.GL_FLOAT, GL.GL_FALSE, 24,
                ctypes.c_void_p(offset),
            )
            GL.glEnableVertexAttribArray(location)
        GL.glBindVertexArray(0)

    @staticmethod
    def _compile_shader(shader_type, source):
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            message = GL.glGetShaderInfoLog(shader).decode("utf-8", "replace")
            GL.glDeleteShader(shader)
            raise RuntimeError(f"Shader compilation failed:\n{message}")
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
            raise RuntimeError(f"Shader link failed:\n{message}")
        return program

    def resize(self, width, height):
        self.width, self.height = max(1, width), max(1, height)
        GL.glViewport(0, 0, self.width, self.height)

    @staticmethod
    def _make_apple_mesh():
        rings = [
            (-0.76, 0.06), (-0.66, 0.30), (-0.43, 0.52), (-0.12, 0.66),
            (0.16, 0.68), (0.37, 0.52), (0.48, 0.30), (0.39, 0.08),
        ]
        palette = [
            (0.53, 0.15, 0.17), (0.57, 0.17, 0.18), (0.50, 0.13, 0.16),
            (0.55, 0.16, 0.18), (0.48, 0.12, 0.15), (0.58, 0.18, 0.19),
        ]
        sides = 8
        vertices = []

        def point(ring, side):
            z, radius = rings[ring]
            angle = 2.0 * math.pi * side / sides
            lobe = 1.0 + 0.12 * math.cos(5.0 * angle)
            return (
                radius * lobe * math.cos(angle),
                radius * lobe * math.sin(angle),
                z,
            )

        def triangle(a, b, c, color):
            vertices.extend((*a, *color, *b, *color, *c, *color))

        for side in range(sides):
            triangle(
                (0.0, 0.0, -0.76), point(0, (side + 1) % sides),
                point(0, side), palette[side % len(palette)],
            )

        for ring in range(len(rings) - 1):
            for side in range(sides):
                next_side = (side + 1) % sides
                a, b = point(ring, side), point(ring, next_side)
                c, d = point(ring + 1, next_side), point(ring + 1, side)
                color = palette[(ring * 3 + side) % len(palette)]
                triangle(a, b, c, color)
                triangle(a, c, d, color)

        last = len(rings) - 1
        for side in range(sides):
            triangle(
                (0.0, 0.0, 0.39), point(last, side),
                point(last, (side + 1) % sides),
                palette[(side + 2) % len(palette)],
            )

        # Stem and leaf triangles.
        details = [
            ((-0.075, -0.035, 0.40), (0.075, -0.035, 0.40),
             (0.025, 0.015, 0.70), (0.34, 0.20, 0.08)),
            ((-0.075, -0.035, 0.40), (0.025, 0.015, 0.70),
             (-0.025, 0.045, 0.70), (0.34, 0.20, 0.08)),
            ((0.0, 0.0, 0.59), (0.43, 0.04, 0.70),
             (0.14, 0.08, 0.76), (0.25, 0.43, 0.18)),
            ((0.0, 0.0, 0.59), (0.14, 0.08, 0.76),
             (0.10, -0.07, 0.70), (0.34, 0.52, 0.22)),
        ]
        for detail in details:
            triangle(*detail)

        return np.asarray(vertices, dtype=np.float32)

    @staticmethod
    def _model_matrix(apple, elapsed):
        angle = elapsed * apple["speed"] + apple["phase"]
        c, s = math.cos(angle), math.sin(angle)
        rotation = np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)

        bounce = apple["bounce"] * abs(
            math.sin(elapsed * apple["bounce_speed"] + apple["phase"])
        )
        scale = apple["scale"]
        translation = np.identity(4, dtype=np.float32)
        translation[:3, 3] = [
            apple["x"], apple["floor_y"] + 0.76 * scale + bounce, 0.0
        ]
        scaling = np.diag([scale, scale, scale, 1.0]).astype(np.float32)
        return translation @ rotation @ scaling

    def _camera_matrices(self):
        projection = perspective(
            math.radians(45), self.width / self.height, 0.1, 100.0
        )
        view = look_at((0.0, 2.0, 4.5), (0.0, 0.1, 0.0), (0.0, 1.0, 0.0))
        return projection, view

    def project(self, apple, elapsed=0.0):
        projection, view = self._camera_matrices()
        model = self._model_matrix(apple, elapsed)
        clip = projection @ view @ model @ np.array([0, 0, 0, 1], dtype=np.float32)
        ndc = clip[:3] / clip[3]
        x = (ndc[0] + 1.0) * 0.5 * self.width
        y = (1.0 - ndc[1]) * 0.5 * self.height
        radius = self.height * 0.105 * apple["scale"]
        return x, y, radius

    def render(self, apples, elapsed):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.008, 0.008, 0.014, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        projection, view = self._camera_matrices()
        GL.glUseProgram(self.program)
        GL.glBindVertexArray(self.vao)

        for apple in apples:
            model = self._model_matrix(apple, elapsed)
            mvp = projection @ view @ model
            GL.glUniformMatrix4fv(self.mvp_location, 1, GL.GL_TRUE, mvp)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.vertices) // 6)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def dispose(self):
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteVertexArrays(1, [self.vao])
        GL.glDeleteProgram(self.program)