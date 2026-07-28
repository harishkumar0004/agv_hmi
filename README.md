# AGV Delivery HMI

PyQt5-based touchscreen interface for a food delivery robot.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python3 main.py

# 3. For Raspberry Pi kiosk mode (no window manager)
QT_QPA_PLATFORM=eglfs python3 main.py
```

## Project Structure

```
agv_hmi/
├── main.py              # Entry point
├── controller.py        # State machine (brain)
├── main_window.py       # Screen router
├── config.py            # All constants
├── widgets/             # Reusable components
│   ├── __init__.py
│   └── face_widget.py   # Tap/hold face with moods
├── screens/             # One per screen
│   ├── __init__.py
│   ├── idle_screen.py
│   ├── assignment_screen.py
│   ├── transit_screen.py
│   ├── arrived_screen.py
│   └── settings_screen.py
└── requirements.txt
```

## Architecture Rules

1. **Controller owns all state** — screens are dumb display
2. **MainWindow is the only router** — screens never talk to each other
3. **Signals go one way** — Controller → Screens, Screens → Controller
4. **Each screen has on_enter()/on_exit()** — self-contained lifecycle

## State Machine

```
Idle → Assignment → Navigating → Arrived → [more stops? → Navigating]
                                         → [done → Returning → Idle]
```

## Part 1 Status

- ✅ Controller with full state machine
- ✅ MainWindow router (on_exit → setCurrentWidget → on_enter)
- ✅ FaceWidget with tap vs long-press
- ✅ All 5 placeholder screens wired correctly
- ✅ PIN overlay for settings
- ✅ 45s arrival reminder timer
- ✅ Inactivity timeout on assignment screen
- ⬜ Real face images (using emoji placeholders)
- ⬜ ESP32 serial link (Part 6)
- ⬜ Real hardware GPIO (Part 6)
