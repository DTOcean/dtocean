import math


def bearing_to_radians(bearing):
    angle = 90.0 - bearing
    if angle <= -180.0:
        angle += 360.0

    angle = math.radians(angle)

    if angle < 0:
        angle += 2 * math.pi

    return angle


def radians_to_bearing(x):
    initial_bearing = 90 - math.degrees(x)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing
