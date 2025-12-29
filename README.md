# Pico Wheely

**Pico Wheely** is a 4WD Raspberry Pi Pico-powered car with Bluetooth control, ultrasonic obstacle avoidance, and a fully containerized development setup.  
It features:

- Independent motor control via **L298N** (2 channels → 4 motors)  
- **HC-SR04** ultrasonic sensor for obstacle detection  
- Bluetooth commands for mobile control  
- LED heartbeat for visual feedback  
- Reproducible development environment with **VS Code dev container**  
- Easy-to-modify MicroPython code  

---

## Table of Contents

- [Hardware](#hardware)  
- [3D Printed Components](#3d-printed-components)  
- [Wiring](#wiring)  
- [Bluetooth Commands](#bluetooth-commands)  
- [Setup & Flashing](#setup--flashing)  
- [Running the Car](#running-the-car)  
- [Future Improvements](#future-improvements)  
- [License](#license)  

---

## Hardware

| Component | Model / Notes |
|-----------|---------------|
| Microcontroller | Raspberry Pi Pico |
| Motor Driver | L298N (2 channels) |
| Motors | 4 DC motors (2 per channel) |
| Battery | 2-cell li-ion battery 18650 |
| Distance Sensor | HC-SR04 |
| Bluetooth | UART module (HC-05 / HC-06 / HM-10) |
| LED | Onboard Pico LED (GPIO 25) |

---

## 3D Printed Components

- **Car chassis** – main body  
- **Pico mount** – supports the Pico module  
- **HC-SR04 mount** - support for the HC-SR04 sensor
- **Motor controller mount** – fixes L298N on chassis  

**Print Settings (recommended):**  
- Material: PETG and PLA
- Infill: 20–30%  
- Layer height: 0.2mm  
- Supports: Only if necessary for mounts  

**Files:** `/cad/` folder in repository (STL)

---

## Wiring

| Signal | Pin on Pico | Notes |
|--------|------------|-------|
| MOTOR_A PWM | GPIO 7 | ENA |
| MOTOR_A IN1 | GPIO 6 | Direction |
| MOTOR_A IN2 | GPIO 5 | Direction |
| MOTOR_B PWM | GPIO 2 | ENB |
| MOTOR_B IN1 | GPIO 4 | Direction |
| MOTOR_B IN2 | GPIO 3 | Direction |
| HC-SR04 TRIG | GPIO 27 | Output |
| HC-SR04 ECHO | GPIO 28 | Input |
| UART TX | GPIO 0 | Bluetooth TX |
| UART RX | GPIO 1 | Bluetooth RX |
| LED | GPIO 25 | Onboard |

---

## Bluetooth Commands

Send single-character commands via your mobile Bluetooth app. Android Arduino Car can be used

| Command | Action |
|---------|-------|
| `F` | Forward |
| `B` | Backward |
| `L` | Rotate Left |
| `R` | Rotate Right |
| `FS` | Forward short (0.1s) |
| `G` | Forward-left (diagonal) |
| `I` | Forward-right (diagonal) |
| `H` | Backward-right (diagonal) |
| `J` | Backward-left (diagonal) |
| `S` | Stop |

---

## Setup & Flashing

**Using VS Code Dev Container:**

1. Open the project in VS Code  
2. Reopen in **Dev Container**  
4. Connect Pico via USB  
5. Flash the code



## WSL Utils

In case of using Windows and WSL, the usb needs to be attached to the WSL
1. Open Windows Powershell as Administrator
2. Use "usbipd list" to identify the USB device
3. Bind the device: "usbipd bind --busid 1-8"
4. Attache the device to the WSL "usbipd attach --wsl --busid 1-8"

## Control with Android Arduino CAR
1. Open Android Marketplace
2. Install Android Arduino CAR
3. Connect to the Bluetooth device
4. Have fun :)
