# coding:utf-8
import sys
from enum import Enum

from PyQt6.QtCore import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (QApplication, QCompleter, QFrame, QHBoxLayout,
                             QLabel, QVBoxLayout, QWidget)
from qfluentwidgets import (CaptionLabel, CardWidget, ElevatedCardWidget,
                            FlowLayout)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (FluentWindow, IconWidget, ImageLabel, MessageBox,
                            NavigationAvatarWidget, NavigationItemPosition,
                            ScrollArea, SplashScreen, StyleSheetBase,
                            SystemThemeListener, TextWrap, Theme, isDarkTheme,
                            qconfig, setTheme)
from qframelesswindow import FramelessWindow, StandardTitleBar

# def update_palette(app, theme):
#     """Update the application's text color based on the selected theme."""
#     palette = QApplication.instance().palette()

#     if theme == "Dark":
#         palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))  # White text for dark mode
#     else:
#         palette.setColor(QPalette.ColorRole.WindowText, QColor("black"))  # Black text for light mode

#     QApplication.instance().setPalette(palette)  # Apply palette globally


class Demo(FluentWindow):

    def __init__(self):
        super().__init__()
        self.resize(860, 700)
        # self.setMinimumWidth(860)
        self.setWindowIcon(QIcon("./icon2.png"))
        self.setWindowTitle("RF4S")

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(256, 256))

        # titleBar = StandardTitleBar(self.splashScreen)
        # titleBar.setIcon(self.windowIcon())
        # titleBar.setTitle(self.windowTitle())
        # self.splashScreen.setTitleBar(titleBar)
        self.show()

        # self.createSubInterface()
        self.splashScreen.finish()

        self.homeInterface = HomeInterface(self)
        self.addSubInterface(self.homeInterface, FIF.HOME, "Home")

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(2000, loop.quit)
        loop.exec()


class HomeInterface(ScrollArea):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWidgetResizable(True)
        # self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("HomeInterface")

        banner = QWidget(self)
        banner.setFixedHeight(336)
        image_label = QLabel(banner)
        pixmap = QPixmap("image.png")
        image_label.setPixmap(pixmap)
        # Optional: Resize or position the QLabel if necessary
        # image_label.resize(pixmap.width(), pixmap.height())
        # image_label.move(50, 50)  # Adjust position as needed

        view = QWidget(self)
        view.setObjectName("view")
        self.setWidget(view)
        self.setStyleSheet(
            """
            #view {
                background-color: transparent;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }
            """
        )

        self.vBoxLayout = QVBoxLayout(view)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(banner)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cardView = SampleCardView("test", view)
        self.cardView.addSampleCard(
            icon="./icon2.png",
            title="Run Fishing Bot",
            content=self.tr("Choose a mode and start fishing automatically."),
            routeKey="basicInputInterface",
            index=0,
        )
        self.cardView.addSampleCard(
            icon="./icon2.png",
            title="Craft Items",
            content=self.tr("Craft food, groundbait, lure, etc."),
            routeKey="basicInputInterface",
            index=1,
        )
        self.cardView.addSampleCard(
            icon="./icon2.png",
            title="Harvest Baits",
            content=self.tr(
                "Harvest baits and replenish hunger/comfort automatically."
            ),
            routeKey="basicInputInterface",
            index=2,
        )
        self.cardView.addSampleCard(
            icon="./icon2.png",
            title="Toggle moving forward",
            content=self.tr(
                "Toggle moving forward by holding down 'W' key."
            ),
            routeKey="basicInputInterface",
            index=3,
        )
        self.cardView.addSampleCard(
            icon="./icon2.png",
            title="Automate Friction Brake",
            content=self.tr(
                "Automate the Friction Brake when a fish is hooked."
            ),
            routeKey="basicInputInterface",
            index=4,
        )
        self.cardView.addSampleCard(
            icon="./icon2.png",
            title="Calculate Tackle's Stats",
            content=self.tr(
                "Calculate your reel's real drag and leader's real load capacity based on wear"
            ),
            routeKey="basicInputInterface",
            index=5,
        )
        self.vBoxLayout.addWidget(self.cardView)


# class StyleSheet(StyleSheetBase, Enum):
#     """ Style sheet  """

#     LINK_CARD = "link_card"
#     SAMPLE_CARD = "sample_card"
#     HOME_INTERFACE = "home_interface"
#     ICON_INTERFACE = "icon_interface"
#     VIEW_INTERFACE = "view_interface"
#     SETTING_INTERFACE = "setting_interface"
#     GALLERY_INTERFACE = "gallery_interface"
#     NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"

#     def path(self, theme=Theme.AUTO):
#         theme = qconfig.theme if theme == Theme.AUTO else theme
#         return f":/gallery/qss/{theme.value.lower()}/{self.value}.qss"


class SignalBus(QObject):
    """pyqtSignal bus"""

    switchToSampleCard = pyqtSignal(str, int)
    micaEnableChanged = pyqtSignal(bool)
    supportSignal = pyqtSignal()


signalBus = SignalBus()


class SampleCardView(QWidget):
    """Sample card view"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        # self.titleLabel = QLabel(title, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.flowLayout = FlowLayout()

        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)
        self.vBoxLayout.setSpacing(10)
        self.flowLayout.setContentsMargins(0, 36, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        # self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.flowLayout, 1)

        # self.titleLabel.setObjectName("viewTitleLabel")
        self.setStyleSheet(
            """
            #titleLabel {
                color: black;
                font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                font-weight: bold;
            }

            #contentLabel {
                color: rgb(118, 118, 118);
                font: 12px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
            }

            #viewTitleLabel {
                color: black;
                font: 20px "Segoe UI SemiBold", "Microsoft YaHei", 'PingFang SC';
            }
            """
        )

    def addSampleCard(self, icon, title, content, routeKey, index):
        """add sample card"""
        card = SampleCard(icon, title, content, routeKey, index, self)
        self.flowLayout.addWidget(card)


class SampleCard(CardWidget):
    """Sample card"""

    def __init__(self, icon, title, content, routeKey, index, parent=None):
        super().__init__(parent=parent)
        self.index = index
        self.routekey = routeKey

        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.switchToSampleCard.emit(self.routekey, self.index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Demo()
    # w.show()
    app.exec()
