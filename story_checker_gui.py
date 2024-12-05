from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox, QDialog,
                            QSystemTrayIcon, QMenu, QAction, QApplication,
                            QProgressBar, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from instagram_story_checker import InstagramStoryChecker
import logging
import os
import time
import webbrowser

class MonitoringThread(QThread):
    """Hikaye kontrolü için arka plan thread'i"""
    story_found = pyqtSignal(str)  # Hikaye bulunduğunda sinyal gönder
    error_occurred = pyqtSignal(str)  # Hata durumunda sinyal gönder
    time_remaining = pyqtSignal(int)  # Kalan süreyi bildirmek için yeni sinyal
    
    def __init__(self, checker, target_input, interval):
        super().__init__()
        self.checker = checker
        self.target_input = target_input
        self.is_running = True
        self.check_interval = interval * 60  # Dakikayı saniyeye çevir
    
    def run(self):
        while self.is_running:
            try:
                target_username = self.target_input.text()
                if self.checker.check_user_story(target_username):
                    self.story_found.emit(target_username)
                
                # Geri sayım
                for remaining in range(self.check_interval, 0, -1):
                    if not self.is_running:
                        break
                    self.time_remaining.emit(remaining)
                    time.sleep(1)
                    
            except Exception as e:
                self.error_occurred.emit(str(e))
                time.sleep(60)
    
    def stop(self):
        self.is_running = False

class LoginThread(QThread):
    """Giriş işlemi için arka plan thread'i"""
    success = pyqtSignal()  # Başarılı giriş sinyali
    failure = pyqtSignal(str)  # Hata sinyali
    two_factor_required = pyqtSignal()  # 2FA gerekli sinyali
    
    def __init__(self, checker):
        super().__init__()
        self.checker = checker
    
    def run(self):
        try:
            result = self.checker.login()
            if result == "2FA_REQUIRED":
                self.two_factor_required.emit()
            elif result:
                self.success.emit()
            else:
                self.failure.emit("Giriş başarısız")
        except Exception as e:
            self.failure.emit(str(e))

class StoryCheckerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.setWindowTitle("Instagram Hikaye Takipçisi")
        self.setMinimumSize(400, 200)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Giriş bilgileri bölümü
        credentials_group = QWidget()
        credentials_layout = QVBoxLayout(credentials_group)
        
        # Kullanıcı adı
        username_layout = QHBoxLayout()
        username_label = QLabel("Instagram Kullanıcı Adı:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Şifre
        password_layout = QHBoxLayout()
        password_label = QLabel("Instagram Şifresi:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Şifre göster/gizle butonu
        self.toggle_password_button = QPushButton("👁")
        self.toggle_password_button.setFixedWidth(30)
        self.toggle_password_button.setToolTip("Şifreyi Göster/Gizle")
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)
        
        # Takip edilecek kullanıcı
        target_layout = QHBoxLayout()
        target_label = QLabel("Takip Edilecek Kullanıcı:")
        self.target_input = QLineEdit()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_input)
        
        # Kontrol aralığı seçimi
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Kontrol Aralığı:")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['1 dakika', '2 dakika', '5 dakika', '10 dakika', '15 dakika', '30 dakika'])
        self.interval_combo.setCurrentText('5 dakika')  # Varsayılan 5 dakika
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_combo)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Bilgileri Kaydet")
        self.start_button = QPushButton("Takibi Başlat")
        self.stop_button = QPushButton("Takibi Durdur")
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        # Layout'ları ana layout'a ekle
        credentials_layout.addLayout(username_layout)
        credentials_layout.addLayout(password_layout)
        credentials_layout.addLayout(target_layout)
        credentials_layout.addLayout(interval_layout)
        credentials_layout.addLayout(button_layout)
        
        layout.addWidget(credentials_group)
        
        # Buton bağlantıları
        self.save_button.clicked.connect(self.save_credentials)
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        
        # InstagramStoryChecker örneği
        self.checker = None
        self.monitoring = False
        
        # Kaydedilmiş bilgileri yükle
        self.load_saved_credentials()
        
        # Sistem tepsisi ikonu oluştur
        self.create_tray_icon()
        
        self.monitoring_thread = None
        self.login_thread = None
        
        # İlerleme çubuğu ve durum mesajı için container
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Belirsiz ilerleme
        self.progress_bar.hide()  # Başlangıçta gizli
        progress_layout.addWidget(self.progress_bar)
        
        # Durum mesajı
        self.status_label = QLabel("Bekleniyor...")
        progress_layout.addWidget(self.status_label)
        
        # Ana layout'a ekle
        layout.addWidget(progress_container)
        
        # Butonları güncelle
        self.start_button.setText("Takibi Başlat")
        self.stop_button.setText("Takibi Durdur")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        self.start_button.setStyleSheet("QPushButton { background-color: #51cf66; color: white; }")
    
    def create_tray_icon(self):
        """Sistem tepsisi ikonu ve menüsünü oluşturur"""
        try:
            # İkon dosyasının yolunu bul
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if not os.path.exists(icon_path):
                icon_path = "icon.ico"  # Aynı dizinde ara
            
            # Sistem tepsisi ikonu oluştur
            self.tray_icon = QSystemTrayIcon(self)
            
            # İkonu ayarla
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            else:
                logging.warning("İkon dosyası bulunamadı!")
            
            # Tepsi menüsü oluştur
            self.tray_menu = QMenu()  # self ile saklayalım
            
            # Menü öğeleri
            show_action = QAction("Göster", self.tray_menu)
            show_action.triggered.connect(self.show)
            
            hide_action = QAction("Gizle", self.tray_menu)
            hide_action.triggered.connect(self.hide)
            
            quit_action = QAction("Çıkış", self.tray_menu)
            quit_action.triggered.connect(self.close_application)
            
            # Menüye öğeleri ekle
            self.tray_menu.addAction(show_action)
            self.tray_menu.addAction(hide_action)
            self.tray_menu.addSeparator()
            self.tray_menu.addAction(quit_action)
            
            # Menüyü ikona bağla
            self.tray_icon.setContextMenu(self.tray_menu)
            
            # İkonu göster
            self.tray_icon.show()
            
            # İkona çift tıklama olayını bağla
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            logging.info("Sistem tepsisi ikonu oluşturuldu")
            
        except Exception as e:
            logging.error(f"Sistem tepsisi oluşturma hatası: {str(e)}")
    
    def toggle_password_visibility(self):
        """Şifre görünürlüğünü değiştirir"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("👁")
    
    def tray_icon_activated(self, reason):
        """Sistem tepsisi ikonuna tıklanınca"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def close_application(self):
        """Uygulamayı tamamen kapatır"""
        try:
            if self.checker:
                self.checker.close()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            self.close()
            QApplication.instance().quit()
        except Exception as e:
            logging.error(f"Uygulama kapatma hatası: {str(e)}")
            self.close()
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        if self.monitoring:
            # Takip devam ediyorsa, sadece gizle
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Instagram Hikaye Takipçisi",
                "Program arka planda çalışmaya devam ediyor",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            # Takip yoksa tamamen kapat
            self.close_application()
    
    def save_credentials(self):
        """Giriş bilgilerini kaydet"""
        try:
            from setup_credentials import encrypt_credentials, create_key
            
            username = self.username_input.text()
            password = self.password_input.text()
            target = self.target_input.text()  # Takip edilecek kullanıcıyı da kaydedelim
            
            if not username or not password:
                QMessageBox.warning(self, "Hata", "Kullanıcı adı ve şifre boş olamaz!")
                return
                
            # Şifreleme anahtarı oluştur
            key = create_key()
            
            # Bilgileri şifrele ve kaydet
            encrypt_credentials(username, password, key)
            
            # Takip edilecek kullanıcıyı da kaydet
            with open("target_user.txt", "w", encoding='utf-8') as f:
                f.write(target)
            
            # Kullanıcı arayüzündeki bilgileri temizle
            self.username_input.clear()
            self.password_input.clear()
            
            QMessageBox.information(self, "Başarılı", "Giriş bilgileri kaydedildi!")
            
        except Exception as e:
            logging.error(f"Bilgi kaydetme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Bilgiler kaydedilemedi: {str(e)}")
    
    def load_saved_credentials(self):
        """Kaydedilmiş bilgileri yükle"""
        try:
            # Giriş bilgilerini yükle
            from setup_credentials import load_key, decrypt_credentials
            try:
                key = load_key()
                username, password = decrypt_credentials(key)
                
                # Giriş alanlarını doldur
                self.username_input.setText(username)
                self.password_input.setText(password)
                logging.info("Kaydedilmiş giriş bilgileri yüklendi")
            except Exception as e:
                logging.warning(f"Giriş bilgileri yüklenemedi: {str(e)}")
            
            # Takip edilecek kullanıcıyı yükle
            if os.path.exists("target_user.txt"):
                with open("target_user.txt", "r", encoding='utf-8') as f:
                    target = f.read().strip()
                    self.target_input.setText(target)
                    logging.info("Kaydedilmiş hedef kullanıcı yüklendi")
                
        except Exception as e:
            logging.error(f"Bilgi yükleme hatası: {str(e)}")
    
    def start_monitoring(self):
        """Hikaye takibini başlat"""
        try:
            target_username = self.target_input.text()
            if not target_username:
                QMessageBox.warning(self, "Hata", "Takip edilecek kullanıcı adı boş olamaz!")
                return
            
            # İlerleme çubuğunu göster
            self.progress_bar.show()
            self.status_label.setText("Instagram'a giriş yapılıyor...")
            
            # Butonları ve ComboBox'ı güncelle
            self.start_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.interval_combo.setEnabled(False)  # ComboBox'ı devre dışı bırak
            
            # Bilgilendirme mesajı
            QMessageBox.information(
                self,
                "Bilgi",
                "Program çalışmaya başladı.\nPencereyi kapatırsanız program sistem tepsisinde çalışmaya devam edecek."
            )
            
            # Checker'ı başlat
            self.checker = InstagramStoryChecker(
                username_input=self.username_input,
                password_input=self.password_input
            )
            
            # Login thread'ini başlat
            self.login_thread = LoginThread(self.checker)
            self.login_thread.success.connect(self.on_login_success)
            self.login_thread.failure.connect(self.on_login_failure)
            self.login_thread.two_factor_required.connect(self.on_two_factor_required)
            self.login_thread.start()
            
        except Exception as e:
            self.on_monitoring_error(str(e))
    
    def on_login_success(self):
        """Giriş başarılı olduğunda"""
        self.status_label.setText("Giriş başarılı! Hikaye kontrolü başlatılıyor...")
        
        # Seçilen kontrol aralığını al
        interval = int(self.interval_combo.currentText().split()[0])  # "5 dakika" -> 5
        
        # Monitoring thread'ini başlat
        self.monitoring_thread = MonitoringThread(
            self.checker, 
            self.target_input,
            interval  # Kontrol aralığını geç
        )
        self.monitoring_thread.story_found.connect(self.on_story_found)
        self.monitoring_thread.error_occurred.connect(self.on_monitoring_error)
        self.monitoring_thread.time_remaining.connect(self.update_time_remaining)
        self.monitoring_thread.start()
        
        # UI güncellemeleri
        self.monitoring = True
        self.stop_button.setEnabled(True)
    
    def on_login_failure(self, error_message):
        """Giriş başarısız olduğunda"""
        self.progress_bar.hide()
        self.status_label.setText("Giriş başarısız!")
        self.start_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        QMessageBox.critical(self, "Hata", f"Instagram'a giriş yapılamadı: {error_message}")
    
    def on_two_factor_required(self):
        """İki faktörlü doğrulama gerektiğinde"""
        dialog = VerificationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            code = dialog.get_code()
            if not self.checker.submit_2fa_code(code):
                QMessageBox.critical(self, "Hata", "Doğrulama kodu kabul edilmedi!")
                return
            self.on_login_success()
    
    def on_story_found(self, username):
        """Hikaye bulunduğunda"""
        self.send_notification(f"{username} kullanıcısının hikayesi var!")
        webbrowser.open("https://kosmosvize.com.tr")
    
    def on_monitoring_error(self, error_message):
        """Takip sırasında hata oluştuğunda"""
        logging.error(f"Takip hatası: {error_message}")
    
    def send_notification(self, message):
        """Windows bildirimi gönderir"""
        try:
            notification = Notification(
                app_id="Instagram Hikaye Takipçisi",
                title="Yeni Hikaye!",
                msg=message,
                duration="long"
            )
            notification.show()
            logging.info(f"Bildirim gönderildi: {message}")
        except Exception as e:
            logging.error(f"Bildirim gönderme hatası: {str(e)}")
    
    def stop_monitoring(self):
        """Hikaye takibini durdur"""
        try:
            self.status_label.setText("Takip durduruluyor...")
            
            if self.monitoring_thread:
                self.monitoring_thread.stop()
                self.monitoring_thread.wait()
                self.monitoring_thread = None
            
            if self.checker:
                self.checker.close()
                self.checker = None
            
            self.monitoring = False
            self.progress_bar.hide()
            self.status_label.setText("Bekleniyor...")
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.interval_combo.setEnabled(True)  # ComboBox'ı tekrar aktif et
            
        except Exception as e:
            logging.error(f"Takip durdurma hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Takip durdurulamadı: {str(e)}")
    
    def update_time_remaining(self, seconds):
        """Kalan süreyi güncelle"""
        minutes = seconds // 60
        secs = seconds % 60
        status_text = f"Sonraki kontrol: {minutes:02d}:{secs:02d}"
        self.status_label.setText(status_text)
        
        # İlerleme çubuğunu güncelle
        interval = int(self.interval_combo.currentText().split()[0]) * 60  # Saniyeye çevir
        self.progress_bar.setRange(0, interval)
        self.progress_bar.setValue(interval - seconds)
    
class VerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instagram Doğrulama")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Açıklama
        info_label = QLabel(
            "Instagram hesabınızı korumak için bir doğrulama kodu gönderdik.\n"
            "Lütfen mail adresinizi kontrol edip gelen kodu girin:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Kod giriş alanı
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("6 haneli kodu buraya girin")
        self.code_input.setMaxLength(6)  # Sadece 6 karakter
        self.code_input.setAlignment(Qt.AlignCenter)  # Ortala
        
        # Büyük font kullan
        font = self.code_input.font()
        font.setPointSize(16)
        self.code_input.setFont(font)
        
        layout.addWidget(self.code_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.submit_button = QPushButton("Doğrula")
        self.submit_button.setDefault(True)  # Enter tuşu ile tetiklenebilir
        self.submit_button.clicked.connect(self.validate_and_accept)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Durum mesajı için label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
        
        # Kod girişine odaklan
        self.code_input.setFocus()
    
    def validate_and_accept(self):
        """Kodu doğrula ve kabul et"""
        code = self.code_input.text().strip()
        
        # Basit doğrulama
        if not code:
            self.status_label.setText("Lütfen kodu girin!")
            return
        
        if not code.isdigit():
            self.status_label.setText("Kod sadece rakamlardan oluşmalıdır!")
            return
            
        if len(code) != 6:
            self.status_label.setText("Kod 6 haneli olmalıdır!")
            return
            
        self.accept()
    
    def get_code(self):
        """Girilen kodu döndür"""
        return self.code_input.text().strip() 