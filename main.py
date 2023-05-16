from TMCL.tmcm import Trinamic6214
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

        if not parts:
            continue
        elif parts[0] == 'move':
            if len(parts) < 3:
                print("Invalid command. Please provide a motor and/or distance.")
                continue

            try:
                distance = int(parts[2])
                trinamic_6214.motor_array[int(parts[1])].move_to_position(distance)
                print("Moved motor by", distance)
            except ValueError:
                print("Invalid distance. Please provide an integer.")
        elif parts[0] == 'gp':
            if len(parts) < 2:
                print("Invalid command. Please provide a motor.")
                continue
            print("Current position:", trinamic_6214.motor_array[int(parts[1])].get_position())
        elif parts[0] == 'exit':
            print("Exiting...")
            is_running = False
            break
        else:
            print("Invalid command. Please try again.")


def main():
    global trinamic_6214
    for motor in trinamic_6214.motor_array:
        motor.set_acceleration(200)
        motor.set_max_velocity(100)
        print("Initial position:", motor.get_position())

    global is_running
    is_running = True
    x = Thread(target=comm_loop, daemon=True)
    x.start()

    while is_running:
        trinamic_6214.update()
        sleep(1 / tick_speed)

    x.join()


if __name__ == '__main__':
    print("Starting VirtualTMCM")

    main()
