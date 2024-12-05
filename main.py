from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from story_checker_gui import StoryCheckerWindow
import sys
import logging
import os

# Günlük dosyası ayarları
logging.basicConfig(
    filename="instagram_story_checker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)

def main():
    global app  # Global olarak tut
    app = QApplication(sys.argv)
    window = StoryCheckerWindow()
    window.show()
    
    logging.info("Instagram Hikaye Takipçisi başlatıldı.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
