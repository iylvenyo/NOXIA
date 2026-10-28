from array import array
from pathlib import Path
import ctypes
import time

from OpenGL import GL


SHADER_DIR = Path(__file__).resolve().parent / "shaders"


FULLSCREEN_VERTEX_SHADER = """#version 330 core
void main()
{
    vec2 positions[3] = vec2[](
        vec2(-1.0, -1.0),
        vec2( 3.0, -1.0),
        vec2(-1.0,  3.0)
    );

    gl_Position = vec4(positions[gl_VertexID], 0.0, 1.0);
}
"""


LINES_VERTEX_SHADER = """#version 330 core
layout(location = 0) in vec2 a_position;
layout(location = 1) in vec4 a_color;

uniform vec2 uCanvasSize;
out vec4 v_color;

void main()
{
    float x = (a_position.x / uCanvasSize.x) * 2.0 - 1.0;
    float y = 1.0 - (a_position.y / uCanvasSize.y) * 2.0;

    gl_Position = vec4(x, y, 0.0, 1.0);
    v_color = a_color;
}
"""


LINES_FRAGMENT_SHADER = """#version 330 core
in vec4 v_color;
out vec4 fragColor;

void main()
{
    fragColor = v_color;
}
"""


def _format_gl_log(log):
    if isinstance(log, bytes):
        return log.decode(errors="replace")
    return str(log)


def compile_shader(shader_type, source):
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)

    if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
        log = _format_gl_log(GL.glGetShaderInfoLog(shader))
        GL.glDeleteShader(shader)
        raise RuntimeError(f"OpenGL shader compile failed:\n{log}")

    return shader


def create_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(GL.GL_VERTEX_SHADER, vertex_source)
    fragment_shader = compile_shader(GL.GL_FRAGMENT_SHADER, fragment_source)

    program = GL.glCreateProgram()
    GL.glAttachShader(program, vertex_shader)
    GL.glAttachShader(program, fragment_shader)
    GL.glLinkProgram(program)

    GL.glDeleteShader(vertex_shader)
    GL.glDeleteShader(fragment_shader)

    if not GL.glGetProgramiv(program, GL.GL_LINK_STATUS):
        log = _format_gl_log(GL.glGetProgramInfoLog(program))
        GL.glDeleteProgram(program)
        raise RuntimeError(f"OpenGL program link failed:\n{log}")

    return program


def add_quad(vertices, x1, y1, x2, y2, width, color):
    """Add a thick line segment as two triangles."""
    dx = x2 - x1
    dy = y2 - y1
    length = (dx * dx + dy * dy) ** 0.5

    if length < 0.001:
        return

    half_width = width / 2.0
    px = -dy / length * half_width
    py = dx / length * half_width

    points = (
        (x1 + px, y1 + py),
        (x1 - px, y1 - py),
        (x2 + px, y2 + py),
        (x2 + px, y2 + py),
        (x1 - px, y1 - py),
        (x2 - px, y2 - py),
    )

    red, green, blue, alpha = color

    for x, y in points:
        vertices.extend((x, y, red, green, blue, alpha))


class NoxiaGLRenderer:
    def __init__(self):
        fragment_source = (
            SHADER_DIR / "topologica.frag"
        ).read_text(encoding="utf-8")

        self.background_program = create_program(
            FULLSCREEN_VERTEX_SHADER,
            fragment_source,
        )
        self.lines_program = create_program(
            LINES_VERTEX_SHADER,
            LINES_FRAGMENT_SHADER,
        )

        self.background_vao = GL.glGenVertexArrays(1)
        self.lines_vao = GL.glGenVertexArrays(1)
        self.lines_vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.lines_vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.lines_vbo)

        stride = 6 * 4

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(
            0,
            2,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            stride,
            ctypes.c_void_p(0),
        )

        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(
            1,
            4,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            stride,
            ctypes.c_void_p(8),
        )

        GL.glBindVertexArray(0)

        self.resolution_location = GL.glGetUniformLocation(
            self.background_program,
            "iResolution",
        )
        self.time_location = GL.glGetUniformLocation(
            self.background_program,
            "iTime",
        )
        self.mouse_location = GL.glGetUniformLocation(
            self.background_program,
            "iMouse",
        )
        self.frame_location = GL.glGetUniformLocation(
            self.background_program,
            "iFrame",
        )
        self.enabled_location = GL.glGetUniformLocation(
            self.background_program,
            "uShowBackground",
        )
        self.canvas_location = GL.glGetUniformLocation(
            self.lines_program,
            "uCanvasSize",
        )

        self.start_time = time.perf_counter()

    def draw(
        self,
        area,
        commands,
        frame,
        show_background,
        mouse_x,
        mouse_y,
        transition_scale=1.0,
        clear=True,
        overlay=False,
        line_color=None,
    ):
        width = max(1, area.get_allocated_width())
        height = max(1, area.get_allocated_height())
        scale_factor = area.get_scale_factor()

        framebuffer_width = width * scale_factor
        framebuffer_height = height * scale_factor

        GL.glViewport(
            0,
            0,
            framebuffer_width,
            framebuffer_height,
        )

        if clear:
            GL.glClearColor(0.0, 0.0, 0.0, 1.0)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if overlay:
            GL.glDisable(GL.GL_DEPTH_TEST)

        if show_background:
            GL.glUseProgram(self.background_program)

            GL.glUniform3f(
                self.resolution_location,
                framebuffer_width,
                framebuffer_height,
                1.0,
            )
            GL.glUniform1f(
                self.time_location,
                time.perf_counter() - self.start_time,
            )
            GL.glUniform4f(
                self.mouse_location,
                mouse_x * scale_factor,
                mouse_y * scale_factor,
                0.0,
                0.0,
            )
            GL.glUniform1i(self.frame_location, int(frame))
            GL.glUniform1i(self.enabled_location, 1)

            GL.glBindVertexArray(self.background_vao)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

        vertices = array("f")
        center_x = width / 2.0
        center_y = height / 2.0

        for command in commands:
            if transition_scale <= 0.001:
                continue

            x1 = center_x + (command.x1 - center_x) * transition_scale
            y1 = center_y + (command.y1 - center_y) * transition_scale
            x2 = center_x + (command.x2 - center_x) * transition_scale
            y2 = center_y + (command.y2 - center_y) * transition_scale

            if line_color is not None:
                add_quad(
                    vertices,
                    x1,
                    y1,
                    x2,
                    y2,
                    max(0.1, command.width * 9.0 * transition_scale),
                    (1.0, 0.0, 0.0, 0.14),
                )

                add_quad(
                    vertices,
                    x1,
                    y1,
                    x2,
                    y2,
                    max(0.1, command.width * 4.5 * transition_scale),
                    (1.0, 0.02, 0.01, 0.40),
                )

                core_color = line_color
                core_width = max(
                    0.1,
                    command.width * 2.2 * transition_scale,
                )

            elif show_background:
                add_quad(
                    vertices,
                    x1,
                    y1,
                    x2,
                    y2,
                    max(0.1, command.width * 9.0 * transition_scale),
                    (0.02, 0.45, 1.0, 0.12),
                )
                add_quad(
                    vertices,
                    x1,
                    y1,
                    x2,
                    y2,
                    max(0.1, command.width * 4.5 * transition_scale),
                    (0.05, 0.75, 1.0, 0.32),
                )

                core_color = (1.0, 1.0, 1.0, 1.0)
                core_width = max(
                    0.1,
                    command.width * 2.5 * transition_scale,
                )

            else:
                core_color = command.color
                core_width = max(
                    0.1,
                    command.width * transition_scale,
                )

            add_quad(
                vertices,
                x1,
                y1,
                x2,
                y2,
                core_width,
                core_color,
            )

        if vertices:
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendFunc(
                GL.GL_SRC_ALPHA,
                GL.GL_ONE_MINUS_SRC_ALPHA,
            )

            GL.glUseProgram(self.lines_program)
            GL.glUniform2f(
                self.canvas_location,
                width,
                height,
            )

            GL.glBindVertexArray(self.lines_vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.lines_vbo)
            GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(vertices) * vertices.itemsize,
                vertices.tobytes(),
                GL.GL_DYNAMIC_DRAW,
            )
            GL.glDrawArrays(
                GL.GL_TRIANGLES,
                0,
                len(vertices) // 6,
            )

            GL.glBindVertexArray(0)
            GL.glDisable(GL.GL_BLEND)

        if overlay:
            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glUseProgram(0)

    def dispose(self):
        GL.glDeleteBuffers(1, [self.lines_vbo])
        GL.glDeleteVertexArrays(1, [self.lines_vao])
        GL.glDeleteVertexArrays(1, [self.background_vao])
        GL.glDeleteProgram(self.lines_program)
        GL.glDeleteProgram(self.background_program)
