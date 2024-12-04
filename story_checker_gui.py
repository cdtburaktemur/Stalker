from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QLineEdit, QPushButton, QLabel, QTextEdit)
from PyQt5.QtCore import QTimer, pyqtSlot
from instagram_story_checker import InstagramStoryChecker
import sys
import time

class StoryCheckerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checker = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_story)
        self.init_ui()

    def init_ui(self):
        """Arayüz elemanlarını oluşturur"""
        self.setWindowTitle('Instagram Hikaye Takipçisi')
        self.setGeometry(100, 100, 600, 400)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Kullanıcı adı alanı
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Instagram kullanıcı adınız')
        layout.addWidget(self.username_input)

        # Şifre alanı
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Instagram şifreniz')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Takip edilecek kullanıcı
        self.target_username = QLineEdit()
        self.target_username.setPlaceholderText('Takip edilecek kullanıcı adı')
        layout.addWidget(self.target_username)

        # Başlat/Durdur butonu
        self.start_button = QPushButton('Takibi Başlat')
        self.start_button.clicked.connect(self.toggle_checking)
        layout.addWidget(self.start_button)

        # Log alanı
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Durum etiketi
        self.status_label = QLabel('Durum: Beklemede')
        layout.addWidget(self.status_label)

    def log_message(self, message):
        """Log alanına mesaj ekler"""
        current_time = time.strftime("%H:%M:%S")
        self.log_area.append(f"[{current_time}] {message}")

    @pyqtSlot()
    def toggle_checking(self):
        """Hikaye kontrolünü başlatır/durdurur"""
        if self.checker is None:
            # Takibi başlat
            self.checker = InstagramStoryChecker()
            self.checker.setup_driver()
            
            username = self.username_input.text()
            password = self.password_input.text()
            
            self.log_message("Giriş yapılıyor...")
            if self.checker.login(username, password):
                self.log_message("Giriş başarılı!")
                self.start_button.setText('Takibi Durdur')
                self.status_label.setText('Durum: Çalışıyor')
                
                # Her dakika kontrol et (60000 ms = 1 dakika)
                self.timer.start(60000)
                self.check_story()  # İlk kontrolü hemen yap
            else:
                self.log_message("Giriş başarısız!")
                self.checker.close()
                self.checker = None
        else:
            # Takibi durdur
            self.timer.stop()
            self.checker.close()
            self.checker = None
            self.start_button.setText('Takibi Başlat')
            self.status_label.setText('Durum: Beklemede')
            self.log_message("Takip durduruldu")

    @pyqtSlot()
    def check_story(self):
        """Hikaye kontrolünü gerçekleştirir"""
        if self.checker:
            target = self.target_username.text()
            if self.checker.check_user_story(target):
                self.log_message(f"{target} kullanıcısının hikayesi var!")
            else:
                self.log_message(f"{target} kullanıcısının hikayesi yok.")

    def closeEvent(self, event):
        """Program kapatılırken kaynakları temizler"""
        if self.checker:
            self.checker.close()
        event.accept() 