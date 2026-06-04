from math import pi


def axis_position(axis: str, x: float, y: float) -> float:
    # Each turtle moves only along one axis, so we project the pose onto the
    # coordinate that matters for crossing decisions.
    if axis == 'horizontal':
        return x
    return y


def should_reverse(
    position: float,
    direction: int,
    min_position: float,
    max_position: float,
) -> bool:
    if direction > 0:
        return position >= max_position
    return position <= min_position


def has_cleared_center(
    position: float,
    direction: int,
    intersection: float,
    clear_distance: float,
) -> bool:
    if direction > 0:
        return position > intersection + clear_distance
    return position < intersection - clear_distance


def is_approaching_center(position: float, direction: int, intersection: float) -> bool:
    if direction > 0:
        return position < intersection
    return position > intersection


def is_axis_green(light_state: dict, axis: str, green_color: str) -> bool:
    return light_state['active_axis'] == axis and light_state['color'] == green_color


def should_request_crossing(
    turtle: dict,
    position: float,
    intersection: float,
    request_distance: float,
) -> bool:
    # Do not send duplicate requests while one is already pending or once the
    # turtle has already received permission for this crossing.
    if turtle['request_pending'] or turtle['permission_granted']:
        return False

    if not is_approaching_center(position, turtle['direction'], intersection):
        return False

    return abs(intersection - position) <= request_distance


def should_stop(
    turtle: dict,
    light_state: dict,
    position: float,
    intersection: float,
    stop_distance: float,
    light_buffer_distance: float,
    green_color: str,
) -> bool:
    if not is_approaching_center(position, turtle['direction'], intersection):
        return False

    distance = abs(intersection - position)

    if turtle['permission_granted']:
        return False

    # This is the hard stop line right before the center of the intersection.
    if distance <= stop_distance:
        return True

    # Slightly earlier than the stop line we already respect the light, so the
    # turtle does not slide into the intersection.
    if distance <= light_buffer_distance and not is_axis_green(
        light_state,
        turtle['axis'],
        green_color,
    ):
        return True

    return False


def desired_heading(axis: str, direction: int) -> float:
    # The sign of direction decides whether the turtle should face right/left
    # on the horizontal lane or up/down on the vertical lane.
    if axis == 'horizontal':
        if direction > 0:
            return 0.0
        return pi

    if direction > 0:
        return pi / 2.0
    return -pi / 2.0
