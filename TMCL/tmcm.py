from TMCL.tmcl import TMCLParameter, TMCLStatus, TMCLReply, TMCLRequest, TMCLGlobalParameter, TMCLDigitalInputs, \
    TMCLCommand


class Trinamic5160:
    def __init__(self, tick_speed, identity):
        self.identity = identity
        self.parameters = {
            TMCLParameter.TARGET_POSITION: 0,
            TMCLParameter.ACTUAL_POSITION: 0,
            TMCLParameter.ACTUAL_SPEED: 0,
            TMCLParameter.MAXIMUM_POSITIONING_SPEED: 0,
            TMCLParameter.MAXIMUM_ACCELERATION: 0,
            TMCLParameter.ABSOLUTE_MAX_CURRENT: 0,
            TMCLParameter.STANDBY_CURRENT: 0,
            TMCLParameter.POSITION_REACHED_FLAG: 0,
            TMCLParameter.ACCELERATION_A1: 0,
            TMCLParameter.VELOCITY_V1: 0,
            TMCLParameter.MAXIMUM_DECELERATION: 0,
            TMCLParameter.AXIS_PARAM_VELOCITY_VSTART: 0,
            TMCLParameter.AXIS_PARAM_VELOCITY_VSTOP: 0,
            TMCLParameter.AXIS_PARAM_RAMP_WAIT_TIME: 0,
            TMCLParameter.AXIS_PARAM_SERIAL_HEARTBEAT: 0,
            TMCLParameter.AXIS_PARAM_RELATIVE_POSITIONING_OPTION: 0,
            TMCLParameter.AXIS_PARAM_MICROSTEP_RESOLUTION: 8,
            TMCLParameter.AXIS_PARAM_CHOPPER_OFF_TIME: 0,
            TMCLParameter.AXIS_PARAM_LATCHED_POSITION: 0,
            TMCLParameter.AXIS_PARAM_LATCHED_ENCODER: 0,
            TMCLParameter.AXIS_PARAM_ENCODER_MODE: 0,
            TMCLParameter.AXIS_PARAM_ACTUAL_LOAD_VALUE: 0,
            TMCLParameter.AXIS_PARAM_EXTENDED_ERROR_FLAGS: 0,
            TMCLParameter.AXIS_PARAM_MOTOR_DRIVER_ERROR_FLAGS: 0,
            TMCLParameter.ENCODER_POSITION: 0,
            TMCLParameter.AXIS_PARAM_ENCODER_RESOLUTION: 3600,
            TMCLParameter.AXIS_PARAM_ENCODER_DEVIATION: 0,
            TMCLParameter.AXIS_PARAM_EXTERNAL_ENCODER_POSITION: 0,
            TMCLParameter.AXIS_PARAM_EXTERNAL_ENCODER_RESOLUTION: 0,
            TMCLParameter.AXIS_PARAM_EXTERNAL_ENCODER_DEVIATION: 0,
            TMCLParameter.AXIS_PARAM_REVERSE_SHAFT: 0,
        }

        self.tick_speed = tick_speed
        self.direction_is_forward = True

    def __str__(self):
        return f"TMC5160.{self.identity}"

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
    def __init__(self, tick_speed, motor_count, serial_port):
        self.motor_array = [Trinamic5160(tick_speed, idx) for idx in range(motor_count)]
        self.motor_count = motor_count
        self.global_parameter_bank_0 = {
            TMCLGlobalParameter.GLOBAL_PARAM_BAUD_RATE: 8,
            TMCLGlobalParameter.GLOBAL_PARAM_SERIAL_ADDRESS: 1,
            TMCLGlobalParameter.GLOBAL_PARAM_SERIAL_HEARTBEAT: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_CAN_BIT_RATE: 8,
            TMCLGlobalParameter.GLOBAL_PARAM_CAN_REPLY_ID: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_CAN_ID: 1,
            TMCLGlobalParameter.GLOBAL_PARAM_TELEGRAM_PAUSE_TIME: 15,
            TMCLGlobalParameter.GLOBAL_PARAM_SERIAL_HOST_ADDRESS: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_AUTO_START_MODE: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_TMCL_CODE_PROTECTION: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_CAN_HEARTBEAT: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_CAN_SECONDARY_ADDRESS: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_COORDINATE_STORAGE: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_DO_NOT_RESTORE_USER_VARIABLES: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_SERIAL_SECONDARY_ADDRESS: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_TMCL_APPLICATION_STATUS: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_DOWNLOAD_MODE: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_TMCL_PROGRAM_COUNTER: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_TMCL_TICK_TIMER: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_RANDOM_NUMBER: 0,
            TMCLGlobalParameter.GLOBAL_PARAM_SUPPRESS_REPLY: 1
        }
        self.serial_port = serial_port

        # TODO: Initialize all 3 banks
        self.digital_input_bank_0 = {
            TMCLDigitalInputs.AIN0: 0,
            TMCLDigitalInputs.IN1: 0,
            TMCLDigitalInputs.IN2: 0,
            TMCLDigitalInputs.IN3: 0,
            TMCLDigitalInputs.AIN4: 0,
            TMCLDigitalInputs.IN5: 0,
            TMCLDigitalInputs.IN6: 0,
            TMCLDigitalInputs.IN7: 0,
            TMCLDigitalInputs.STO: 0,
            TMCLDigitalInputs.STO1: 0,
            TMCLDigitalInputs.STO2: 0,
        }

    def set_global_parameter(self, parameter_number: TMCLParameter, value: int) -> TMCLReply:
        self.global_parameter_bank_0[parameter_number] = value
        return TMCLReply(0, 0, TMCLStatus.SUCCESS, TMCLCommand.SGP, 0)

    def get_global_parameter(self, parameter_number: TMCLParameter) -> TMCLReply:
        value = self.global_parameter_bank_0[parameter_number]
        return TMCLReply(0, 0, TMCLStatus.SUCCESS, TMCLCommand.GGP, value)

    def move_to_position(self, command_type: int, axis: int, position: int) -> TMCLReply:
        if self.motor_count > axis >= 0:
            status = TMCLStatus.SUCCESS
        else:
            status = TMCLStatus.WRONG_TYPE

        if command_type not in [0, 1, 2]:
            status = TMCLStatus.WRONG_TYPE

        self.motor_array[axis].move_to_position(position)
        return TMCLReply(0, 0, status, TMCLCommand.MVP, 0)

    def motor_stop(self, axis: int) -> TMCLReply:
        """
        Stop the motor on the specified axis.
        Args:
            axis (int): The axis number.
        Returns:
            TMCLReply
        """
        if self.motor_count > axis >= 0:
            status = TMCLStatus.SUCCESS
        else:
            status = TMCLStatus.WRONG_TYPE
        self.motor_array[axis].set_parameter(TMCLParameter.ACTUAL_SPEED, 0)
        current_position = self.motor_array[axis].get_parameter(TMCLParameter.ACTUAL_POSITION)
        self.motor_array[axis].set_parameter(TMCLParameter.TARGET_POSITION, current_position)
        return TMCLReply(0, 0, status, TMCLCommand.MST, 0)

    def set_axis_parameter(self, parameter_number: TMCLParameter, axis: int, value: int) -> TMCLReply:
        self.motor_array[axis].set_parameter(parameter_number, value)
        if self.motor_count > axis >= 0:
            status = TMCLStatus.SUCCESS
        else:
            status = TMCLStatus.WRONG_TYPE

        return TMCLReply(0, 0, status, TMCLCommand.SAP, value)

    def get_axis_parameter(self, parameter_number: TMCLParameter, axis: int) -> TMCLReply:
        if self.motor_count > axis >= 0:
            status = TMCLStatus.SUCCESS
        else:
            status = TMCLStatus.WRONG_TYPE

        value = self.motor_array[axis].get_parameter(parameter_number)
        return TMCLReply(0, 0, status, TMCLCommand.GAP, value)

    def get_input(self, port: int, bank_number: int) -> TMCLReply:
        # TODO: Return based on bank_number
        if 3 > bank_number >= 0:
            status = TMCLStatus.SUCCESS
        else:
            status = TMCLStatus.WRONG_TYPE

        value = self.digital_input_bank_0[port]
        return TMCLReply(0, 0, status, TMCLCommand.GAP, value)

    def process_command(self, input_bytes: bytes) -> None:
        if len(input_bytes) != 9:
            print("Length of input too long/short")
            return
        request = TMCLRequest.from_buffer(input_bytes)
        print(request)

        match request.command:
            case TMCLCommand.GAP:
                response_result = self.get_axis_parameter(request.commandType, request.motorBank)
            case TMCLCommand.SAP:
                response_result = self.set_axis_parameter(request.commandType, request.motorBank, request.value)
            case TMCLCommand.MST:
                response_result = self.motor_stop(request.motorBank)
            case TMCLCommand.GIO:
                response_result = self.get_input(request.commandType, request.motorBank)
            case TMCLCommand.MVP:
                response_result = self.move_to_position(request.commandType, request.motorBank, request.value)
            case TMCLCommand.SGP:
                response_result = self.set_global_parameter(request.commandType, request.value)
            case TMCLCommand.GGP:
                response_result = self.get_global_parameter(request.commandType)
            case _:
                print("Received invalid command")
                response_result = TMCLReply(0, 0, TMCLStatus.INVALID_COMMAND, 0, 0)

        self.send_response(response_result)

    def send_response(self, response: TMCLReply) -> None:
        print(response)
        self.serial_port.send(response.to_buffer())

    def update(self) -> None:
        for motor in self.motor_array:
            motor.update()
