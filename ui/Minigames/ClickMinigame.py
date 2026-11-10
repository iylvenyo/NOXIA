import gi
import random
import time
import math

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from graphics.apple_rush_renderer import AppleRushRenderer


ROUND_SECONDS = 45
APPLE_COUNT = 7


class ClickingMinigame(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title="Apple Rush")
        self.set_default_size(900, 650)

        self.score = 0
        self.max_button_amount = APPLE_COUNT
        self.started_at = None
        self.finished = False
        self.apples = []
        self.renderer = None

        self.area = Gtk.GLArea()
        self.area.set_required_version(3, 3)
        self.area.set_hexpand(True)
        self.area.set_vexpand(True)
        self.area.connect("realize", self.on_realize)
        self.area.connect("resize", self.on_resize)
        self.area.connect("render", self.on_render)

        click = Gtk.GestureClick()
        click.connect("pressed", self.on_click)
        self.area.add_controller(click)

        self.overlay = Gtk.Overlay()
        self.overlay.set_child(self.area)

        self.hud = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=28,
        )
        self.hud.set_halign(Gtk.Align.CENTER)
        self.hud.set_valign(Gtk.Align.START)
        self.hud.set_margin_top(18)

        self.score_label = Gtk.Label(label="APPLES  0")
        self.timer_label = Gtk.Label(label=f"TIME  {ROUND_SECONDS}")

        for label in (self.score_label, self.timer_label):
            label.add_css_class("title-2")
            label.set_markup(
                f'<span foreground="#c9b4a0">{label.get_text()}</span>'
            )
            self.hud.append(label)

        self.overlay.add_overlay(self.hud)
        self.set_child(self.overlay)

        GLib.timeout_add(33, self.tick)

    def start_game(self):
        self.score = 0
        self.started_at = None
        self.finished = False
        self.apples.clear()

        self.score_label.set_text("APPLES  0")
        self.timer_label.set_text(f"TIME  {ROUND_SECONDS}")

        for index in range(self.max_button_amount):
            button = self.generate_button()

            # Spread the initial targets evenly from -3.0 to 3.0.
            if self.max_button_amount > 1:
                button["x"] = (
                    -3.0
                    + 6.0 * index / (self.max_button_amount - 1)
                )
            else:
                button["x"] = 0.0

            self.apples.append(button)

        self.area.queue_render()

    def randomize_buttons(self, button):
        button.update({
            "x": random.uniform(-2.65, 2.65),
            "floor_y": -2.0,
            "phase": random.uniform(0, math.tau),
            "speed": random.uniform(-0.45, 0.45),
            "bounce": random.uniform(1.2, 2.75),
            "bounce_speed": random.uniform(1.5, 1.8),
            "scale": random.uniform(0.72, 0.88),
        })

    def generate_button(self):
        # I made the targets the renderer data instead of the old Gtk.Button widgets.
        button = {}
        self.randomize_buttons(button)
        return button

    def on_button_clicked(self, button):
        self.randomize_buttons(button)
        self.score += 1
        self.score_label.set_text(f"APPLES  {self.score}")

    # Some new extra methods here for the grpahics

    def on_realize(self, area):
        area.make_current()
        error = area.get_error()

        if error is not None:
            print(f"Could not create OpenGL context: {error}")
            return

        self.renderer = AppleRushRenderer()
        self.renderer.resize(
            area.get_allocated_width(),
            area.get_allocated_height(),
        )

    def on_resize(self, area, width, height):
        if self.renderer is not None:
            self.renderer.resize(width, height)

    def on_render(self, area, context):
        elapsed = (
            time.perf_counter() - self.started_at
            if self.started_at is not None
            else 0.0
        )

        if self.renderer is not None:
            self.renderer.render(self.apples, elapsed)

        return True

    def on_click(self, gesture, press_count, x, y):
        if self.finished:
            return

        if self.started_at is None:
            self.started_at = time.perf_counter()

        if self.renderer is None:
            return

        elapsed = time.perf_counter() - self.started_at

        for button in self.apples:
            apple_x, apple_y, radius = self.renderer.project(
                button, elapsed
            )

            if (x - apple_x) ** 2 + (y - apple_y) ** 2 <= radius ** 2:
                self.on_button_clicked(button)
                break

        self.area.queue_render()

    def tick(self):
        if self.started_at is not None and not self.finished:
            elapsed = time.perf_counter() - self.started_at
            remaining = max(0, math.ceil(ROUND_SECONDS - elapsed))
            self.timer_label.set_text(f"TIME  {remaining}")

            if remaining == 0:
                self.finished = True
                self.apples.clear()

        self.area.queue_render()
        return True


def on_activate(app):
    window = ClickingMinigame(application=app)
    window.start_game()
    window.present()


app = Gtk.Application(application_id="com.example.AppleRush")
app.connect("activate", on_activate)
app.run(None)