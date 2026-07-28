"""
assignment_screen.py — Waiter selects racks and assigns tables.

Flow:
  1. Tap a rack card (Rack 1, 2, or 3)
  2. Table grid appears — tap a table number
  3. Pair appears in "Assigned" list
  4. Repeat for more racks, or tap "Start Delivery"

Features:
  - Battery % display (top-left, staff-facing info)
  - Gear icon (top-right) → PIN overlay → Settings
  - Inactivity timer: auto-return to idle after 25s of no interaction
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout,
    QLineEdit
)

from config import RACK_COUNT, TABLE_COUNT, INACTIVITY_TIMEOUT_MS, ADMIN_PIN


class AssignmentScreen(QWidget):
    """
    ┌─────────────────────────────────────────┐
    │ 🔋 85%                    [⚙️]         │  ← battery + gear
    │                                         │
    │  Select Rack        [Assigned List]     │
    │  [R1] [R2] [R3]     R1→T5  R3→T2       │
    │                                         │
    │  Select Table:      [Start Delivery]    │
    │  [1] [2] [3] [4]...                     │
    │  [5] [6] [7] [8]...                     │
    │                                         │
    │  ┌─────────────────────────────────┐    │
    │  │  Enter PIN                      │    │  ← PIN overlay (modal)
    │  │  [****]                         │    │
    │  │  [1][2][3]  [4][5][6]           │    │
    │  │  [7][8][9]  [C][0][✓]           │    │
    │  └─────────────────────────────────┘    │
    └─────────────────────────────────────────┘
    """

    start_delivery = pyqtSignal()           # "Start" button tapped
    assignment_cancelled = pyqtSignal()     # inactivity timeout
    request_settings = pyqtSignal()         # gear tapped + PIN correct

    def __init__(self, parent=None):
        super().__init__(parent)

        self._selected_rack = None
        self._assigned_pairs = []  # list of (rack, table)

        self._setup_ui()
        self._setup_inactivity_timer()
        self._setup_pin_overlay()

    def _setup_ui(self):
        """Build the assignment screen layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ═══════ TOP BAR: Battery + Gear ═══════
        top_bar = QHBoxLayout()

        # --- Battery % (placeholder until ESP32 reports real data) ---
        self.battery_label = QLabel("🔋 --%", self)
        self.battery_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        top_bar.addWidget(self.battery_label)
        top_bar.addStretch()

        # --- Gear icon for settings ---
        self.gear_btn = QPushButton("⚙️", self)
        self.gear_btn.setFixedSize(40, 40)
        self.gear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                font-size: 20px;
                border: none;
            }
            QPushButton:pressed {
                color: #fff;
            }
        """)
        self.gear_btn.clicked.connect(self._on_gear_clicked)
        top_bar.addWidget(self.gear_btn)

        main_layout.addLayout(top_bar)

        # ═══════ MAIN CONTENT: Rack/Table + Assigned List ═══════
        content = QHBoxLayout()
        content.setSpacing(20)

        # --- LEFT: Rack + Table selection ---
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)

        rack_label = QLabel("Select a Rack:", self)
        rack_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        left_panel.addWidget(rack_label)

        rack_layout = QHBoxLayout()
        self.rack_buttons = []
        for i in range(1, RACK_COUNT + 1):
            btn = QPushButton(f"Rack {i}", self)
            btn.setFixedSize(100, 80)
            btn.setStyleSheet(self._rack_button_style(False))
            btn.clicked.connect(lambda checked, r=i: self._on_rack_selected(r))
            rack_layout.addWidget(btn)
            self.rack_buttons.append(btn)
        left_panel.addLayout(rack_layout)

        self.table_label = QLabel("Select a Table:", self)
        self.table_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        self.table_label.hide()
        left_panel.addWidget(self.table_label)

        self.table_grid = QWidget(self)
        table_layout = QGridLayout(self.table_grid)
        table_layout.setSpacing(8)
        self.table_buttons = []
        for t in range(1, TABLE_COUNT + 1):
            btn = QPushButton(str(t), self)
            btn.setFixedSize(60, 50)
            btn.setStyleSheet(self._table_button_style(False))
            btn.clicked.connect(lambda checked, tbl=t: self._on_table_selected(tbl))
            row = (t - 1) // 5
            col = (t - 1) % 5
            table_layout.addWidget(btn, row, col)
            self.table_buttons.append(btn)
        self.table_grid.hide()
        left_panel.addWidget(self.table_grid)

        left_panel.addStretch()
        content.addLayout(left_panel, stretch=2)

        # --- RIGHT: Assigned list + Start button ---
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignTop)

        assigned_label = QLabel("Assigned Deliveries:", self)
        assigned_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        right_panel.addWidget(assigned_label)

        self.assigned_list = QLabel("None yet", self)
        self.assigned_list.setStyleSheet("""
            QLabel {
                color: #aaa;
                font-size: 14px;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 8px;
                min-height: 100px;
            }
        """)
        self.assigned_list.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_panel.addWidget(self.assigned_list)

        self.start_btn = QPushButton("🚀 Start Delivery", self)
        self.start_btn.setFixedHeight(60)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.start_btn.clicked.connect(self._on_start_clicked)
        right_panel.addWidget(self.start_btn)

        right_panel.addStretch()
        content.addLayout(right_panel, stretch=1)

        main_layout.addLayout(content)
        self.setLayout(main_layout)

    def _setup_inactivity_timer(self):
        """Timer that returns to idle if waiter walks away."""
        self._inactivity_timer = QTimer(self)
        self._inactivity_timer.setSingleShot(True)
        self._inactivity_timer.timeout.connect(self._on_inactivity_timeout)

    def _setup_pin_overlay(self):
        """Modal PIN keypad overlay for settings access."""
        self.pin_overlay = QWidget(self)
        self.pin_overlay.setGeometry(200, 80, 400, 420)
        self.pin_overlay.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 2px solid #444;
                border-radius: 15px;
            }
        """)
        self.pin_overlay.hide()
        self.pin_overlay.raise_()

        overlay_layout = QVBoxLayout(self.pin_overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)

        pin_title = QLabel("Enter PIN", self.pin_overlay)
        pin_title.setAlignment(Qt.AlignCenter)
        pin_title.setStyleSheet("font-size: 20px; color: #fff;")
        overlay_layout.addWidget(pin_title)

        self.pin_display = QLineEdit(self.pin_overlay)
        self.pin_display.setAlignment(Qt.AlignCenter)
        self.pin_display.setEchoMode(QLineEdit.Password)
        self.pin_display.setReadOnly(True)
        self.pin_display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                color: #fff;
                background: #333;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        overlay_layout.addWidget(self.pin_display)

        keypad = QGridLayout()
        keypad.setSpacing(8)
        digits = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            'C', '0', '✓'
        ]
        for i, digit in enumerate(digits):
            btn = QPushButton(digit, self.pin_overlay)
            btn.setFixedSize(80, 60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: white;
                    font-size: 20px;
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)
            if digit == 'C':
                btn.clicked.connect(self._pin_clear)
            elif digit == '✓':
                btn.clicked.connect(self._pin_verify)
            else:
                btn.clicked.connect(lambda checked, d=digit: self._pin_digit(d))
            keypad.addWidget(btn, i // 3, i % 3)

        overlay_layout.addLayout(keypad)

    # ═══════════════════════════════════════════════════════
    # PUBLIC API (called by MainWindow)
    # ═══════════════════════════════════════════════════════

    def on_enter(self):
        """Reset everything when entering this screen."""
        self._selected_rack = None
        self._assigned_pairs = []
        self._update_ui()
        self.table_label.hide()
        self.table_grid.hide()
        self.pin_overlay.hide()
        self._inactivity_timer.start(INACTIVITY_TIMEOUT_MS)
        # Stub: update battery from ESP32 later
        self.battery_label.setText("🔋 85%")

    def on_exit(self):
        """Stop the inactivity timer when leaving."""
        self._inactivity_timer.stop()
        self.pin_overlay.hide()

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS
    # ═══════════════════════════════════════════════════════

    def _on_rack_selected(self, rack):
        """A rack button was tapped."""
        self._reset_inactivity()
        self._selected_rack = rack

        for i, btn in enumerate(self.rack_buttons):
            btn.setStyleSheet(self._rack_button_style(i + 1 == rack))

        self.table_label.show()
        self.table_grid.show()

        assigned_tables = [t for r, t in self._assigned_pairs]
        for t, btn in enumerate(self.table_buttons, 1):
            btn.setEnabled(t not in assigned_tables)
            btn.setStyleSheet(self._table_button_style(False))

    def _on_table_selected(self, table):
        """A table button was tapped — add the pair."""
        self._reset_inactivity()
        if self._selected_rack is None:
            return

        self._assigned_pairs.append((self._selected_rack, table))
        self._selected_rack = None

        for btn in self.rack_buttons:
            btn.setStyleSheet(self._rack_button_style(False))

        self.table_label.hide()
        self.table_grid.hide()
        self._update_ui()

    def _on_start_clicked(self):
        """Start delivery button tapped."""
        self._inactivity_timer.stop()
        self.start_delivery.emit()

    def _on_inactivity_timeout(self):
        """No interaction for too long — go back to idle."""
        self.assignment_cancelled.emit()

    def _on_gear_clicked(self):
        """Gear icon tapped — show PIN overlay."""
        self._pin_clear()
        self.pin_overlay.show()
        self.pin_overlay.raise_()
        self._inactivity_timer.stop()  # pause inactivity while entering PIN

    def _pin_digit(self, digit):
        """PIN keypad digit pressed."""
        current = self.pin_display.text()
        if len(current) < 6:
            self.pin_display.setText(current + digit)

    def _pin_clear(self):
        """Clear PIN entry."""
        self.pin_display.clear()

    def _pin_verify(self):
        """Check PIN and enter settings if correct."""
        if self.pin_display.text() == ADMIN_PIN:
            self.pin_overlay.hide()
            self._pin_clear()
            self.request_settings.emit()
        else:
            self.pin_display.setText("WRONG")
            QTimer.singleShot(800, self._pin_clear)

    # ═══════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ═══════════════════════════════════════════════════════

    def _reset_inactivity(self):
        """Restart the inactivity timer on any interaction."""
        self._inactivity_timer.stop()
        self._inactivity_timer.start(INACTIVITY_TIMEOUT_MS)

    def _update_ui(self):
        """Refresh the assigned list and start button state."""
        if self._assigned_pairs:
            lines = [f"Rack {r} → Table {t}" for r, t in self._assigned_pairs]
            self.assigned_list.setText("\n".join(lines))
            self.start_btn.setEnabled(True)
        else:
            self.assigned_list.setText("None yet")
            self.start_btn.setEnabled(False)

    def _rack_button_style(self, selected):
        """CSS for rack buttons."""
        if selected:
            return """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 10px;
                    border: 2px solid #5dade2;
                }
            """
        return """
            QPushButton {
                background-color: #333;
                color: #ccc;
                font-size: 16px;
                border-radius: 10px;
                border: 2px solid #555;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """

    def _table_button_style(self, selected):
        """CSS for table number buttons."""
        if selected:
            return """
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                }
            """
        return """
            QPushButton {
                background-color: #444;
                color: #ddd;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:pressed {
                background-color: #555;
            }
            QPushButton:disabled {
                background-color: #222;
                color: #555;
            }
        """
