import math

# float comparison courtesy of stack overflow
# http://stackoverflow.com/questions/10334688/how-dangerous-is-it-to-compare-floating-point-values
FL_EPS = 0.0000001192092896
FL_MIN = 1.175494e-38
def near(f1, f2, k = 1):
    return (abs(f1 - f2) < k * FL_EPS * abs(f1 + f2) or abs(f1 - f2) < FL_MIN)

class Vector2():
    # 2D vector/point
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Vector2(self.x, self.y)

    def __abs__(self): # gives the value squared to avoid sqrt
        return (self.x * self.x + self.y * self.y)

    def __add__(self, v2):
        return Vector2(self.x + v2.x, self.y + v2.y)

    def __sub__(self, v2):
        return Vector2(self.x - v2.x, self.y - v2.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def update(self, v2):
        # use this instead of assignment to update a vector in place
        self.x = v2.x
        self.y = v2.y

    def slope(self):
        # returns None if infinite
        if self.x == 0:
            return None
        else:
            return (self.y / self.x)

    def cross(self, v2):
        return (self.x * v2.y - self.y * v2.x)

    def normalize(self):
        denom = math.sqrt(abs(self))
        return Vector2(self.x / denom, self.y / denom)


class Line():
    # line segment helper. start and end are Vector2
    def __init__(self, start, end):
        # if the two points are actually exactly same (happens very rarely, only on 0,0),
        # then fake a short line so it still responds to intersection
        if start.y == end.y and start.x == end.x:
            start.y = start.y + 0.1
            start.x = start.x + 0.1
        self.start = start
        self.end = end

    def slope(self):
        # returns None if infinite
        return (self.end - self.start).slope()

    def offset(self):
        # returns None if slope is infinite
        if self.slope():
            return (self.start.y - self.slope() * self.start.x)
        else:
            return None

    def get_abc(self):
        # returns A, B, C that define the line as Ax + By = C
        a = self.end.y - self.start.y
        b = self.start.x - self.end.x
        c = a * self.start.x + b * self.start.y
        return [a, b, c]

    def within(self, point):
        # returns true if the point lies within the box formed by the start and end points
        if near(self.start.x, self.end.x):
            c1 = near(point.x, self.start.x)
        else:
            c1 = point.x < max(self.start.x, self.end.x) and point.x > min(self.start.x, self.end.x)
        if near(self.start.y, self.end.y):
            c2 = near(point.y, self.start.y)
        else:
            c2 = point.y < max(self.start.y, self.end.y) and point.y > min(self.start.y, self.end.y)
        return c1 and c2

    def intersection(self, line):
        # returns the point of intersection if the lines were infinite.
        # if parallel, will return None
        (a1, b1, c1) = self.get_abc()
        (a2, b2, c2) = line.get_abc()
        det = a1 * b2 - a2 * b1
        if det == 0:
            return None
        else:
            x = float(b2 * c1 - b1 * c2) / det
            y = float(a1 * c2 - a2 * c1) / det
            return Vector2(x, y)

    def intersect(self, line):
        # returns true if the line segments intersect
        point = self.intersection(line)
        if point:
            return self.within(point) and line.within(point)
        else:
            return False

class BoundingCircle():
    # bounding circle helper
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def inside(self, point):
        # returns true if the point is inside the circle
        return abs(point - self.center) < (self.radius * self.radius)
