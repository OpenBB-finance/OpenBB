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
}
QScrollBar {
    background: #3d3d3d;
    alternate-background-color: #3d3d3d;
}
QScrollBar:horizontal {
    border: 1px solid #3d3d3d;
    background: #3d3d3d;
    height: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #2d2d2d;
    min-width: 0px;
}
QScrollBar:vertical {
    border: 1px solid #3d3d3d;
    background: #3d3d3d;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #2d2d2d;
    min-height: 0px;
}
QScrollBar::add-line:vertical {
    border: 1px solid #3d3d3d;
    background: #3d3d3d;
    height: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical {
    border: 1px solid #3d3d3d;
    background: #3d3d3d;
    height: 0 px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
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
