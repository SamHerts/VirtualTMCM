from TMCL.tmcm import Trinamic6214
from TMCL.tmcl import TMCLParameter, TMCLRequest, TMCLCommand

from time import sleep
from threading import Thread

tick_speed = 100
is_running = False

trinamic_6214 = Trinamic6214(tick_speed, 1)


def comm_loop():
    global is_running
    while is_running:
        command = input("Enter a command (move <motor> <distance>, gp <motor>, or exit): ")
        parts = command.split()

        match parts:
            case []:
                continue
            case [('MVP' | 'mvp'), motor_idx, position] if len(parts) >= 3:
                trinamic_6214.process_command(TMCLRequest(0, TMCLCommand.MVP, 0, int(motor_idx), int(position)))
            case [('GAP' | 'gap'), motor_idx] if len(parts) >= 2:
                trinamic_6214.process_command(TMCLRequest(0, TMCLCommand.GAP, TMCLParameter.ACTUAL_POSITION, int(motor_idx), 0))
            case [('exit' | 'quit')]:
                print("Exiting...")
                is_running = False
                break
            case [command, command_type, motor_bank, value] if len(parts) == 4:
                request = TMCLRequest(0, int(command), int(command_type), int(motor_bank), int(value))
                trinamic_6214.process_command(request)
            case _:
                print("Invalid command. Please try again.")


def main():
    global trinamic_6214
    for idx in range(trinamic_6214.motor_count):
        trinamic_6214.set_acceleration(idx, 200)
        trinamic_6214.set_max_velocity(idx, 100)
        print("Initial position:", trinamic_6214.get_position(idx))

    global is_running
    is_running = True
    x = Thread(target=comm_loop, daemon=True)
    x.start()

    while is_running:
        trinamic_6214.update()
        sleep(1)

    x.join()


if __name__ == '__main__':
    print("Starting VirtualTMCM")

    main()
