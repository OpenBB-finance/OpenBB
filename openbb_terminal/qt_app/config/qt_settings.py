from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QApplication

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
WEB_ENGINE_SETTINGS = [
    (QWebEngineSettings.WebAttribute.WebGLEnabled, True),
    (QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True),
    (QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True),
    (QWebEngineSettings.WebAttribute.LocalStorageEnabled, True),
    (QWebEngineSettings.WebAttribute.PluginsEnabled, True),
]

STYLE_SHEET = """
QPushButton {
    background-color: "#3d3d40";
}
QWidget,
QLineEdit,
QAbstractItemView,
QTreeWidget,
QHeaderView,
QListView {
    background-color: "#3d3d40";
    color: "white";
}
QHeaderView::section,
QListView,
QTreeView {
    background-color: #2d2d2d;
    color: white;
}
QTreeView::item:hover,
QTreeView::item::selected,
QListView::item::selected {
    background-color: #3d3d3d;
    color: white;
    border: 1px solid #2d2d2d;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #2d2d2d;
    width: 15px;
    height: 15px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""

LOADING_HTML = """
<style>
.lds-ripple {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
}
.lds-ripple div {
    position: absolute;
    border: 4px solid #1e88e5;
    opacity: 1;
    border-radius: 50%;
    animation: lds-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
}
.lds-ripple div:nth-child(2) {
    animation-delay: -0.5s;
}
@keyframes lds-ripple {
    0% {
        top: 36px;
        left: 36px;
        width: 0;
        height: 0;
        opacity: 0;
    }
    4.9% {
        top: 36px;
        left: 36px;
        width: 0;
        height: 0;
        opacity: 0;
    }
    5% {
        top: 36px;
        left: 36px;
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        top: 0px;
        left: 0px;
        width: 72px;
        height: 72px;
        opacity: 0;
    }
}
</style>
<div style="position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);">
    <div class="lds-ripple"><div></div><div></div></div>
"""


APP_PALETTE = QPalette()
APP_PALETTE.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
APP_PALETTE.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
APP_PALETTE.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
APP_PALETTE.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
APP_PALETTE.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
APP_PALETTE.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
APP_PALETTE.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
APP_PALETTE.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
APP_PALETTE.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
APP_PALETTE.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
APP_PALETTE.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
APP_PALETTE.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
APP_PALETTE.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)


QT_PATH = Path(__file__).parent.parent.resolve()
ICON_PATH = QT_PATH / "assets/favicon.ico"
