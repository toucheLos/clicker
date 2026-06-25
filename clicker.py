# -*- coding: utf-8 -*-
"Aim trainer overlay - click dots on your screen like an FPS."

import sys
import random
import json
import os
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QSlider, QPushButton, QColorDialog,
    QComboBox, QCheckBox, QGroupBox, QGridLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QPixmap,
    QFont, QRadialGradient, QCursor, QLinearGradient,
)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clicker_config.json")
SCORES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")

DEFAULTS = {
    "color": "#ff3333",
    "outline_color": "#ffffff",
    "size": 30,
    "texture": "solid",
    "show_outline": True,
    "outline_width": 2,
    "overlay_opacity": 35,
}

TEXTURES = ["solid", "gradient", "bullseye", "crosshair", "glow"]
CHALLENGE_TARGETS = [10, 25, 50, 100]

STYLE = """
QWidget {
    background: #11111b;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
}
QLabel { background: transparent; }

/* Tabs */
QTabWidget::pane {
    background: #181825;
    border: none;
    border-top: 2px solid #313244;
}
QTabBar { background: transparent; }
QTabBar::tab {
    background: transparent;
    color: #6c7086;
    padding: 10px 20px;
    border: none;
    border-bottom: 3px solid transparent;
    font-weight: bold;
    font-size: 13px;
}
QTabBar::tab:hover { color: #a6adc8; }
QTabBar::tab:selected {
    color: #cba6f7;
    border-bottom: 3px solid #cba6f7;
}

/* Group boxes */
QGroupBox {
    background: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 10px 12px;
    font-weight: bold;
    font-size: 12px;
    color: #a6adc8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #bac2de;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 4px;
    background: #313244;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 14px; height: 14px; margin: -5px 0;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.4, fy:0.4,
        stop:0 #d4bfff, stop:1 #cba6f7);
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cba6f7, stop:1 #b4befe);
    border-radius: 2px;
}

/* Buttons */
QPushButton {
    background: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 18px;
    color: #cdd6f4;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background: #45475a;
    border-color: #585b70;
}
QPushButton:pressed {
    background: #585b70;
}

/* Combos */
QComboBox {
    background: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 6px 14px;
    color: #cdd6f4;
    min-height: 20px;
}
QComboBox:hover { border-color: #585b70; }
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    selection-background-color: #45475a;
    padding: 4px;
}

/* Checkboxes */
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 4px;
    border: 2px solid #45475a; background: #1e1e2e;
}
QCheckBox::indicator:hover { border-color: #585b70; }
QCheckBox::indicator:checked {
    background: #cba6f7; border-color: #cba6f7;
}

/* Table */
QTableWidget {
    background: #1e1e2e;
    color: #cdd6f4;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 8px;
    font-size: 12px;
}
QTableWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #313244;
}
QTableWidget::item:alternate { background: #181825; }
QHeaderView::section {
    background: #313244;
    color: #a6adc8;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #181825; width: 8px; border: none;
}
QScrollBar::handle:vertical {
    background: #45475a; border-radius: 4px; min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        for k, v in DEFAULTS.items():
            cfg.setdefault(k, v)
        return cfg
    return dict(DEFAULTS)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def load_scores():
    if os.path.exists(SCORES_PATH):
        with open(SCORES_PATH) as f:
            return json.load(f)
    return {}


def save_scores(scores):
    with open(SCORES_PATH, "w") as f:
        json.dump(scores, f, indent=2)


def add_score(target, elapsed, hits, misses):
    scores = load_scores()
    key = str(target)
    if key not in scores:
        scores[key] = []
    acc = hits / (hits + misses) * 100 if (hits + misses) > 0 else 0
    scores[key].append({
        "time": round(elapsed, 3),
        "hits": hits,
        "misses": misses,
        "accuracy": round(acc, 1),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    scores[key].sort(key=lambda s: s["time"])
    scores[key] = scores[key][:10]
    save_scores(scores)


def format_time(seconds):
    m = int(seconds) // 60
    s = seconds - m * 60
    if m > 0:
        return f"{m}:{s:05.2f}"
    return f"{s:.2f}s"


class DotPreview(QWidget):
    """Live preview of the current dot style."""
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.setFixedSize(120, 120)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)

    def _tick(self):
        self._phase = (self._phase + 1) % 60
        if self.overlay.texture == "glow":
            self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#11111b"))

        color = QColor(self.overlay.dot_color)
        r = min(self.overlay.dot_size, 90) // 2
        cx, cy = 60, 60
        center = QPoint(cx, cy)

        if self.overlay.texture == "solid":
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(center, r, r)
        elif self.overlay.texture == "gradient":
            grad = QRadialGradient(cx - r * 0.3, cy - r * 0.3, r)
            grad.setColorAt(0.0, QColor(color).lighter(140))
            grad.setColorAt(0.7, color)
            grad.setColorAt(1.0, color.darker(130))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(center, r, r)
        elif self.overlay.texture == "bullseye":
            for i in range(3, 0, -1):
                ring_r = int(r * i / 3)
                p.setBrush(QBrush(color if i % 2 == 1 else QColor(255, 255, 255, 220)))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(center, ring_r, ring_r)
        elif self.overlay.texture == "crosshair":
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(center, r, r)
            p.setPen(QPen(QColor(255, 255, 255, 200), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(cx - r, cy, cx + r, cy)
            p.drawLine(cx, cy - r, cx, cy + r)
            p.drawEllipse(center, r // 3, r // 3)
        elif self.overlay.texture == "glow":
            pulse = abs(self._phase - 30) / 30.0
            glow_r = int(r * (1.3 + 0.3 * pulse))
            gc = QColor(color)
            gc.setAlpha(int(60 + 30 * pulse))
            gg = QRadialGradient(cx, cy, glow_r)
            gg.setColorAt(0.0, gc)
            gg.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            p.setBrush(QBrush(gg))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(center, glow_r, glow_r)
            p.setBrush(QBrush(color))
            p.drawEllipse(center, r, r)

        if self.overlay.show_outline and self.overlay.texture != "bullseye":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(self.overlay.outline_color), self.overlay.outline_width))
            p.drawEllipse(center, r, r)

        p.end()


def _color_swatch(color_str, size=28):
    """Round color swatch label."""
    lbl = QLabel()
    lbl.setFixedSize(size, size)
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color_str))
    p.setPen(QPen(QColor("#585b70"), 2))
    p.drawRoundedRect(2, 2, size - 4, size - 4, 6, 6)
    p.end()
    lbl.setPixmap(pm)
    return lbl


def _update_swatch(lbl, color_str, size=28):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color_str))
    p.setPen(QPen(QColor("#585b70"), 2))
    p.drawRoundedRect(2, 2, size - 4, size - 4, 6, 6)
    p.end()
    lbl.setPixmap(pm)


class SettingsPanel(QWidget):
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.setWindowTitle("Aim Trainer")
        self.setFixedSize(420, 660)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1e2e, stop:0.5 #2a2040, stop:1 #1e1e2e);
                border-bottom: 1px solid #313244;
            }
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)

        # Crosshair icon
        icon_lbl = QLabel()
        icon_pm = QPixmap(36, 36)
        icon_pm.fill(Qt.GlobalColor.transparent)
        ip = QPainter(icon_pm)
        ip.setRenderHint(QPainter.RenderHint.Antialiasing)
        ip.setPen(QPen(QColor("#cba6f7"), 2))
        ip.drawEllipse(6, 6, 24, 24)
        ip.drawLine(18, 2, 18, 34)
        ip.drawLine(2, 18, 34, 18)
        ip.setBrush(QColor("#f38ba8"))
        ip.setPen(Qt.PenStyle.NoPen)
        ip.drawEllipse(14, 14, 8, 8)
        ip.end()
        icon_lbl.setPixmap(icon_pm)
        hl.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("AIM TRAINER")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4; letter-spacing: 3px;")
        subtitle = QLabel("click fast, click precise")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #6c7086;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        hl.addLayout(title_col)
        hl.addStretch()

        root.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self.tabs.addTab(self._build_play_tab(), "PLAY")
        self.tabs.addTab(self._build_settings_tab(), "SETTINGS")
        self.tabs.addTab(self._build_scores_tab(), "SCORES")

    # ── Play Tab ────────────────────────────────────────

    def _build_play_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        mode_group = QGroupBox("Game Mode")
        mg = QVBoxLayout(mode_group)
        mg.setSpacing(10)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Free Play", "Challenge"])
        self.mode_combo.currentTextChanged.connect(self._mode_changed)
        mg.addWidget(self.mode_combo)

        target_row = QHBoxLayout()
        self.target_row_label = QLabel("Target hits:")
        self.target_row_label.setStyleSheet("color: #a6adc8;")
        self.target_combo = QComboBox()
        self.target_combo.addItems([str(t) for t in CHALLENGE_TARGETS])
        self.target_combo.setCurrentText("25")
        target_row.addWidget(self.target_row_label)
        target_row.addWidget(self.target_combo)
        target_row.addStretch()
        mg.addLayout(target_row)

        self.target_row_label.hide()
        self.target_combo.hide()

        layout.addWidget(mode_group)

        # Stats card
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        sc_layout = QVBoxLayout(stats_card)
        sc_layout.setSpacing(4)
        stats_title = QLabel("SESSION STATS")
        stats_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        stats_title.setStyleSheet("color: #6c7086; letter-spacing: 2px; border: none;")
        stats_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc_layout.addWidget(stats_title)
        self.stats_label = QLabel("Hits: 0  Misses: 0  Accuracy: --")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setFont(QFont("Consolas", 12))
        self.stats_label.setStyleSheet("color: #cdd6f4; border: none;")
        sc_layout.addWidget(self.stats_label)
        layout.addWidget(stats_card)

        # Result banner
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet("""
            QFrame {
                background: #1e1e2e;
                border: 1px solid #a6e3a1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        rf_layout = QVBoxLayout(self.result_frame)
        rf_layout.setSpacing(2)
        self.result_title = QLabel()
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.result_title.setStyleSheet("color: #a6e3a1; border: none;")
        self.result_detail = QLabel()
        self.result_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_detail.setFont(QFont("Consolas", 12))
        self.result_detail.setStyleSheet("color: #cdd6f4; border: none;")
        rf_layout.addWidget(self.result_title)
        rf_layout.addWidget(self.result_detail)
        self.result_frame.hide()
        layout.addWidget(self.result_frame)

        layout.addStretch()

        # Buttons
        self.start_btn = QPushButton("START")
        self.start_btn.setFixedHeight(44)
        self.start_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a6e3a1, stop:1 #94e2d5);
                color: #1e1e2e; border: none; border-radius: 10px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #94e2d5, stop:1 #89dceb);
            }
            QPushButton:pressed { background: #74c7ec; }
        """)
        self.start_btn.clicked.connect(self._start_clicked)
        layout.addWidget(self.start_btn)

        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #f38ba8;
                border: 1px solid #45475a; border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover { background: #313244; border-color: #f38ba8; }
        """)
        quit_btn.clicked.connect(QApplication.quit)
        layout.addWidget(quit_btn)

        return w

    # ── Settings Tab ────────────────────────────────────

    def _build_settings_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Preview + Circle settings side by side
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.dot_preview = DotPreview(self.overlay)
        self.dot_preview.setStyleSheet("""
            background: #11111b;
            border: 1px solid #313244;
            border-radius: 10px;
        """)
        top_row.addWidget(self.dot_preview)

        circle_group = QGroupBox("Circle")
        cg = QGridLayout(circle_group)
        cg.setSpacing(8)

        cg.addWidget(QLabel("Size"), 0, 0)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 120)
        self.size_slider.setValue(self.overlay.dot_size)
        self.size_slider.valueChanged.connect(self._size_changed)
        self.size_label = QLabel(str(self.overlay.dot_size))
        self.size_label.setFixedWidth(28)
        self.size_label.setStyleSheet("color: #cba6f7; font-weight: bold;")
        cg.addWidget(self.size_slider, 0, 1)
        cg.addWidget(self.size_label, 0, 2)

        cg.addWidget(QLabel("Style"), 1, 0)
        self.texture_combo = QComboBox()
        self.texture_combo.addItems(TEXTURES)
        self.texture_combo.setCurrentText(self.overlay.texture)
        self.texture_combo.currentTextChanged.connect(self._texture_changed)
        cg.addWidget(self.texture_combo, 1, 1, 1, 2)

        cg.addWidget(QLabel("Color"), 2, 0)
        self.color_preview = _color_swatch(self.overlay.dot_color)
        color_btn = QPushButton("Pick")
        color_btn.setFixedWidth(56)
        color_btn.clicked.connect(self._pick_color)
        cg.addWidget(self.color_preview, 2, 1, Qt.AlignmentFlag.AlignLeft)
        cg.addWidget(color_btn, 2, 2)

        top_row.addWidget(circle_group, 1)
        layout.addLayout(top_row)

        # Outline
        outline_group = QGroupBox("Outline")
        og = QGridLayout(outline_group)
        og.setSpacing(8)

        self.outline_check = QCheckBox("Show outline")
        self.outline_check.setChecked(self.overlay.show_outline)
        self.outline_check.toggled.connect(self._outline_toggled)
        og.addWidget(self.outline_check, 0, 0, 1, 3)

        og.addWidget(QLabel("Width"), 1, 0)
        self.outline_slider = QSlider(Qt.Orientation.Horizontal)
        self.outline_slider.setRange(1, 8)
        self.outline_slider.setValue(self.overlay.outline_width)
        self.outline_slider.valueChanged.connect(self._outline_width_changed)
        self.outline_w_label = QLabel(str(self.overlay.outline_width))
        self.outline_w_label.setFixedWidth(28)
        self.outline_w_label.setStyleSheet("color: #cba6f7; font-weight: bold;")
        og.addWidget(self.outline_slider, 1, 1)
        og.addWidget(self.outline_w_label, 1, 2)

        og.addWidget(QLabel("Color"), 2, 0)
        self.outline_color_preview = _color_swatch(self.overlay.outline_color)
        outline_color_btn = QPushButton("Pick")
        outline_color_btn.setFixedWidth(56)
        outline_color_btn.clicked.connect(self._pick_outline_color)
        og.addWidget(self.outline_color_preview, 2, 1, Qt.AlignmentFlag.AlignLeft)
        og.addWidget(outline_color_btn, 2, 2)

        layout.addWidget(outline_group)

        # Overlay
        overlay_group = QGroupBox("Overlay")
        ovg = QGridLayout(overlay_group)
        ovg.setSpacing(8)

        ovg.addWidget(QLabel("Dim"), 0, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 120)
        self.opacity_slider.setValue(self.overlay.overlay_opacity)
        self.opacity_slider.valueChanged.connect(self._opacity_changed)
        self.opacity_label = QLabel(str(self.overlay.overlay_opacity))
        self.opacity_label.setFixedWidth(28)
        self.opacity_label.setStyleSheet("color: #cba6f7; font-weight: bold;")
        ovg.addWidget(self.opacity_slider, 0, 1)
        ovg.addWidget(self.opacity_label, 0, 2)

        layout.addWidget(overlay_group)
        layout.addStretch()

        return w

    # ── Scores Tab ──────────────────────────────────────

    def _build_scores_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        filter_row = QHBoxLayout()
        fl = QLabel("Target:")
        fl.setStyleSheet("color: #a6adc8;")
        filter_row.addWidget(fl)
        self.scores_filter = QComboBox()
        self.scores_filter.addItems(["All"] + [str(t) for t in CHALLENGE_TARGETS])
        self.scores_filter.currentTextChanged.connect(self._refresh_scores)
        filter_row.addWidget(self.scores_filter)
        filter_row.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #f38ba8;
                border: 1px solid #45475a; border-radius: 6px;
                padding: 4px 12px; font-size: 11px;
            }
            QPushButton:hover { background: #313244; border-color: #f38ba8; }
        """)
        clear_btn.clicked.connect(self._clear_scores)
        filter_row.addWidget(clear_btn)
        layout.addLayout(filter_row)

        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(5)
        self.scores_table.setHorizontalHeaderLabels(["", "TIME", "ACC", "TARGET", "DATE"])
        self.scores_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.scores_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.scores_table.setColumnWidth(0, 40)
        self.scores_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.scores_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.scores_table.verticalHeader().hide()
        self.scores_table.setAlternatingRowColors(True)
        self.scores_table.setShowGrid(False)
        layout.addWidget(self.scores_table)

        return w

    def _refresh_scores(self):
        scores = load_scores()
        filt = self.scores_filter.currentText()

        rows = []
        for target_key, entries in scores.items():
            if filt != "All" and target_key != filt:
                continue
            for entry in entries:
                rows.append((entry["time"], entry.get("accuracy", 0),
                             int(target_key), entry.get("date", "")))

        rows.sort(key=lambda r: r[0])
        self.scores_table.setRowCount(len(rows))
        medal_colors = ["#f9e2af", "#b4befe", "#fab387"]
        for i, (t, acc, target, date) in enumerate(rows):
            if i < 3:
                rank = ["1st", "2nd", "3rd"][i]
                color = medal_colors[i]
            else:
                rank = str(i + 1)
                color = "#6c7086"

            items = [rank, format_time(t), f"{acc:.0f}%", str(target), date]
            for c, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(color if (i < 3 and c == 0) else "#cdd6f4"))
                if i < 3 and c == 1:
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
                self.scores_table.setItem(i, c, item)

    def _clear_scores(self):
        save_scores({})
        self._refresh_scores()

    # ── Callbacks ───────────────────────────────────────

    def _mode_changed(self, text):
        is_challenge = text == "Challenge"
        self.target_row_label.setVisible(is_challenge)
        self.target_combo.setVisible(is_challenge)

    def _start_clicked(self):
        mode = self.mode_combo.currentText()
        if mode == "Challenge":
            target = int(self.target_combo.currentText())
            self.overlay.start_challenge(target)
        else:
            self.overlay.start_freeplay()
        self.result_frame.hide()

    def show_result(self, elapsed, hits, misses, target, is_record):
        acc = hits / (hits + misses) * 100 if (hits + misses) > 0 else 0
        if is_record:
            self.result_title.setText("NEW RECORD!")
            self.result_title.setStyleSheet("color: #f9e2af; border: none;")
            self.result_frame.setStyleSheet("""
                QFrame {
                    background: #1e1e2e;
                    border: 1px solid #f9e2af;
                    border-radius: 10px; padding: 10px;
                }
            """)
        else:
            self.result_title.setText("CHALLENGE COMPLETE")
            self.result_title.setStyleSheet("color: #a6e3a1; border: none;")
            self.result_frame.setStyleSheet("""
                QFrame {
                    background: #1e1e2e;
                    border: 1px solid #a6e3a1;
                    border-radius: 10px; padding: 10px;
                }
            """)
        self.result_detail.setText(
            f"{target} hits in {format_time(elapsed)}   |   {acc:.1f}% accuracy"
        )
        self.result_frame.show()

    def _size_changed(self, val):
        self.overlay.dot_size = val
        self.size_label.setText(str(val))
        self.overlay.update()
        self.dot_preview.update()
        self.overlay._save()

    def _texture_changed(self, txt):
        self.overlay.texture = txt
        self.overlay.update()
        self.dot_preview.update()
        self.overlay._save()

    def _pick_color(self):
        c = QColorDialog.getColor(QColor(self.overlay.dot_color), self, "Fill color")
        if c.isValid():
            self.overlay.dot_color = c.name()
            _update_swatch(self.color_preview, c.name())
            self.overlay.update()
            self.dot_preview.update()
            self.overlay._save()

    def _pick_outline_color(self):
        c = QColorDialog.getColor(QColor(self.overlay.outline_color), self, "Outline color")
        if c.isValid():
            self.overlay.outline_color = c.name()
            _update_swatch(self.outline_color_preview, c.name())
            self.overlay.update()
            self.dot_preview.update()
            self.overlay._save()

    def _outline_toggled(self, on):
        self.overlay.show_outline = on
        self.overlay.update()
        self.dot_preview.update()
        self.overlay._save()

    def _outline_width_changed(self, val):
        self.overlay.outline_width = val
        self.outline_w_label.setText(str(val))
        self.overlay.update()
        self.dot_preview.update()
        self.overlay._save()

    def _opacity_changed(self, val):
        self.overlay.overlay_opacity = val
        self.opacity_label.setText(str(val))
        self.overlay.update()
        self.overlay._save()

    def update_stats(self, hits, misses):
        if hits + misses > 0:
            acc = hits / (hits + misses) * 100
            self.stats_label.setText(f"Hits: {hits}  Misses: {misses}  Accuracy: {acc:.1f}%")
        else:
            self.stats_label.setText("Hits: 0  Misses: 0  Accuracy: --")

    def keyPressEvent(self, ev):
        if ev.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._start_clicked()
        else:
            super().keyPressEvent(ev)

    def closeEvent(self, ev):
        QApplication.quit()


class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        cfg = load_config()
        self.dot_color = cfg["color"]
        self.outline_color = cfg["outline_color"]
        self.dot_size = cfg["size"]
        self.texture = cfg["texture"]
        self.show_outline = cfg["show_outline"]
        self.outline_width = cfg["outline_width"]
        self.overlay_opacity = cfg["overlay_opacity"]

        self.hits = 0
        self.misses = 0
        self.dot_pos = QPoint(0, 0)
        self._active = False
        self._pulse_phase = 0

        self.mode = "free"
        self.target_hits = 0
        self._start_time = 0.0
        self._elapsed = 0.0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self.settings = SettingsPanel(self)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_tick)
        self._pulse_timer.start(30)

    def start_freeplay(self):
        self.mode = "free"
        self.target_hits = 0
        self.hits = 0
        self.misses = 0
        self._show_overlay()

    def start_challenge(self, target):
        self.mode = "challenge"
        self.target_hits = target
        self.hits = 0
        self.misses = 0
        self._start_time = time.monotonic()
        self._elapsed = 0.0
        self._show_overlay()

    def _show_overlay(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self._respawn_dot()
        self._active = True
        self.settings.hide()
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def _open_settings(self):
        self._active = False
        self.hide()
        self.settings.update_stats(self.hits, self.misses)
        self.settings.show()
        self.settings.raise_()
        self.settings.activateWindow()

    def show_overlay(self):
        self._show_overlay()

    def _respawn_dot(self):
        screen = self.geometry()
        margin = self.dot_size + 20
        x = random.randint(margin, screen.width() - margin)
        y = random.randint(margin, screen.height() - margin)
        self.dot_pos = QPoint(x, y)
        self.update()

    def _pulse_tick(self):
        self._pulse_phase = (self._pulse_phase + 1) % 60
        if self._active:
            if self.mode == "challenge":
                self._elapsed = time.monotonic() - self._start_time
            if self.texture == "glow" or self.mode == "challenge":
                self.update()

    def _save(self):
        save_config({
            "color": self.dot_color,
            "outline_color": self.outline_color,
            "size": self.dot_size,
            "texture": self.texture,
            "show_outline": self.show_outline,
            "outline_width": self.outline_width,
            "overlay_opacity": self.overlay_opacity,
        })

    def _complete_challenge(self):
        self._elapsed = time.monotonic() - self._start_time
        self._active = False
        self.hide()

        scores_before = load_scores()
        key = str(self.target_hits)
        best_before = scores_before.get(key, [{}])[0].get("time", float("inf"))

        add_score(self.target_hits, self._elapsed, self.hits, self.misses)
        is_record = self._elapsed < best_before

        self.settings.update_stats(self.hits, self.misses)
        self.settings.show_result(self._elapsed, self.hits, self.misses,
                                  self.target_hits, is_record)
        self.settings._refresh_scores()
        self.settings.tabs.setCurrentIndex(0)
        self.settings.show()
        self.settings.raise_()
        self.settings.activateWindow()

    def _draw_dot(self, p):
        color = QColor(self.dot_color)
        r = self.dot_size // 2
        cx, cy = self.dot_pos.x(), self.dot_pos.y()

        if self.texture == "solid":
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(self.dot_pos, r, r)
        elif self.texture == "gradient":
            grad = QRadialGradient(cx - r * 0.3, cy - r * 0.3, r)
            grad.setColorAt(0.0, QColor(color).lighter(140))
            grad.setColorAt(0.7, color)
            grad.setColorAt(1.0, color.darker(130))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(self.dot_pos, r, r)
        elif self.texture == "bullseye":
            for i in range(3, 0, -1):
                ring_r = int(r * i / 3)
                p.setBrush(QBrush(color if i % 2 == 1 else QColor(255, 255, 255, 220)))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(self.dot_pos, ring_r, ring_r)
        elif self.texture == "crosshair":
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(self.dot_pos, r, r)
            p.setPen(QPen(QColor(255, 255, 255, 200), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(cx - r, cy, cx + r, cy)
            p.drawLine(cx, cy - r, cx, cy + r)
            p.drawEllipse(self.dot_pos, r // 3, r // 3)
        elif self.texture == "glow":
            pulse = abs(self._pulse_phase - 30) / 30.0
            glow_r = int(r * (1.3 + 0.3 * pulse))
            glow_color = QColor(color)
            glow_color.setAlpha(int(60 + 30 * pulse))
            glow_grad = QRadialGradient(cx, cy, glow_r)
            glow_grad.setColorAt(0.0, glow_color)
            glow_grad.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            p.setBrush(QBrush(glow_grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(self.dot_pos, glow_r, glow_r)
            p.setBrush(QBrush(color))
            p.drawEllipse(self.dot_pos, r, r)

        if self.show_outline and self.texture != "bullseye":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(self.outline_color), self.outline_width))
            p.drawEllipse(self.dot_pos, r, r)

    def paintEvent(self, ev):
        if not self._active:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.fillRect(self.rect(), QColor(0, 0, 0, self.overlay_opacity))
        self._draw_dot(p)

        def hud_text(x, y, text, font_size=14, bold=True, color_hex="#ffffff", alpha=200):
            weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
            p.setFont(QFont("Consolas", font_size, weight))
            p.setPen(QPen(QColor(0, 0, 0, 140), 1))
            p.drawText(x + 2, y + 2, text)
            c = QColor(color_hex)
            c.setAlpha(alpha)
            p.setPen(QPen(c, 1))
            p.drawText(x, y, text)

        hud_text(20, 35, self._hud_line())
        hud_text(20, 55, "Esc = settings", 10, False, "#ffffff", 100)

        if self.mode == "challenge":
            timer_str = format_time(self._elapsed)
            progress = f"{self.hits}/{self.target_hits}"
            sw = self.geometry().width()
            hud_text(sw // 2 - 60, 40, timer_str, 20, True, "#f9e2af")
            hud_text(sw // 2 - 30, 65, progress, 14, True, "#cdd6f4")

        p.end()

    def _hud_line(self):
        total = self.hits + self.misses
        if total > 0:
            acc = self.hits / total * 100
            return f"Hits: {self.hits}  Misses: {self.misses}  Acc: {acc:.0f}%"
        return f"Hits: {self.hits}  Misses: {self.misses}"

    def mousePressEvent(self, ev):
        if not self._active:
            return
        if ev.button() == Qt.MouseButton.LeftButton:
            dx = ev.position().x() - self.dot_pos.x()
            dy = ev.position().y() - self.dot_pos.y()
            r = self.dot_size / 2
            if dx * dx + dy * dy <= r * r:
                self.hits += 1
                if self.mode == "challenge" and self.hits >= self.target_hits:
                    self._complete_challenge()
                    return
                self._respawn_dot()
            else:
                self.misses += 1
                self.update()
            self.settings.update_stats(self.hits, self.misses)

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key.Key_Escape:
            self._open_settings()
        else:
            super().keyPressEvent(ev)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    overlay = Overlay()
    QTimer.singleShot(100, overlay.start_freeplay)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
