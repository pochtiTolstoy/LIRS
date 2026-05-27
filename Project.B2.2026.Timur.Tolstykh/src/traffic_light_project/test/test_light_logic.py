import pytest

from traffic_light_project.light_logic import TrafficLightCycle


def build_cycle():
    return TrafficLightCycle(
        'horizontal',
        'vertical',
        'green',
        'yellow',
        5.0,
        1.5,
    )


def test_cycle_starts_with_horizontal_green():
    cycle = build_cycle()

    state = cycle.get_state(0.0)

    assert state['active_axis'] == 'horizontal'
    assert state['color'] == 'green'
    assert state['seconds_remaining'] == 5.0
    assert state['cycle_count'] == 0


def test_cycle_switches_to_vertical_green():
    cycle = build_cycle()

    state = cycle.get_state(6.6)

    assert state['active_axis'] == 'vertical'
    assert state['color'] == 'green'
    assert state['cycle_count'] == 0


def test_cycle_counts_next_period():
    cycle = build_cycle()

    state = cycle.get_state(13.2)

    assert state['active_axis'] == 'horizontal'
    assert state['color'] == 'green'
    assert state['cycle_count'] == 1


def test_configure_manual_mode_changes_state():
    cycle = build_cycle()

    message = cycle.configure(True, 'vertical', 0.0, 0.0)
    state = cycle.get_state(100.0)

    assert message == 'manual mode enabled'
    assert state['active_axis'] == 'vertical'
    assert state['color'] == 'green'
    assert state['seconds_remaining'] == 0.0


def test_configure_automatic_mode_changes_durations():
    cycle = build_cycle()

    message = cycle.configure(False, 'vertical', 4.0, 1.0)
    state = cycle.get_state(0.0)

    assert message == 'automatic mode enabled'
    assert cycle.green_duration == 4.0
    assert cycle.yellow_duration == 1.0
    assert state['active_axis'] == 'vertical'
    assert state['color'] == 'green'


def test_configure_rejects_invalid_axis():
    cycle = build_cycle()

    with pytest.raises(ValueError):
        cycle.configure(False, 'diagonal', 0.0, 0.0)
