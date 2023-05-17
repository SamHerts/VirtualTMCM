from tmcl import TMCLParameter, TMCLStatus, TMCLReply, TMCLRequest


class Trinamic5160:
    def __init__(self, tick_speed, identity):
        self.identity = identity
        self.parameters = {
            TMCLParameter.TARGET_POSITION: 0,
            TMCLParameter.ACTUAL_POSITION: 0,
            TMCLParameter.ACTUAL_SPEED: 0,
            TMCLParameter.MAXIMUM_POSITIONING_SPEED: None,
            TMCLParameter.MAXIMUM_ACCELERATION: None,
            TMCLParameter.ABSOLUTE_MAX_CURRENT: None,
            TMCLParameter.STANDBY_CURRENT: None,
            TMCLParameter.POSITION_REACHED_FLAG: None,
            TMCLParameter.ACCELERATION_A1: None,
            TMCLParameter.VELOCITY_V1: None,
            TMCLParameter.MAXIMUM_DECELERATION: None,
            TMCLParameter.AXIS_PARAM_VELOCITY_VSTART: None,
            TMCLParameter.AXIS_PARAM_VELOCITY_VSTOP: None,
            TMCLParameter.AXIS_PARAM_RAMP_WAIT_TIME: None,
            TMCLParameter.AXIS_PARAM_SERIAL_HEARTBEAT: None,
            TMCLParameter.AXIS_PARAM_RELATIVE_POSITIONING_OPTION: None,
            TMCLParameter.AXIS_PARAM_MICROSTEP_RESOLUTION: None,
            TMCLParameter.AXIS_PARAM_CHOPPER_OFF_TIME: None,
            TMCLParameter.AXIS_PARAM_LATCHED_POSITION: None,
            TMCLParameter.AXIS_PARAM_LATCHED_ENCODER: None,
            TMCLParameter.AXIS_PARAM_ENCODER_MODE: None,
            TMCLParameter.AXIS_PARAM_ACTUAL_LOAD_VALUE: None,
            TMCLParameter.AXIS_PARAM_EXTENDED_ERROR_FLAGS: None,
            TMCLParameter.AXIS_PARAM_MOTOR_DRIVER_ERROR_FLAGS: None,
            TMCLParameter.AXIS_PARAM_ENCODER_POSITION: None,
            TMCLParameter.AXIS_PARAM_ENCODER_RESOLUTION: None,
            TMCLParameter.AXIS_PARAM_ENCODER_DEVIATION: None,
            TMCLParameter.AXIS_PARAM_EXTERNAL_ENCODER_POSITION: None,
            TMCLParameter.AXIS_PARAM_EXTERNAL_ENCODER_RESOLUTION: None,
            TMCLParameter.AXIS_PARAM_EXTERNAL_ENCODER_DEVIATION: None,
            TMCLParameter.AXIS_PARAM_REVERSE_SHAFT: None,
        }

        self.status = TMCLStatus()
        self.reply = TMCLReply(0, 0, 0, 0, 0)
        self.request = TMCLRequest(0, 0, 0, 0, 0)
        self.tick_speed = tick_speed
        self.direction_is_forward = True

    def __str__(self):
        return "TMC5160.{0} - Dir:{1}, AP:{2}, AV:{3}".format(
            self.identity,
            self.direction_is_forward,
            self.parameters[TMCLParameter.AXIS_PARAM_ACTUAL_POSITION],
            self.parameters[TMCLParameter.AXIS_PARAM_ACTUAL_SPEED],
        )

    def set_parameter(self, param: TMCLParameter, value: int) -> None:
        if param in self.parameters:
            self.parameters[param] = value
        else:
            raise ValueError("Invalid parameter.")

    def get_parameter(self, param: TMCLParameter) -> int:
        if param in self.parameters:
            return self.parameters[param]
        else:
            raise ValueError("Invalid parameter.")

    def move_to_position(self, target_position):
        self.set_parameter(TMCLParameter.TARGET_POSITION, target_position)
        actual_position = self.get_parameter(TMCLParameter.ACTUAL_POSITION)

        self.direction_is_forward = True if (target_position - actual_position) >= 0 else False

    def update(self):
        # Update the position
        actual_position = self.get_parameter(TMCLParameter.ACTUAL_POSITION)
        actual_velocity = self.get_parameter(TMCLParameter.ACTUAL_SPEED)
        target_position = self.get_parameter(TMCLParameter.TARGET_POSITION)
        maximum_velocity = self.get_parameter(TMCLParameter.MAXIMUM_POSITIONING_SPEED)
        acceleration = self.get_parameter(TMCLParameter.ACCELERATION_A1)

        direction_sign = 1 if self.direction_is_forward else -1

        if target_position != actual_position:
            if abs(actual_velocity) <= maximum_velocity:
                actual_velocity = actual_velocity + ((acceleration / self.tick_speed) * direction_sign)
                if abs(actual_velocity) > maximum_velocity:
                    actual_velocity = maximum_velocity * direction_sign

                self.set_parameter(TMCLParameter.ACTUAL_SPEED, int(actual_velocity))

            self.set_parameter(TMCLParameter.POSITION_REACHED_FLAG, 0)
            actual_position = actual_position + actual_velocity
            # Check if we go past
            if self.direction_is_forward:
                if actual_position > target_position:
                    actual_position = target_position
            else:
                if actual_position < target_position:
                    actual_position = target_position

            self.set_parameter(TMCLParameter.ACTUAL_POSITION, int(actual_position))
            self.set_parameter(TMCLParameter.ENCODER_POSITION, int(actual_position))

        else:
            self.set_parameter(TMCLParameter.POSITION_REACHED_FLAG, 1)
            self.set_parameter(TMCLParameter.ACTUAL_SPEED, 0)


class Trinamic6214:
    def __init__(self, tick_speed, motor_count):
        self.motor_array = [Trinamic5160(tick_speed, idx) for idx in range(motor_count)]
        self.motor_count = motor_count

    def move_to_position(self, idx, position):
        self.motor_array[idx].move_to_position(position)

    def motor_stop(self, idx):
        self.motor_array[idx].set_parameter(TMCLParameter.AXIS_PARAM_ACTUAL_SPEED, 0)

    def set_max_velocity(self, idx, velocity):
        self.motor_array[idx].set_parameter(TMCLParameter.AXIS_PARAM_MAXIMUM_POSITIONING_SPEED, velocity)

    def set_acceleration(self, idx, accel):
        self.motor_array[idx].set_parameter(TMCLParameter.AXIS_PARAM_ACCELERATION_A1, accel)

    def get_position(self, idx):
        return self.motor_array[idx].get_parameter(TMCLParameter.AXIS_PARAM_ACTUAL_POSITION)

    def update(self):
        for motor in self.motor_array:
            motor.update()
