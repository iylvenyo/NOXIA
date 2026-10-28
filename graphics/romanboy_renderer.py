# Adapted from RomanBoy by Carsten Steger.

import math
import time

import numpy as np
from OpenGL import GL


VERTEX_SHADER = """
#version 330 core

layout(location = 0) in vec3 aPosition;

uniform mat4 uMVP;
uniform float uScale;

void main() {
    gl_Position = uMVP * vec4(aPosition, 1.0);
    gl_Position.xy *= uScale;
}
"""

FRAGMENT_SHADER = """
#version 330 core

out vec4 fragColor;

void main() {
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""


class RomanBoyRenderer:
    SURFACE_ORDER = 3

    DEFORMATION_SPEED = 1.0
    INITIAL_DEFORMATION = 0.0

    WALK_DIRECTION_DEGREES = 83.0
    WALK_SPEED = 20.0
    FRAME_RATE = 25.0

    GRID_U = SURFACE_ORDER * 64
    GRID_V = 128

    def __init__(self):
        self.initialized = False
        self.start_time = None

    @staticmethod
    def _compile_shader(shader_type, source):
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            message = GL.glGetShaderInfoLog(shader).decode(
                "utf-8", "replace"
            )
            GL.glDeleteShader(shader)
            raise RuntimeError(
                f"RomanBoy shader compilation failed:\n{message}"
            )

        return shader

    def _initialize(self):
        vertex_shader = self._compile_shader(
            GL.GL_VERTEX_SHADER,
            VERTEX_SHADER,
        )
        fragment_shader = self._compile_shader(
            GL.GL_FRAGMENT_SHADER,
            FRAGMENT_SHADER,
        )

        self.program = GL.glCreateProgram()
        GL.glAttachShader(self.program, vertex_shader)
        GL.glAttachShader(self.program, fragment_shader)
        GL.glLinkProgram(self.program)

        GL.glDeleteShader(vertex_shader)
        GL.glDeleteShader(fragment_shader)

        if not GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS):
            message = GL.glGetProgramInfoLog(self.program).decode(
                "utf-8", "replace"
            )
            raise RuntimeError(f"RomanBoy shader link failed:\n{message}")

        self.mvp_location = GL.glGetUniformLocation(self.program, "uMVP")
        self.scale_location = GL.glGetUniformLocation(self.program, "uScale")

        self.vao = GL.glGenVertexArrays(1)
        self.vertex_buffer = GL.glGenBuffers(1)
        self.index_buffer = GL.glGenBuffers(1)
        self.indices = self._make_indices()

        point_count = (self.GRID_U + 1) * (self.GRID_V + 1)

        GL.glBindVertexArray(self.vao)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            point_count * 3 * np.dtype(np.float32).itemsize,
            None,
            GL.GL_DYNAMIC_DRAW,
        )
        GL.glVertexAttribPointer(
            0,
            3,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            0,
            None,
        )
        GL.glEnableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        GL.glBufferData(
            GL.GL_ELEMENT_ARRAY_BUFFER,
            self.indices.nbytes,
            self.indices,
            GL.GL_STATIC_DRAW,
        )

        GL.glBindVertexArray(0)
        self.initialized = True

    def _make_indices(self):
        indices = []

        for row in range(self.GRID_V + 1):
            for column in range(self.GRID_U):
                first = row * (self.GRID_U + 1) + column
                indices.extend((first, first + 1))

        for row in range(self.GRID_V):
            for column in range(self.GRID_U + 1):
                first = row * (self.GRID_U + 1) + column
                indices.extend((first, first + self.GRID_U + 1))

        return np.asarray(indices, dtype=np.uint32)

    def _deformation(self, elapsed):
        phase = (
            self.INITIAL_DEFORMATION
            + elapsed
            * self.DEFORMATION_SPEED
            * 0.001
            * self.FRAME_RATE
        ) % 2.0

        if phase <= 1.0:
            value = phase
        else:
            value = 2.0 - phase

        return ((6.0 * value - 15.0) * value + 10.0) * value**3

    def _surface_point(self, u, walk_v, deformation):
        g = self.SURFACE_ORDER
        v = math.pi / 2.0 - 0.25 * walk_v

        sqrt_two_over_g = math.sqrt(2.0) / g
        half_one_minus_one_over_g = 0.5 * (1.0 - 1.0 / g)
        gm1 = g - 1.0

        cu = math.cos(u)
        su = math.sin(u)
        sgu = math.sin(g * u)
        cgm1u = math.cos(gm1 * u)
        sgm1u = math.sin(gm1 * u)

        cv = math.cos(v)
        cos_v_squared = cv * cv
        sin_two_v = math.sin(2.0 * v)

        numerator_x = (
            sqrt_two_over_g * cos_v_squared * cgm1u
            + half_one_minus_one_over_g * sin_two_v * cu
        )
        numerator_y = (
            sqrt_two_over_g * cos_v_squared * sgm1u
            - half_one_minus_one_over_g * sin_two_v * su
        )

        denominator = 1.0 / (
            1.0
            - 0.5
            * math.sqrt(2.0)
            * deformation
            * sin_two_v
            * sgu
        )

        radius_factor = 1.0 + deformation**2 * (
            0.5 + deformation**2 * (1.0 / 6.0 + deformation**2 / 3.0)
        )
        radius = 1.0 / radius_factor
        vertical_offset = 0.5 * radius_factor

        return np.asarray(
            (
                numerator_x * denominator * radius,
                numerator_y * denominator * radius,
                (cos_v_squared * denominator - vertical_offset) * radius,
            ),
            dtype=np.float32,
        )

    def _walk_state(self, elapsed):
        direction = math.radians(self.WALK_DIRECTION_DEGREES)
        speed_per_second = (
            self.FRAME_RATE * self.WALK_SPEED * math.pi / 4096.0
        )

        v_speed = speed_per_second * math.sin(direction)
        u_speed = speed_per_second * math.cos(direction)

        unbounded_v = 2.0 + elapsed * v_speed
        segment = math.floor(unbounded_v / (2.0 * math.pi))
        remainder = unbounded_v % (2.0 * math.pi)

        if segment % 2 == 0:
            walk_v = remainder
            reflected_v_speed = v_speed
        else:
            walk_v = 2.0 * math.pi - remainder
            reflected_v_speed = -v_speed

        u = (
            0.5
            + elapsed * u_speed
            - segment * math.pi
        ) % (2.0 * math.pi)

        side = -1.0 if ((segment + 1) // 2) % 2 else 1.0

        return u, walk_v, u_speed, reflected_v_speed, segment, side

    def _walk_position(self, elapsed):
        u, walk_v, _u_speed, _v_speed, _segment, _side = (
            self._walk_state(elapsed)
        )
        return u, walk_v

    def _vertices(self, deformation):
        u_values = np.linspace(
            0.0,
            2.0 * math.pi,
            self.GRID_U + 1,
            dtype=np.float64,
        )[None, :]

        walk_v_values = np.linspace(
            0.0,
            2.0 * math.pi,
            self.GRID_V + 1,
            dtype=np.float64,
        )[:, None]

        g = self.SURFACE_ORDER
        v = math.pi / 2.0 - 0.25 * walk_v_values

        sqrt_two_over_g = math.sqrt(2.0) / g
        half_one_minus_one_over_g = 0.5 * (1.0 - 1.0 / g)
        gm1 = g - 1.0

        cu = np.cos(u_values)
        su = np.sin(u_values)
        sgu = np.sin(g * u_values)
        cgm1u = np.cos(gm1 * u_values)
        sgm1u = np.sin(gm1 * u_values)

        cv = np.cos(v)
        cos_v_squared = cv * cv
        sin_two_v = np.sin(2.0 * v)

        numerator_x = (
            sqrt_two_over_g * cos_v_squared * cgm1u
            + half_one_minus_one_over_g * sin_two_v * cu
        )
        numerator_y = (
            sqrt_two_over_g * cos_v_squared * sgm1u
            - half_one_minus_one_over_g * sin_two_v * su
        )

        denominator = 1.0 / (
            1.0
            - 0.5
            * math.sqrt(2.0)
            * deformation
            * sin_two_v
            * sgu
        )

        radius_factor = 1.0 + deformation**2 * (
            0.5 + deformation**2 * (1.0 / 6.0 + deformation**2 / 3.0)
        )
        radius = 1.0 / radius_factor
        vertical_offset = 0.5 * radius_factor

        x = numerator_x * denominator * radius
        y = numerator_y * denominator * radius
        z = (cos_v_squared * denominator - vertical_offset) * radius

        return np.ascontiguousarray(
            np.stack((x, y, z), axis=-1).reshape(-1, 3),
            dtype=np.float32,
        )

    @staticmethod
    def _normalize(vector):
        length = np.linalg.norm(vector)
        if length < 1e-7:
            return None
        return vector / length

    def _mvp(self, elapsed, deformation, width, height):
        u, walk_v, u_speed, v_speed, _segment, side_sign = (
            self._walk_state(elapsed)
        )
        position = self._surface_point(u, walk_v, deformation)

        epsilon = 0.001
        du = (
            self._surface_point(u + epsilon, walk_v, deformation) - position
        ) / epsilon
        dv = (
            self._surface_point(u, walk_v + epsilon, deformation) - position
        ) / epsilon

        normal = self._normalize(np.cross(du, -4.0 * dv))

        if normal is None:
            normal = np.asarray((0.0, 1.0, 0.0), dtype=np.float32)
        else:
            normal = normal * side_sign

        forward = self._normalize(du * u_speed + dv * v_speed)

        if forward is None:
            forward = self._normalize(du)

        if forward is None:
            forward = np.asarray((0.0, 0.0, -1.0), dtype=np.float32)
        
        camera = position + normal * 0.12
        target = position + forward * 0.10

        forward = self._normalize(target - camera)
        side = self._normalize(np.cross(forward, normal))

        if side is None:
            side = np.asarray((1.0, 0.0, 0.0), dtype=np.float32)

        up = self._normalize(np.cross(side, forward))

        if up is None:
            up = normal

        view = np.identity(4, dtype=np.float32)
        view[0, :3] = side
        view[1, :3] = up
        view[2, :3] = -forward
        view[0, 3] = -np.dot(side, camera)
        view[1, 3] = -np.dot(up, camera)
        view[2, 3] = np.dot(forward, camera)

        aspect = max(width, 1) / max(height, 1)
        near = 0.01
        far = 20.0
        f = 1.0 / math.tan(math.radians(65.0) / 2.0)

        projection = np.zeros((4, 4), dtype=np.float32)
        projection[0, 0] = f / aspect
        projection[1, 1] = f
        projection[2, 2] = (far + near) / (near - far)
        projection[2, 3] = (2.0 * far * near) / (near - far)
        projection[3, 2] = -1.0

        return projection @ view

    def render(self, area, transition_scale=1.0):
        area.make_current()

        if area.get_error() is not None:
            return False

        if not self.initialized:
            self._initialize()

        if self.start_time is None:
            self.start_time = time.monotonic()

        elapsed = time.monotonic() - self.start_time
        deformation = self._deformation(elapsed)

        width = max(area.get_allocated_width(), 1)
        height = max(area.get_allocated_height(), 1)

        GL.glViewport(0, 0, width, height)

        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_SCISSOR_TEST)
        GL.glColorMask(
            GL.GL_TRUE,
            GL.GL_TRUE,
            GL.GL_TRUE,
            GL.GL_TRUE,
        )
        GL.glDepthMask(GL.GL_TRUE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)

        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClearDepth(1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLineWidth(1.5)

        vertices = self._vertices(deformation)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferSubData(
            GL.GL_ARRAY_BUFFER,
            0,
            vertices.nbytes,
            vertices,
        )

        mvp = self._mvp(elapsed, deformation, width, height)

        GL.glUseProgram(self.program)
        GL.glUniformMatrix4fv(
            self.mvp_location,
            1,
            GL.GL_FALSE,
            np.ascontiguousarray(mvp.T, dtype=np.float32),
        )
        GL.glUniform1f(self.scale_location, transition_scale)

        GL.glBindVertexArray(self.vao)
        GL.glDrawElements(
            GL.GL_LINES,
            self.indices.size,
            GL.GL_UNSIGNED_INT,
            None,
        )

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
        GL.glDisable(GL.GL_DEPTH_TEST)

        return True
