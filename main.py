from PyQt5.QtWidgets import QApplication
from story_checker_gui import StoryCheckerWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = StoryCheckerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 