"""
assignment_screen.py — Waiter selects racks and assigns tables.

Flow:
  1. Tap a rack card (Rack 1, 2, or 3)
  2. Table grid appears — tap a table number
  3. Pair appears in "Assigned" list
  4. Repeat for more racks, or tap "Start Delivery"

Features:
  - Inactivity timer: auto-return to idle after 25s of no interaction
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout, QScrollArea
)

from config import RACK_COUNT, TABLE_COUNT, INACTIVITY_TIMEOUT_MS


class AssignmentScreen(QWidget):
    """
    ┌─────────────────────────────────────────┐
    │  Select Rack        [Assigned List]     │
    │  [R1] [R2] [R3]     R1→T5  R3→T2       │
    │                                         │
    │  Select Table:      [Start Delivery]    │
    │  [1] [2] [3] [4]...                     │
    │  [5] [6] [7] [8]...                     │
    └─────────────────────────────────────────┘
    """

    start_delivery = pyqtSignal()           # "Start" button tapped
    assignment_cancelled = pyqtSignal()     # inactivity timeout

    def __init__(self, parent=None):
        super().__init__(parent)

        self._selected_rack = None
        self._assigned_pairs = []  # list of (rack, table)

        self._setup_ui()
        self._setup_inactivity_timer()

    def _setup_ui(self):
        """Build the assignment screen layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)

        # ═══════ LEFT PANEL: Rack + Table selection ═══════
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)

        # --- Rack selection ---
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

        # --- Table grid (hidden until rack selected) ---
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
        main_layout.addLayout(left_panel, stretch=2)

        # ═══════ RIGHT PANEL: Assigned list + Start button ═══════
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
        main_layout.addLayout(right_panel, stretch=1)

        self.setLayout(main_layout)

    def _setup_inactivity_timer(self):
        """Timer that returns to idle if waiter walks away."""
        self._inactivity_timer = QTimer(self)
        self._inactivity_timer.setSingleShot(True)
        self._inactivity_timer.timeout.connect(self._on_inactivity_timeout)

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
        self._inactivity_timer.start(INACTIVITY_TIMEOUT_MS)

    def on_exit(self):
        """Stop the inactivity timer when leaving."""
        self._inactivity_timer.stop()

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS
    # ═══════════════════════════════════════════════════════

    def _on_rack_selected(self, rack):
        """A rack button was tapped."""
        self._reset_inactivity()
        self._selected_rack = rack

        # Update rack button visuals
        for i, btn in enumerate(self.rack_buttons):
            btn.setStyleSheet(self._rack_button_style(i + 1 == rack))

        # Show table grid
        self.table_label.show()
        self.table_grid.show()

        # Disable already-assigned tables
        assigned_tables = [t for r, t in self._assigned_pairs]
        for t, btn in enumerate(self.table_buttons, 1):
            btn.setEnabled(t not in assigned_tables)
            btn.setStyleSheet(self._table_button_style(False))

    def _on_table_selected(self, table):
        """A table button was tapped — add the pair."""
        self._reset_inactivity()
        if self._selected_rack is None:
            return

        # Add to assignments
        self._assigned_pairs.append((self._selected_rack, table))

        # Clear rack selection (force re-select for next pair)
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
