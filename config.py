"""
config.py — All system constants, pins, timers, and configuration.

This is the SINGLE place to change values. No magic numbers anywhere else.
"""

# ─────────────────────────────────────────────────────────────
# HARDWARE / GPIO (Raspberry Pi BCM numbering)
# ─────────────────────────────────────────────────────────────
SHUTDOWN_REQUEST_PIN = 25      # ESP32 → Pi: "please shut down"
SHUTDOWN_ACK_PIN = 26          # Pi → ESP32: "I'm truly halted"

# ─────────────────────────────────────────────────────────────
# SERIAL (ESP32 communication)
# ─────────────────────────────────────────────────────────────
SERIAL_PORT = "/dev/ttyUSB0"   # or /dev/ttyAMA0 if using GPIO UART
SERIAL_BAUD = 115200

# ─────────────────────────────────────────────────────────────
# DELIVERY TASK
# ─────────────────────────────────────────────────────────────
RACK_COUNT = 3                 # how many racks on the robot
TABLE_COUNT = 20               # how many tables in the restaurant

# ─────────────────────────────────────────────────────────────
# TIMERS (all in milliseconds)
# ─────────────────────────────────────────────────────────────
LONG_PRESS_MS = 2500           # how long to hold face to enter assignment
INACTIVITY_TIMEOUT_MS = 25000  # auto-return to idle from assignment screen
ARRIVAL_REMINDER_MS = 45000    # "worried" face + banner if no confirmation
IDLE_BLINK_INTERVAL_MS = 4000  # face blink cycle when idle

# ─────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────
ADMIN_PIN = "1234"             # PIN to enter Settings (change for production!)

# ─────────────────────────────────────────────────────────────
# DISPLAY
# ─────────────────────────────────────────────────────────────
SCREEN_WIDTH = 800             # Waveshare 7" display
SCREEN_HEIGHT = 480
FULLSCREEN = True
