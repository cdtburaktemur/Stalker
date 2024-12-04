from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from story_checker_gui import StoryCheckerWindow
import sys
import logging
import os
import setup_utils  # Setup işlemlerini içeren modülü içeri aktar

# Günlük dosyası ayarları
logging.basicConfig(
    filename="instagram_story_checker.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    app = QApplication(sys.argv)

    # Programın ana dizinini bul ve ikonun yolunu belirle
    script_directory = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_directory, "icon.ico")

    # Sistem tepsisi için simge
    tray_icon = QSystemTrayIcon(QIcon(icon_path), parent=app)
    tray_menu = QMenu()
          # Ana Pencereyi Açma Seçeneği
    open_action = QAction("Arayüzü Aç", tray_menu)
    open_action.triggered.connect(lambda: window.show())
    tray_menu.addAction(open_action)

    # Çıkış Seçeneği
    exit_action = QAction("Çıkış", tray_menu)
    exit_action.triggered.connect(lambda: (stop_service(), app.quit()))
    tray_menu.addAction(exit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()


    window = StoryCheckerWindow()
    window.show()
    start_service()
    tray_icon.showMessage(
        "Instagram Hikaye Takipçisi",
        "Uygulama sistem tepsisine taşındı.",
        QSystemTrayIcon.Information,
        2000
    )

    logging.info("Instagram Hikaye Takipçisi başlatıldı.")

    setup_utils.main()
    # Otomatik Başlatma Ayarlarını Yap
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_scheduler_or_registry.py")
    os.system(f'python "{script_path}"')

    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Hata oluştu: {str(e)}")
