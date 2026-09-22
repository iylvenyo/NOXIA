class Point:
    __slots__ = ("x", "y", "z", "sx", "sy", "sz")

    def __init__(self, x=0.0, y=0.0, z=0.0, sx=0, sy=0, sz=0):
        self.x = x
        self.y = y
        self.z = z
        self.sx = sx
        self.sy = sy
        self.sz = sz

class Arm:
    __slots__ = ("color", "pixel", "numpt", "growth", "rate")

    def __init__(self, color, pixel, numpt, growth, rate):
        self.color = color
        self.pixel = pixel
        self.numpt = numpt
        self.growth = growth
        self.rate = rate

class DrawCommand:
    __slots__ = ("x1", "y1", "x2", "y2", "width", "color", "is_tip")

    def __init__(self, x1, y1, x2, y2, width, color, is_tip=False):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.color = color
        self.is_tip = is_tip
