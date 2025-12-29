from machine import Pin, PWM, UART, time_pulse_us
import time
import _thread

# ==========================================================
# Configuration
# ==========================================================

# Motor (L298N) pins
MOTOR_A_PWM = 7     # ENA
MOTOR_A_IN1 = 6
MOTOR_A_IN2 = 5

MOTOR_B_PWM = 2     # ENB
MOTOR_B_IN1 = 4
MOTOR_B_IN2 = 3

# HC-SR04 pins
SONAR_TRIG = 27
SONAR_ECHO = 28

# Bluetooth UART
BT_UART_ID = 0
BT_BAUDRATE = 9600
BT_TX = 0
BT_RX = 1

# Constants
SAFE_DISTANCE_CM = 20
MAX_PWM = 65535
SONAR_TIMEOUT_US = 30000

# ==========================================================
# Hardware setup
# ==========================================================

# Motor PWM
motor_a_pwm = PWM(Pin(MOTOR_A_PWM))
motor_b_pwm = PWM(Pin(MOTOR_B_PWM))
motor_a_pwm.freq(1000)
motor_b_pwm.freq(1000)

# Motor direction pins
motor_a_in1 = Pin(MOTOR_A_IN1, Pin.OUT)
motor_a_in2 = Pin(MOTOR_A_IN2, Pin.OUT)
motor_b_in1 = Pin(MOTOR_B_IN1, Pin.OUT)
motor_b_in2 = Pin(MOTOR_B_IN2, Pin.OUT)

# Sonar
trig = Pin(SONAR_TRIG, Pin.OUT)
echo = Pin(SONAR_ECHO, Pin.IN)

# Bluetooth UART
uart = UART(BT_UART_ID, baudrate=BT_BAUDRATE, tx=Pin(BT_TX), rx=Pin(BT_RX))

# Onboard LED
led = Pin(25, Pin.OUT)


# ==========================================================
# Global state
# ==========================================================
last_command = "S" # Stop by default

# ==========================================================
# Shared state (multicore)
# ==========================================================

distance_cm = 1000.0
distance_lock = _thread.allocate_lock()


# ==========================================================
# Bluetooth commands mapping
# ==========================================================

# Each command maps to: (motor1_dir, motor1_speed, motor2_dir, motor2_speed)
COMMANDS = {
    "FS": ("F", 50, "F", 50),   # Forward short
    "F":  ("F", 50, "F", 50),   # Forward
    "B":  ("B", 50, "B", 50),   # Backward
    "R":  ("B", 70, "F", 70),   # Rotate right
    "L":  ("F", 70, "B", 70),   # Rotate left
    "J":  ("B", 40, "B", 100),  # Diagonal/back-left
    "H":  ("B", 100, "B", 40),  # Diagonal/back-right
    "G":  ("F", 100, "F", 40),  # Diagonal/forward-left
    "I":  ("F", 40, "F", 100),  # Diagonal/forward-right
    "S":  ("S", 0, "S", 0),     # Stop
}

# ==========================================================
# Motor control
# ==========================================================

def set_motors(m1_dir, m1_speed, m2_dir, m2_speed):
    """
    Control both motor channels independently.
    """
    duty_m1 = int(MAX_PWM * max(0, min(100, m1_speed)) / 100)
    duty_m2 = int(MAX_PWM * max(0, min(100, m2_speed)) / 100)

    # Motor A
    motor_a_pwm.duty_u16(duty_m1)
    if m1_dir == 'F':
        motor_a_in1.value(1); motor_a_in2.value(0)
    elif m1_dir == 'B':
        motor_a_in1.value(0); motor_a_in2.value(1)
    else:
        motor_a_in1.value(0); motor_a_in2.value(0)

    # Motor B
    motor_b_pwm.duty_u16(duty_m2)
    if m2_dir == 'F':
        motor_b_in1.value(1); motor_b_in2.value(0)
    elif m2_dir == 'B':
        motor_b_in1.value(0); motor_b_in2.value(1)
    else:
        motor_b_in1.value(0); motor_b_in2.value(0)

# ==========================================================
# HC-SR04 distance measurement
# ==========================================================

def read_distance():
    """Read distance in cm using HC-SR04."""
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    try:
        pulse = time_pulse_us(echo, 1, SONAR_TIMEOUT_US)
        if pulse < 0:
            return 1000.0
        return min(pulse / 58.0, 400.0)
    except OSError:
        return 1000.0

def distance_worker():
    """Continuously update distance on core 1."""
    global distance_cm
    while True:
        d = read_distance()
        with distance_lock:
            distance_cm = d
        time.sleep(0.05)

# Start distance thread on core 1
_thread.start_new_thread(distance_worker, ())

# ==========================================================
# LED heartbeat
# ==========================================================

def blink_led():
    led.toggle()

# ==========================================================
# Main loop
# ==========================================================

blink_counter = 0

while True:

    with distance_lock:
        d = distance_cm

    # -------------------------
    # Obstacle avoidance
    # -------------------------
    if d < SAFE_DISTANCE_CM:
        print(f"Obstacle detected! Distance: {d:.2f} cm. Moving backward.")
        set_motors("B", 50, "B", 50)
        time.sleep(0.5)
        set_motors("S", 0, "S", 0)
        continue

    # -------------------------
    # Execute last command
    # -------------------------
    if last_command == "FS":
        m1_dir, m1_speed, m2_dir, m2_speed = COMMANDS["FS"]
        set_motors(m1_dir, m1_speed, m2_dir, m2_speed)
        time.sleep(0.1)
        set_motors("S", 0, "S", 0)
        last_command = "S"
    else:
        if last_command in COMMANDS:
            m1_dir, m1_speed, m2_dir, m2_speed = COMMANDS[last_command]
            set_motors(m1_dir, m1_speed, m2_dir, m2_speed)
        else:
            set_motors("S", 0, "S", 0)

    # -------------------------
    # Bluetooth command handling
    # -------------------------
    if uart.any():
        line = uart.readline()
        if line:
            try:
                cmd = line.decode("utf-8").strip()
                uart.write(cmd + "\n")
                print(f"Received command: {cmd}")
                last_command = cmd if cmd else "S"
            except Exception as e:
                print(f"UART error: {e}")

    # -------------------------
    # LED heartbeat
    # -------------------------
    blink_counter += 1
    if blink_counter >= 10:
        blink_led()
        blink_counter = 0

    time.sleep(0.1)
