import sys
import webbrowser

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu


def open_github_repository(inst):
    webbrowser.open("https://github.com/bohdanbobrowski/pr-dl")


class PrDlGui:
    def __init__(self):
        self.window: None | QMainWindow = None
        self.app: None | QApplication = None
        self._init_app()

    def _init_app(self):
        self.app = QApplication(sys.argv)
        ui_file_name = "prdl_gui.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        self.window.setFixedSize(640, 480)
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)
        self.window.show()

    def run(self):
        menu_help: QMenu = self.window.findChild(QMenu, "menuHelp")
        for menu_action in menu_help.actions():
            if menu_action.objectName() == "action_git_hub_repository":
                menu_action.triggered.connect(open_github_repository)
        sys.exit(self.app.exec())


if __name__ == "__main__":
    prdl_gui = PrDlGui()
    prdl_gui.run()
