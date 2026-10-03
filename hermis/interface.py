import os
import re
import time
from collections import deque
from pathlib import Path

from PyQt6.QtCore import (
    QEasingCurve,
    QMutex,
    QMutexLocker,
    QObject,
    QPropertyAnimation,
    Qt,
    QThread,
    QTimer,
    QUrl,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPalette, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import main

_WORD_REGEX = re.compile(r"\b\w{4,}\b", re.IGNORECASE)

# ── Dark palette (Material-inspired) ────────────────────────────────────────


def _apply_modern_theme(app: QApplication, dark: bool = False):
    """Modern techno-minimal visual system: soft glass surfaces + vivid accents."""
    if dark:
        bg = "#12161F"
        surface = "#1A202B"
        surface_2 = "#171C25"
        border = "#27303D"
        text = "#F7F9FC"
        muted = "#D3DAE6"
        input_bg = "#151A22"
        card_file = "#1B3655"
        card_options = "#34285A"
        card_ai = "#153E39"
        card_output = "#493617"
        card_run = "#49243D"
        accent = "#9285FF"
        accent_2 = "#3DD9D1"
        accent_hover = "#AAA0FF"
        card_file_end = "#223142"
        card_options_end = "#302C40"
        card_ai_end = "#203632"
        card_output_end = "#3B3224"
        card_run_end = "#3B2B36"
        tone_border = "rgba(255,255,255,28)"
    else:
        bg = "#EEF2F7"
        surface = "#FFFFFF"
        surface_2 = "#FAFBFD"
        border = "#DCE3EC"
        text = "#253146"
        muted = "#536277"
        input_bg = "#FFFFFF"
        card_file = "#D4EAFF"
        card_options = "#E5D9FF"
        card_ai = "#D0F3E8"
        card_output = "#FFE5B2"
        card_run = "#F3D6E7"
        accent = "#6D5EF5"
        accent_2 = "#17BEBB"
        accent_hover = "#7F71FF"
        card_file_end = "#BBDFFF"
        card_options_end = "#D7C9F5"
        card_ai_end = "#B9E8D8"
        card_output_end = "#F7D38F"
        card_run_end = "#EFC0D7"
        tone_border = "rgba(255,255,255,150)"

    app.setStyleSheet(f"""
        QApplication {{
            background: {bg};
            color: {text};
        }}

        QWidget {{
            font-family: "Adwaita Sans", "Cantarell", "Noto Sans", "Segoe UI", sans-serif;
            font-size: 10pt;
            color: {text};
            font-weight: 560;
        }}

        QMainWindow, QWidget#root {{
            background: {bg};
        }}

        QLabel#brand {{
            color: {text};
            font-size: 20pt;
            font-weight: 850;
            letter-spacing: 1.2px;
        }}

        QLabel#micro {{
            color: {muted};
            font-size: 8pt;
            font-weight: 800;
            letter-spacing: 1.4px;
        }}

        QLabel#heroSubtitle {{
            color: {muted};
            font-size: 9.5pt;
        }}

        QLabel#cardTitle {{
            color: {text};
            font-size: 11.5pt;
            font-weight: 800;
        }}

        QLabel#cardHint, QLabel#pathLabel {{
            color: {muted};
            font-size: 8.8pt;
        }}

        QLabel#cardGlyph {{
            background: transparent;
            padding: 0;
        }}

        QLabel#statusPill {{
            background: {surface};
            color: {accent};
            border: 1px solid {border};
            border-radius: 15px;
            padding: 6px 11px;
            font-size: 8.5pt;
            font-weight: 800;
            letter-spacing: 0.8px;
        }}

        QFrame#techLine {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {accent},
                stop:0.50 {accent_2},
                stop:1 {accent}
            );
            border: 0;
            border-radius: 2px;
        }}

        QFrame#card {{
            background: {surface};
            border: 1px solid {tone_border};
            border-radius: 24px;
        }}

        QFrame#card[cardTone="file"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_file}, stop:1 {card_file_end});
            border-color: {tone_border};
        }}
        QFrame#card[cardTone="options"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_options}, stop:1 {card_options_end});
            border-color: {tone_border};
        }}
        QFrame#card[cardTone="ai"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_ai}, stop:1 {card_ai_end});
            border-color: {tone_border};
        }}
        QFrame#card[cardTone="output"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_output}, stop:1 {card_output_end});
            border-color: {tone_border};
        }}
        QFrame#card[cardTone="run"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_run}, stop:1 {card_run_end});
            border-color: {tone_border};
        }}

        QPushButton {{
            background: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 9px 14px;
            min-height: 18px;
            font-weight: 700;
        }}

        QPushButton:hover {{
            border-color: {accent};
            background: {input_bg};
        }}

        QPushButton:pressed {{
            background: {border};
        }}

        QPushButton#primaryButton {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {accent},
                stop:1 {accent_hover}
            );
            border: 0;
            color: white;
            border-radius: 15px;
            padding: 12px 18px;
            font-size: 10.5pt;
            font-weight: 850;
        }}

        QPushButton#primaryButton:hover {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {accent_hover},
                stop:1 {accent}
            );
        }}

        QPushButton#primaryButton:disabled {{
            background: {border};
            color: {muted};
        }}

        QPushButton#smallButton {{
            padding: 7px 11px;
            border-radius: 10px;
            font-size: 8.6pt;
        }}

        QComboBox, QLineEdit {{
            background: {input_bg};
            color: {text};
            border: 1px solid {border};
            border-radius: 11px;
            padding: 9px 11px;
            min-height: 18px;
        }}

        QComboBox:hover, QLineEdit:hover {{
            border-color: {accent};
        }}

        QComboBox::drop-down {{
            border: 0;
            width: 28px;
        }}

        QComboBox QAbstractItemView {{
            background: {surface};
            color: {text};
            border: 1px solid {border};
            selection-background-color: {accent};
            selection-color: white;
            padding: 5px;
        }}

        QCheckBox {{
            spacing: 8px;
            color: {text};
            font-weight: 650;
        }}

        QCheckBox::indicator {{
            width: 17px;
            height: 17px;
            border-radius: 5px;
            border: 1px solid {border};
            background: {input_bg};
        }}

        QCheckBox::indicator:checked {{
            background: {accent};
            border-color: {accent};
        }}

        QProgressBar {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 9px;
            text-align: center;
            color: {text};
            min-height: 16px;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {accent},
                stop:0.55 {accent_2},
                stop:1 #F06CB5
            );
            border-radius: 8px;
        }}

        QTextEdit {{
            background: {surface_2};
            color: {text};
            border: 1px solid {border};
            border-radius: 15px;
            padding: 10px;
            selection-background-color: {accent};
            selection-color: white;
        }}

        QScrollArea {{
            background: transparent;
            border: 0;
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 4px;
        }}

        QScrollBar::handle:vertical {{
            background: {border};
            border-radius: 4px;
            min-height: 35px;
        }}

        QToolTip {{
            background: {text};
            color: {surface};
            border: 0;
            border-radius: 8px;
            padding: 7px;
        }}
    """)

    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window, QColor(bg))
    pal.setColor(QPalette.ColorRole.Base, QColor(input_bg))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(surface))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(text))
    pal.setColor(QPalette.ColorRole.Text, QColor(text))
    pal.setColor(QPalette.ColorRole.Button, QColor(surface))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(text))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(accent))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(muted))
    app.setPalette(pal)
    app.setProperty("hermis_dark", dark)


def _decorate_card(card: QFrame, glyph: str, accent: str):
    """Soft neumorphic depth + a low-opacity corner glyph."""
    shadow = QGraphicsDropShadowEffect(card)
    dark = bool(QApplication.instance().property("hermis_dark"))
    shadow.setBlurRadius(26 if dark else 24)
    shadow.setOffset(4, 7)
    shadow.setColor(QColor("#00000070" if dark else "#00000028"))
    card.setGraphicsEffect(shadow)

    layout = card.layout()
    if layout is None:
        return

    layout.addStretch(1)
    glyph_label = QLabel(glyph, card)
    glyph_label.setObjectName("cardGlyph")
    glyph_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
    glyph_label.setFont(QFont("Adwaita Sans", 35, QFont.Weight.Light))
    glyph_label.setStyleSheet(f"QLabel#cardGlyph {{ color: {accent}5C; background: transparent; }}")
    glyph_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    layout.addWidget(glyph_label, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)


def _add_pulse(widget: QWidget, start: float = 0.55, end: float = 1.0):
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(start)
    widget.setGraphicsEffect(effect)

    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(1400)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    anim.setLoopCount(-1)
    anim.start()
    widget._pulse_animation = anim
    widget._pulse_effect = effect


# ═
#  QThread Workers  –  off-loaded heavy computation
# ══════════════════════════════════════════════════════════════════════════


class InitWorker(QObject):
    """Loads OCR resources in background."""

    finished = pyqtSignal()

    @pyqtSlot()
    def run(self):
        # Não inicializa EasyOCR no startup: o modelo só é necessário para PDFs
        # sem texto extraível. Isso reduz custo de inicialização e RAM/VRAM ociosos.
        self.finished.emit()


class AnalysisWorker(QObject):
    """Runs main.main() in a QThread, emitting signals back to the GUI."""

    log = pyqtSignal(str)
    progress = pyqtSignal(int, int, float, float, int)  # done,total,elapsed,dur,chars
    stream_tok = pyqtSignal(int, str)  # chunk_idx, token
    stream_init = pyqtSignal(int)  # total_chunks
    block_done = pyqtSignal(int)  # chunk_idx
    finished = pyqtSignal(object)  # result_path | None

    def __init__(self, params: dict):
        super().__init__()
        self._params = params

    @pyqtSlot()
    def run(self):
        p = self._params
        p["update_log_callback"] = self.log.emit
        p["init_stream_callback"] = self.stream_init.emit
        p["update_progress_callback"] = self.progress.emit
        p["update_stream_callback"] = self.stream_tok.emit
        p["finish_block_callback"] = self.block_done.emit
        result = main.main(**p)
        self.finished.emit(result)


# ══════════════════════════════════════════════════════════════════════════
#  Streaming Window  –  real-time token monitor
# ══════════════════════════════════════════════════════════════════════════


class StreamingWindow(QWidget):
    """Janela de streaming com flush via QTimer – zero bloqueio da thread principal."""

    def __init__(self, total_parts: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hermis • Processamento")
        self.resize(980, 760)

        self._total = total_parts
        self._buffers: dict[int, deque] = {}
        self._mutex = QMutex()

        # ── Layout ──
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(10)

        self._frames: dict[int, QFrame] = {}
        self._labels: dict[int, QLabel] = {}
        self._text_edits: dict[int, QTextEdit] = {}

        for i in range(total_parts):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet(
                "QFrame { background: palette(base); border: 1px solid palette(mid); border-radius: 16px; }"
            )
            fl = QVBoxLayout(frame)

            lbl = QLabel(f"PARTE {i + 1}")
            lbl.setFont(QFont("Inter", 12, QFont.Weight.Bold))
            fl.addWidget(lbl)

            te = QTextEdit()
            te.setReadOnly(True)
            te.setFont(QFont("JetBrains Mono", 10))
            te.setMaximumHeight(260)
            fl.addWidget(te)

            lay.addWidget(frame)
            self._frames[i] = frame
            self._labels[i] = lbl
            self._text_edits[i] = te
            self._buffers[i] = deque()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        # Flush timer – coalesce tokens every 150 ms (~6 fps).
        # 60ms causa sobrecarga de repaint no Qt sem retorno visual para humanos.
        self._timer = QTimer(self)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._flush)
        self._timer.start()

    # ── Thread-safe enqueue ──
    @pyqtSlot(int, str)
    def on_stream_token(self, idx: int, token: str):
        with QMutexLocker(self._mutex):
            # [STAFF FIX] Impede KeyError em chamadas fantasmas caso a thread engasgue
            if idx in self._buffers:
                self._buffers[idx].append(token)

    # ── Batch flush on GUI thread ──
    def _flush(self):
        updates = []
        with QMutexLocker(self._mutex):
            for idx, buf in self._buffers.items():
                if buf:
                    updates.append((idx, "".join(buf)))
                    buf.clear()

        if not updates:
            return

        self.setUpdatesEnabled(False)
        try:
            for idx, combined in updates:
                te = self._text_edits.get(idx)
                if te:
                    cursor = te.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    cursor.insertText(combined)
                    # [STAFF FIX] REMOVIDO: te.ensureCursorVisible()
                    # Apenas inserir pelo cursor no final já dá trigger no autoscroll
                    # sem disparar repaints redundantes na viewport da QScrollArea.
        finally:
            self.setUpdatesEnabled(True)

    @pyqtSlot(int)
    def on_block_finished(self, idx: int):
        frame = self._frames.get(idx)
        if frame:
            frame.setStyleSheet(
                "QFrame { background: palette(base); border: 2px solid #159570; border-radius: 16px; }"
            )

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)


# ══════════════════════════════════════════════════════════════════════════
#  Loading Screen
# ══════════════════════════════════════════════════════════════════════════


class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedSize(440, 220)
        self._center_on_screen()

        lay = QVBoxLayout(self)
        lbl = QLabel("Inicializando IA e OCR...\nAguarde...")
        lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)

        self._bar = QProgressBar(self)
        self._bar.setRange(0, 0)  # indeterminate
        self._bar.setFixedWidth(320)
        lay.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

    def _center_on_screen(self):
        geo = (
            self.screen().availableGeometry()
            if self.screen()
            else QApplication.primaryScreen().availableGeometry()
        )
        x = (geo.width() - self.width()) // 2 + geo.x()
        y = (geo.height() - self.height()) // 2 + geo.y()
        self.move(x, y)

    def fade_close(self):
        self.close()


# ══════════════════════════════════════════════════════════════════════════
#  Main Window
# ══════════════════════════════════════════════════════════════════════════


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = Path(__file__).resolve().parent / "assets" / "icon.png"
        if icon_path.is_file():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowTitle("Hermis")
        self.resize(1160, 880)
        self.setMinimumSize(1000, 780)

        self.filepath: str | None = None
        self._streaming_window: StreamingWindow | None = None
        self._orig_palette = QApplication.instance().palette()

        self.is_running = False
        self.start_time: float | None = None

        # Thread management
        self._init_thread: QThread | None = None
        self._work_thread: QThread | None = None

        # Log batching
        self._log_buffer: deque = deque()
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(100)
        self._log_timer.timeout.connect(self._flush_log)

        # Timer loop
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._tick_clock)

        # Show loading then init
        self._loading = LoadingScreen()
        self._loading.show()
        QTimer.singleShot(100, self._start_init)

    # ── Initialisation ──────────────────────────────────────────────────────

    def _start_init(self):
        self._init_worker = InitWorker()
        self._init_thread = QThread()
        self._init_worker.moveToThread(self._init_thread)
        self._init_thread.started.connect(self._init_worker.run)
        self._init_worker.finished.connect(self._on_init_done)
        self._init_worker.finished.connect(self._init_thread.quit)
        self._init_thread.start()

    def _on_init_done(self):
        self._loading.fade_close()
        self._build_ui()
        self.show()

    # ── UI Construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(24, 21, 24, 22)
        root.setSpacing(13)

        # Compact product header — avoids the old oversized title treatment.
        header = QHBoxLayout()
        header.setSpacing(10)

        mark = QLabel("✦")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(38, 38)
        mark.setStyleSheet("""
            QLabel {
                background: #6D5EF5;
                color: white;
                border-radius: 12px;
                font-size: 18pt;
                font-weight: 800;
            }
        """)
        header.addWidget(mark)

        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand = QLabel("HERMIS")
        brand.setObjectName("brand")
        brand_col.addWidget(brand)

        micro = QLabel("TEXT INTELLIGENCE  /  DOCUMENT ANALYSIS")
        micro.setObjectName("micro")
        brand_col.addWidget(micro)
        header.addLayout(brand_col)

        header.addStretch()

        self._status_pill = QLabel("●  LOCAL / READY")
        self._status_pill.setObjectName("statusPill")
        header.addWidget(self._status_pill)

        pulse = QLabel("●")
        pulse.setStyleSheet("QLabel { color: #17BEBB; font-size: 10pt; }")
        pulse.setFixedWidth(12)
        _add_pulse(pulse, 0.35, 0.95)
        header.addWidget(pulse)

        self._btn_theme = QPushButton("Theme")
        self._btn_theme.setObjectName("smallButton")
        self._btn_theme.setToolTip("Alternar entre tema claro e escuro")
        self._btn_theme.clicked.connect(self._toggle_theme)
        header.addWidget(self._btn_theme)

        root.addLayout(header)

        techline = QFrame()
        techline.setObjectName("techLine")
        techline.setFixedHeight(1)
        root.addWidget(techline)

        # Dashboard grid.
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 5)
        grid.setColumnStretch(1, 4)
        grid.setColumnStretch(2, 4)

        # 01 — Document.
        self._file_card = QFrame()
        self._file_card.setObjectName("card")
        self._file_card.setProperty("cardTone", "file")
        file_lay = QVBoxLayout(self._file_card)
        file_lay.setContentsMargins(18, 17, 18, 17)
        file_lay.setSpacing(8)

        file_title = QLabel("01  DOCUMENT")
        file_title.setObjectName("cardTitle")
        file_lay.addWidget(file_title)

        file_hint = QLabel("Escolha o texto que será processado.")
        file_hint.setObjectName("cardHint")
        file_lay.addWidget(file_hint)

        self._btn_select = QPushButton("Selecionar arquivo")
        self._btn_select.setObjectName("primaryButton")
        self._btn_select.clicked.connect(self._select_file)
        file_lay.addWidget(self._btn_select)

        self._lbl_path = QLabel("Nenhum arquivo selecionado")
        self._lbl_path.setObjectName("pathLabel")
        self._lbl_path.setWordWrap(True)
        file_lay.addWidget(self._lbl_path)

        _decorate_card(self._file_card, "⌁", "#5E9DFF")
        grid.addWidget(self._file_card, 0, 0, 2, 1)

        # 02 — Work mode.
        opts = QFrame()
        opts.setObjectName("card")
        opts.setProperty("cardTone", "options")
        opts_lay = QVBoxLayout(opts)
        opts_lay.setContentsMargins(18, 17, 18, 17)
        opts_lay.setSpacing(8)

        opts_title = QLabel("02  WORKFLOW")
        opts_title.setObjectName("cardTitle")
        opts_lay.addWidget(opts_title)

        mode_label = QLabel("Como o conteúdo deve ser transformado?")
        mode_label.setObjectName("cardHint")
        opts_lay.addWidget(mode_label)

        self._combo_mode = QComboBox()
        self._combo_mode.addItems(
            [
                "Apenas Traduzir",
                "Apenas Resumir",
                "Explicação Resumida",
                "Explicação Equilibrada",
                "Explicação Detalhada",
                "Argumentos",
            ]
        )
        self._combo_mode.setCurrentText("Explicação Equilibrada")
        self._combo_mode.currentTextChanged.connect(self._toggle_inputs)
        opts_lay.addWidget(self._combo_mode)

        fmt_row = QHBoxLayout()
        fmt_label = QLabel("Formato")
        fmt_label.setObjectName("cardHint")
        fmt_row.addWidget(fmt_label)
        fmt_row.addStretch()

        self._combo_fmt = QComboBox()
        self._combo_fmt.addItems(["PDF", "TXT"])
        self._combo_fmt.setCurrentText("PDF")
        self._combo_fmt.currentTextChanged.connect(self._toggle_inputs)
        fmt_row.addWidget(self._combo_fmt, 1)
        opts_lay.addLayout(fmt_row)

        _decorate_card(opts, "◌", "#A16CFF")
        grid.addWidget(opts, 0, 1)

        # 03 — AI engine.
        ai_frame = QFrame()
        ai_frame.setObjectName("card")
        ai_frame.setProperty("cardTone", "ai")
        ai_lay = QVBoxLayout(ai_frame)
        ai_lay.setContentsMargins(18, 17, 18, 17)
        ai_lay.setSpacing(8)

        ai_title_row = QHBoxLayout()
        ai_title = QLabel("03  AI ENGINE")
        ai_title.setObjectName("cardTitle")
        ai_title_row.addWidget(ai_title)
        ai_title_row.addStretch()

        self._btn_refresh_models = QPushButton("Atualizar")
        self._btn_refresh_models.setObjectName("smallButton")
        self._btn_refresh_models.clicked.connect(self._populate_ai_models)
        ai_title_row.addWidget(self._btn_refresh_models)
        ai_lay.addLayout(ai_title_row)

        ai_hint = QLabel("Modelo local ou Gemini Cloud.")
        ai_hint.setObjectName("cardHint")
        ai_lay.addWidget(ai_hint)

        self._combo_ai = QComboBox()
        ai_lay.addWidget(self._combo_ai)

        self._lbl_ai_info = QLabel("llama.cpp  •  Vulkan  •  auto")
        self._lbl_ai_info.setObjectName("cardHint")
        ai_lay.addWidget(self._lbl_ai_info)

        _decorate_card(ai_frame, "✦", "#29BFAE")
        grid.addWidget(ai_frame, 0, 2)

        # 04 — Export.
        self._cover_frame = QFrame()
        self._cover_frame.setObjectName("card")
        self._cover_frame.setProperty("cardTone", "output")
        cover_lay = QVBoxLayout(self._cover_frame)
        cover_lay.setContentsMargins(18, 17, 18, 17)
        cover_lay.setSpacing(8)

        cover_title = QLabel("04  EXPORT")
        cover_title.setObjectName("cardTitle")
        cover_lay.addWidget(cover_title)

        self._chk_cover = QCheckBox("Criar capa no PDF")
        self._chk_cover.toggled.connect(self._toggle_inputs)
        cover_lay.addWidget(self._chk_cover)

        self._meta_widget = QWidget()
        meta_lay = QGridLayout(self._meta_widget)
        meta_lay.setContentsMargins(0, 2, 0, 0)
        meta_lay.setHorizontalSpacing(8)
        meta_lay.setVerticalSpacing(7)

        author_label = QLabel("Autor")
        author_label.setObjectName("cardHint")
        title_label = QLabel("Título")
        title_label.setObjectName("cardHint")
        genre_label = QLabel("Gênero")
        genre_label.setObjectName("cardHint")

        self._entry_author = QLineEdit()
        self._entry_author.setPlaceholderText("Nome do autor")
        self._entry_title = QLineEdit()
        self._entry_title.setPlaceholderText("Título do livro")

        self._combo_genre = QComboBox()
        self._combo_genre.addItems(
            [
                "política",
                "fantasia",
                "científico",
                "história",
                "biografia",
                "autoajuda",
                "filosofia",
                "mistério",
                "romance",
                "infantil",
                "educação",
                "economia",
                "saúde",
                "culinária",
                "viagem",
                "arte",
                "tecnologia",
                "geral",
            ]
        )
        self._combo_genre.setCurrentText("geral")

        meta_lay.addWidget(author_label, 0, 0)
        meta_lay.addWidget(self._entry_author, 0, 1)
        meta_lay.addWidget(title_label, 1, 0)
        meta_lay.addWidget(self._entry_title, 1, 1)
        meta_lay.addWidget(genre_label, 2, 0)
        meta_lay.addWidget(self._combo_genre, 2, 1)
        cover_lay.addWidget(self._meta_widget)
        self._meta_widget.hide()

        _decorate_card(self._cover_frame, "↗", "#E2A63D")
        grid.addWidget(self._cover_frame, 1, 1)

        # 05 — Execution.
        run_card = QFrame()
        run_card.setObjectName("card")
        run_card.setProperty("cardTone", "run")
        run_lay = QVBoxLayout(run_card)
        run_lay.setContentsMargins(18, 17, 18, 17)
        run_lay.setSpacing(8)

        run_title = QLabel("05  RUN")
        run_title.setObjectName("cardTitle")
        run_lay.addWidget(run_title)

        self._chk_recap = QCheckBox("Recapitular cada bloco durante a explicação")
        run_lay.addWidget(self._chk_recap)

        self._btn_run = QPushButton("Iniciar análise")
        self._btn_run.setObjectName("primaryButton")
        self._btn_run.setEnabled(False)
        self._btn_run.clicked.connect(self._run_analysis)
        run_lay.addWidget(self._btn_run)

        _decorate_card(run_card, "≫", "#E267B4")
        grid.addWidget(run_card, 1, 2)

        # Progress.
        progress_card = QFrame()
        progress_card.setObjectName("card")
        progress_lay = QVBoxLayout(progress_card)
        progress_lay.setContentsMargins(18, 15, 18, 15)
        progress_lay.setSpacing(8)

        progress_head = QHBoxLayout()
        progress_title = QLabel("SYSTEM STATUS")
        progress_title.setObjectName("cardTitle")
        progress_head.addWidget(progress_title)
        progress_head.addStretch()

        self._lbl_eta = QLabel("Ready")
        self._lbl_eta.setObjectName("cardHint")
        progress_head.addWidget(self._lbl_eta)
        progress_lay.addLayout(progress_head)

        self._progress = QProgressBar()
        self._progress.setValue(0)
        progress_lay.addWidget(self._progress)

        self._activity = QProgressBar()
        self._activity.setRange(0, 0)
        self._activity.hide()
        progress_lay.addWidget(self._activity)

        time_row = QHBoxLayout()
        self._lbl_elapsed = QLabel("Decorrido: 00:00")
        self._lbl_elapsed.setObjectName("cardHint")
        time_row.addWidget(self._lbl_elapsed)
        time_row.addStretch()
        system_hint = QLabel("ASYNC PROCESSING  /  THREAD SAFE")
        system_hint.setObjectName("micro")
        time_row.addWidget(system_hint)
        progress_lay.addLayout(time_row)

        _decorate_card(progress_card, "◎", "#6D5EF5")
        grid.addWidget(progress_card, 2, 0, 1, 3)

        # Diagnostics.
        log_card = QFrame()
        log_card.setObjectName("card")
        log_lay = QVBoxLayout(log_card)
        log_lay.setContentsMargins(18, 15, 18, 15)
        log_lay.setSpacing(7)

        log_head = QHBoxLayout()
        log_title = QLabel("ACTIVITY")
        log_title.setObjectName("cardTitle")
        log_head.addWidget(log_title)
        log_head.addStretch()
        log_hint = QLabel("DIAGNOSTIC FEED")
        log_hint.setObjectName("micro")
        log_head.addWidget(log_hint)
        log_lay.addLayout(log_head)

        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setFixedHeight(118)
        self._log_box.setFont(QFont("JetBrains Mono", 9))
        log_lay.addWidget(self._log_box)

        _decorate_card(log_card, "≋", "#7D8798")
        grid.addWidget(log_card, 3, 0, 1, 3)

        root.addLayout(grid)
        root.addStretch()

        self._toggle_inputs()

    # ── Theme ───────────────────────────────────────────────────────────────

    _is_dark = False

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        app = QApplication.instance()
        _apply_modern_theme(app, self._is_dark)

        # Keep the physical/neumorphic depth coherent after a theme swap.
        shadow_color = QColor("#00000070" if self._is_dark else "#00000028")
        for card in self.findChildren(QFrame, "card"):
            effect = card.graphicsEffect()
            if isinstance(effect, QGraphicsDropShadowEffect):
                effect.setColor(shadow_color)
                effect.setBlurRadius(26 if self._is_dark else 24)
                effect.setOffset(4, 7)

        if hasattr(self, "_status_pill"):
            self._status_pill.setText(
                "●  LOCAL / READY" if not self.is_running else "●  PROCESSING"
            )

    # ── Toggle inputs ───────────────────────────────────────────────────────

    def _toggle_inputs(self, _=None):
        mode = self._combo_mode.currentText()
        fmt = self._combo_fmt.currentText()
        show_cover = fmt == "PDF" and mode != "Argumentos"

        self._chk_cover.setEnabled(show_cover)
        if show_cover and self._chk_cover.isChecked():
            self._meta_widget.show()
        else:
            self._meta_widget.hide()

    # ── Label & AI updates ───────────────────────────────────────────────────

    def _populate_ai_models(self):
        current_selection = (
            self._combo_ai.currentText()
            if hasattr(self, "_combo_ai") and self._combo_ai.count() > 0
            else ""
        )
        self._combo_ai.clear()

        llama_models = main.get_installed_llamacpp_models()
        for model_id in llama_models:
            self._combo_ai.addItem(f"{model_id} (llama.cpp)")

        if not llama_models:
            self._combo_ai.addItem("Llama.cpp Server")

        self._combo_ai.addItem("Gemini (Google Cloud)")

        if current_selection:
            index = self._combo_ai.findText(current_selection)
            if index >= 0:
                self._combo_ai.setCurrentIndex(index)

    # ── File selection ──────────────────────────────────────────────────────

    def _select_file(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Selecionar Documento")
        dialog.setNameFilter("Documentos (*.txt *.pdf *.epub *.mobi)")
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, False)
        if dialog.exec():
            path = dialog.selectedFiles()[0]
            self.filepath = path
            self._lbl_path.setText(os.path.basename(path))
            self._btn_run.setEnabled(True)
            self._log_add(f"Selecionado: {path}\n")

    # ── Logging (batched) ───────────────────────────────────────────────────

    def _log_add(self, text: str):
        self._log_buffer.append(text)
        if not self._log_timer.isActive():
            self._log_timer.start()

    def _flush_log(self):
        if not self._log_buffer:
            self._log_timer.stop()
            return
        combined = "".join(self._log_buffer)
        self._log_buffer.clear()
        self._log_box.setUpdatesEnabled(False)
        try:
            cursor = self._log_box.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(combined)
            self._log_box.setTextCursor(cursor)
            self._log_box.ensureCursorVisible()
        finally:
            self._log_box.setUpdatesEnabled(True)

    # ── Time helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        if seconds <= 0:
            return "00:00"
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def _tick_clock(self):
        if self.is_running and self.start_time:
            elapsed = time.monotonic() - self.start_time
            self._lbl_elapsed.setText(f"Decorrido: {self._fmt_time(elapsed)}")

    # ── Progress ────────────────────────────────────────────────────────────

    @pyqtSlot(int, int, float, float, int)
    def _on_progress(self, done, total, elapsed, last_dur, last_chars):
        self._progress.setMaximum(total)
        self._progress.setValue(done)

        if done > 0:
            avg = elapsed / done
            eta = (total - done) * avg
            self._lbl_eta.setText(f"Restante: ~{self._fmt_time(eta)}")

        if done == total:
            self._lbl_eta.setText("Concluído!")
            self._lbl_eta.setStyleSheet("color: #2ECC71;")

    # ── Streaming window ────────────────────────────────────────────────────

    @pyqtSlot(int)
    def _on_stream_init(self, total_chunks: int):
        self._streaming_window = StreamingWindow(total_chunks)
        self._streaming_window.show()

    @pyqtSlot(int, str)
    def _on_stream_token(self, idx: int, token: str):
        if self._streaming_window:
            self._streaming_window.on_stream_token(idx, token)

    @pyqtSlot(int)
    def _on_block_done(self, idx: int):
        if self._streaming_window:
            self._streaming_window.on_block_finished(idx)

    # ── Run analysis ────────────────────────────────────────────────────────

    def _run_analysis(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_time = time.monotonic()
        self._clock_timer.start()

        # Disable controls
        self._btn_run.setEnabled(False)
        self._btn_select.setEnabled(False)

        self._progress.setValue(0)
        self._lbl_eta.setText("Processando...")
        self._lbl_eta.setStyleSheet("color: #89b4fa;")
        self._activity.show()
        if hasattr(self, "_status_pill"):
            self._status_pill.setText("●  PROCESSING")

        self._log_add("-" * 20 + "\nIniciando extração de texto...\n")

        selected_ai = self._combo_ai.currentText()
        if hasattr(self, "_status_pill"):
            self._status_pill.setText(
                "●  CLOUD / PROCESSING" if "Gemini" in selected_ai else "●  LOCAL / PROCESSING"
            )
        if "Gemini" in selected_ai:
            use_gemini = True
            model_name = None
        else:
            use_gemini = False
            model_name = selected_ai.replace(" (llama.cpp)", "").strip()
            if model_name == "Llama.cpp Server":
                model_name = None

        params = {
            "filepath_from_interface": self.filepath,
            "analysis_option": self._combo_mode.currentText(),
            "output_format": self._combo_fmt.currentText(),
            "create_cover": self._chk_cover.isChecked(),
            "author_name": self._entry_author.text(),
            "book_title": self._entry_title.text(),
            "book_genre": self._combo_genre.currentText(),
            "enable_recap": self._chk_recap.isChecked(),
            "use_gemini": use_gemini,
            "model_name": model_name,
        }

        self._worker = AnalysisWorker(params)
        self._work_thread = QThread()
        self._worker.moveToThread(self._work_thread)
        self._work_thread.started.connect(self._worker.run)

        # Wire signals
        self._worker.log.connect(self._log_add)
        self._worker.progress.connect(self._on_progress)
        self._worker.stream_init.connect(self._on_stream_init)
        self._worker.stream_tok.connect(self._on_stream_token)
        self._worker.block_done.connect(self._on_block_done)
        self._worker.finished.connect(self._on_analysis_done)
        self._worker.finished.connect(self._work_thread.quit)

        self._work_thread.start()

    @pyqtSlot(object)
    def _on_analysis_done(self, result_path):
        self.is_running = False
        self._clock_timer.stop()
        self._activity.hide()
        if hasattr(self, "_status_pill"):
            self._status_pill.setText("●  LOCAL / READY")

        # Re-enable controls
        self._btn_run.setEnabled(True)
        self._btn_select.setEnabled(True)

        # Close streaming window
        if self._streaming_window:
            self._streaming_window.close()
            self._streaming_window = None

        if result_path and os.path.exists(result_path):
            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{result_path}")
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(result_path)))
            except Exception:
                pass
        else:
            QMessageBox.critical(self, "Erro", "Falha ao gerar arquivo. Verifique o log.")

    # ── Cleanup ─────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # main.main() é síncrona; QThread.quit() não interrompe código Python que
        # já está executando no slot. Não fingimos um shutdown seguro enquanto a
        # análise está em execução, evitando thread órfã e encerramento inconsistente.
        if self._work_thread and self._work_thread.isRunning():
            QMessageBox.warning(
                self,
                "Processamento em andamento",
                "A análise ainda está em execução. Aguarde a conclusão antes de fechar o aplicativo.",
            )
            event.ignore()
            return

        if self._init_thread and self._init_thread.isRunning():
            self._init_thread.quit()
            self._init_thread.wait(1000)

        if self._streaming_window:
            self._streaming_window.close()

        super().closeEvent(event)


# ══════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════


def main_entry():
    app = QApplication([])
    _apply_modern_theme(app, dark=False)
    App()
    app.exec()


if __name__ == "__main__":
    main_entry()
