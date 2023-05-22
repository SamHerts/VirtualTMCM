# Virtual Trinamic Motor Driver for Embedded Firmware


This repository provides a virutal motor driver implementation for embedded firmware development. The purpose of this project is to simulate the behavior of a Trinamic motor driver and enable testing and development of embedded firmware without the need for a physical motor driver.
## Features
- Emulates the functionality of a motor driver to interact with embedded firmware.
- Simulates motor control signals such as speed, direction, and braking.
- Supports customizable motor parameters, allowing developers to simulate different motor characteristics.
- Provides an intuitive and easy-to-use API for integration with existing firmware.

## Installation
To use the fake Trinamic 6214 motor driver simulator in your Python project, follow these steps:

- Clone this repository to your local machine or download the source code.

```shell
git clone git@github.com:SamHerts/VirtualTMCM.git
```

- Ensure that you have Python 3 installed on your system.

- Install the required dependencies using pip:

```shell
pip install -r requirements.txt
```

Usage

The virtual motor driver provides a simulated TMCM-6214 which uses TMCL to initialize the driver, control the motor, and obtain status information. Here's a basic pseudo-code example of how to use the virtual motor driver:
- Initialize a serial port for your embedded firmware to use, and pass it to the VirtualTMCM application:
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```
- Change the serial port in main.py to the opened port from the above command:
```python
serial_port_fd = "/dev/pts/0"
```

- Run your program and use the TMCL documentation to communicate with the virtualized driver
```c++

#include "fcntl.h"
#include "your_implementation_of_tmcm.h"

int main() {
    // Initialize the motor driver
    Trinamic::TMCM6214 tmcm_6214;
    tmcm_6214.init("/dev/pts/0);

    // Set the motor speed and direction
    tmcm_6214.set_speed(100);
    tmcm_6214.set_direction(FORWARD);

    // Start the motor
    tmcm_6214.start();

    // Wait for some time
    delay_ms(5000);

    // Stop the motor
    tmcm_6214.stop();

    return 0;
}
```

For more details on available functions and their usage, please refer to the API documentation.
Customization

The virtual motor driver allows you to customize various parameters to simulate different motor characteristics. You can modify the parameters at startup, or by setting the Axis Parameter associated with the desired setting

Feel free to adjust these parameters to match the behavior of the motor you are emulating.
## Contributing

Contributions to this project are welcome and encouraged! If you have any ideas, bug fixes, or feature implementations, please submit a pull request. Before contributing, please review the contribution guidelines.
## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute this code as per the terms of the license.
## Acknowledgments

- This project was inspired by the need for a simulated motor driver for embedded firmware testing and development.
