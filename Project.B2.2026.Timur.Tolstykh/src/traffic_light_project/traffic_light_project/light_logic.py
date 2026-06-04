class TrafficLightCycle:
    def __init__(
        self,
        horizontal_axis: str,
        vertical_axis: str,
        green_color: str,
        yellow_color: str,
        green_duration: float = 5.0,
        yellow_duration: float = 1.5,
    ) -> None:
        self.horizontal_axis = horizontal_axis
        self.vertical_axis = vertical_axis
        self.green_color = green_color
        self.yellow_color = yellow_color
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.manual_mode = False
        self.manual_axis = self.horizontal_axis
        self.phases = []
        self.period = 0.0
        self.set_automatic_order(self.horizontal_axis)

    def is_valid_axis(self, axis: str) -> bool:
        return axis == self.horizontal_axis or axis == self.vertical_axis

    def set_automatic_order(self, start_axis: str) -> None:
        if start_axis == self.vertical_axis:
            first_axis = self.vertical_axis
            second_axis = self.horizontal_axis
        else:
            first_axis = self.horizontal_axis
            second_axis = self.vertical_axis

        # One full cycle alternates green/yellow for one axis and then
        # green/yellow for the other axis.
        self.phases = [
            {
                'active_axis': first_axis,
                'color': self.green_color,
                'duration': self.green_duration,
            },
            {
                'active_axis': first_axis,
                'color': self.yellow_color,
                'duration': self.yellow_duration,
            },
            {
                'active_axis': second_axis,
                'color': self.green_color,
                'duration': self.green_duration,
            },
            {
                'active_axis': second_axis,
                'color': self.yellow_color,
                'duration': self.yellow_duration,
            },
        ]

        self.period = 0.0
        for light_phase in self.phases:
            self.period += light_phase['duration']

    def configure(
        self,
        manual: bool,
        active_axis: str,
        green_duration: float,
        yellow_duration: float,
    ) -> str:
        if not self.is_valid_axis(active_axis):
            raise ValueError('active_axis must be horizontal or vertical')

        if green_duration < 0.0:
            raise ValueError('green_duration must be >= 0')
        if yellow_duration < 0.0:
            raise ValueError('yellow_duration must be >= 0')

        if green_duration > 0.0:
            self.green_duration = green_duration
        if yellow_duration > 0.0:
            self.yellow_duration = yellow_duration

        if manual:
            self.manual_mode = True
            self.manual_axis = active_axis
            return 'manual mode enabled'

        self.manual_mode = False
        self.set_automatic_order(active_axis)
        return 'automatic mode enabled'

    def get_state(self, elapsed_seconds: float) -> dict:
        if self.manual_mode:
            return {
                'active_axis': self.manual_axis,
                'color': self.green_color,
                'seconds_remaining': 0.0,
                'cycle_count': 0,
            }

        cycle_count = int(elapsed_seconds // self.period)
        phase = elapsed_seconds % self.period

        for light_phase in self.phases:
            duration = light_phase['duration']
            # Move through the phase list by subtracting durations until we
            # land in the current slice of the cycle.
            if phase < duration:
                return {
                    'active_axis': light_phase['active_axis'],
                    'color': light_phase['color'],
                    'seconds_remaining': duration - phase,
                    'cycle_count': cycle_count,
                }

            phase -= duration

        raise RuntimeError('traffic light phase was not found')
