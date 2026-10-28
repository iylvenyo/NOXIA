import time
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gdk, Gtk

from graphics.config import DEFAULT_HEIGHT, DEFAULT_WIDTH, DELAY_US
from graphics.gl_renderer import NoxiaGLRenderer
from graphics.romanboy_renderer import RomanBoyRenderer
from graphics.simulation import NoxiaSimulation


TRANSITION_SECONDS = 1.0
GRAPHIC_COUNT = 3


def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)


class NoxiaGraphicsWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(
            application=app,
            title="NOXIA",
        )

        self.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        self.simulation = NoxiaSimulation()
        self.renderer = None
        self.romanboy_renderer = None

        self.visual_index = 0

        self.transition_started = None
        self.transition_target = None

        self.mouse_x = DEFAULT_WIDTH / 2
        self.mouse_y = DEFAULT_HEIGHT / 2

        self.area = Gtk.GLArea()
        self.area.set_required_version(3, 3)
        self.area.set_hexpand(True)
        self.area.set_vexpand(True)
        self.area.connect("realize", self.on_realize)
        self.area.connect("unrealize", self.on_unrealize)
        self.area.connect("render", self.on_render)

        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self.on_mouse_motion)
        self.area.add_controller(motion)

        self.set_child(self.area)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.key_pressed)
        self.add_controller(key_controller)

        GLib.timeout_add(DELAY_US // 1000, self.tick)

    def on_realize(self, area):
        area.make_current()

        error = area.get_error()
        if error is not None:
            print(f"Could not create OpenGL context: {error}")
            return

        try:
            self.renderer = NoxiaGLRenderer()
        except Exception as error:
            print(f"Could not initialize NOXIA OpenGL renderer: {error}")
            self.renderer = None

        try:
            self.romanboy_renderer = RomanBoyRenderer()
        except Exception as error:
            print(f"Could not initialize RomanBoy renderer: {error}")
            self.romanboy_renderer = None

    def on_unrealize(self, area):
        area.make_current()

        error = area.get_error()
        if error is not None:
            self.renderer = None
            self.romanboy_renderer = None
            return

        if self.renderer is not None:
            self.renderer.dispose()
            self.renderer = None

        if self.romanboy_renderer is not None:
            dispose = getattr(self.romanboy_renderer, "dispose", None)
            if dispose is not None:
                dispose()
            self.romanboy_renderer = None

    def on_render(self, area, context):
        if self.renderer is None:
            return True

        visual_mode = self.visual_index
        transition_scale = 1.0

        if self.transition_started is not None:
            elapsed = time.perf_counter() - self.transition_started
            progress = min(1.0, elapsed / TRANSITION_SECONDS)

            if progress < 0.5:
                phase = smoothstep(progress * 2.0)
                transition_scale = 1.0 - phase
            else:
                visual_mode = self.transition_target
                phase = smoothstep((progress - 0.5) * 2.0)
                transition_scale = phase

            if progress >= 1.0:
                self.visual_index = self.transition_target
                self.transition_target = None
                self.transition_started = None
                visual_mode = self.visual_index
                transition_scale = 1.0

        if visual_mode == 2 and self.romanboy_renderer is not None:
            self.romanboy_renderer.render(
                area,
                transition_scale=transition_scale,
            )

            self.renderer.draw(
                area=area,
                commands=self.simulation.commands,
                frame=self.simulation.frame,
                show_background=False,
                mouse_x=self.mouse_x,
                mouse_y=self.mouse_y,
                transition_scale=transition_scale,
                clear=False,
                overlay=True,
                line_color=(1.0, 0.0, 0.0, 1.0),
            )
        else:
            self.renderer.draw(
                area=area,
                commands=self.simulation.commands,
                frame=self.simulation.frame,
                show_background=(visual_mode == 1),
                mouse_x=self.mouse_x,
                mouse_y=self.mouse_y,
                transition_scale=transition_scale,
            )

        return True

    def on_mouse_motion(self, controller, x, y):
        self.mouse_x = x
        self.mouse_y = self.area.get_allocated_height() - y

    def tick(self):
        self.simulation.step()
        self.area.queue_render()
        return True

    def cycle_graphic(self):
        self.start_background_transition()

    def start_background_transition(self):
        if self.transition_started is not None:
            return

        self.transition_target = (self.visual_index + 1) % GRAPHIC_COUNT
        self.transition_started = time.perf_counter()
        self.area.queue_render()

    def key_pressed(self, controller, keyval, keycode, modifiers):
        if keyval in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q):
            self.close()
            return True

        return False
