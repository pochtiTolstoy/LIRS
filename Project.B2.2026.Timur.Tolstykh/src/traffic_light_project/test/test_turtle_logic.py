from math import pi

from traffic_light_project.turtle_logic import axis_position
from traffic_light_project.turtle_logic import desired_heading
from traffic_light_project.turtle_logic import has_cleared_center
from traffic_light_project.turtle_logic import is_axis_green
from traffic_light_project.turtle_logic import should_request_crossing
from traffic_light_project.turtle_logic import should_reverse
from traffic_light_project.turtle_logic import should_stop


def test_axis_position_uses_matching_coordinate():
    assert axis_position('horizontal', 2.0, 7.0) == 2.0
    assert axis_position('vertical', 2.0, 7.0) == 7.0


def test_should_reverse_at_boundaries():
    assert should_reverse(10.2, 1, 0.8, 10.2) is True
    assert should_reverse(0.8, -1, 0.8, 10.2) is True
    assert should_reverse(5.0, 1, 0.8, 10.2) is False


def test_has_cleared_center_depends_on_direction():
    assert has_cleared_center(5.6, 1, 5.0, 0.5) is True
    assert has_cleared_center(4.4, -1, 5.0, 0.5) is True
    assert has_cleared_center(5.2, 1, 5.0, 0.5) is False


def test_is_axis_green_matches_axis_and_color():
    light_state = {
        'active_axis': 'horizontal',
        'color': 'green',
    }

    assert is_axis_green(light_state, 'horizontal', 'green') is True
    assert is_axis_green(light_state, 'vertical', 'green') is False


def test_should_request_crossing_only_when_approaching():
    turtle = {
        'axis': 'horizontal',
        'direction': 1,
        'request_pending': False,
        'permission_granted': False,
    }

    assert should_request_crossing(turtle, 4.0, 5.0, 1.2) is True
    assert should_request_crossing(turtle, 6.0, 5.0, 1.2) is False


def test_should_stop_when_red_and_close():
    turtle = {
        'axis': 'horizontal',
        'direction': 1,
        'permission_granted': False,
    }
    light_state = {
        'active_axis': 'vertical',
        'color': 'green',
    }

    assert should_stop(turtle, light_state, 4.2, 5.0, 0.7, 1.1, 'green') is True


def test_should_not_stop_when_permission_already_granted():
    turtle = {
        'axis': 'horizontal',
        'direction': 1,
        'permission_granted': True,
    }
    light_state = {
        'active_axis': 'vertical',
        'color': 'green',
    }

    assert should_stop(turtle, light_state, 4.5, 5.0, 0.7, 1.1, 'green') is False


def test_desired_heading_matches_axis_and_direction():
    assert desired_heading('horizontal', 1) == 0.0
    assert desired_heading('horizontal', -1) == pi
    assert desired_heading('vertical', 1) == pi / 2.0
