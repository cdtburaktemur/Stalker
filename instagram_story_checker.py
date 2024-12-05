from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.firefox.service import Service
from winotify import Notification
import webbrowser
import time
import logging
import os
from cryptography.fernet import Fernet

# Logging ayarları
logging.basicConfig(
    filename='instagram_checker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Selenium loglarını kapat
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class InstagramStoryChecker:
    def __init__(self, username_input, password_input):
        try:
            self.driver = None
            self.wait = None
            self.logged_in = False
            
            # GUI'den giriş alanlarını al
            self.username_input = username_input
            self.password_input = password_input
            
            # Firefox ayarlarını yapılandır
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')  # Başlangıçta headless mod açık
            
            # Geckodriver'ın yolunu kontrol et
            geckodriver_path = self.find_geckodriver()
            if geckodriver_path:
                service = Service(geckodriver_path)
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)
                
            self.wait = WebDriverWait(self.driver, 10)
            logging.info("Driver başarıyla başlatıldı")
            
        except Exception as e:
            logging.error(f"Başlatma hatası: {str(e)}")
            print(f"Hata: {str(e)}")
            raise

    def find_geckodriver(self):
        """Sistemde geckodriver'ı bulmaya çalışır"""
        possible_paths = [
            "geckodriver.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python3*", "Scripts", "geckodriver.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Mozilla Firefox", "geckodriver.exe"),
        ]
        
        for path in possible_paths:
            if "*" in path:
                # Wildcard içeren yolları genişlet
                import glob
                matches = glob.glob(path)
                for match in matches:
                    if os.path.exists(match):
                        return match
            elif os.path.exists(path):
                return path
        
        logging.warning("Geckodriver bulunamadı")
        return None

    def setup_driver(self):
        """Tarayıcı ayarlarını yapılandırır"""
        try:
            options = webdriver.FirefoxOptions()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Ek tercihler
            options.set_preference('dom.webdriver.enabled', False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference('network.http.connection-timeout', 30)
            options.set_preference('network.http.connection-retry-timeout', 30)
            
            geckodriver_path = self.find_geckodriver()
            if geckodriver_path:
                service = Service(geckodriver_path)
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)
                
            # Daha uzun timeout süresi
            self.wait = WebDriverWait(self.driver, 20)
            
            # Pencere boyutunu ayarla
            self.driver.set_window_size(1920, 1080)
            
            logging.info("Driver yeniden yapılandırıldı")
            
        except Exception as e:
            logging.error(f"Driver yapılandırma hatası: {str(e)}")
            raise

    def load_credentials(self):
        """Şifrelenmiş giriş bilgilerini yükler ve çözer"""
        try:
            from setup_credentials import load_key, decrypt_credentials
            key = load_key()
            username, password = decrypt_credentials(key)
            return username, password
        except Exception as e:
            logging.error(f"Giriş bilgileri yükleme hatası: {str(e)}")
            raise

    def login(self):
        """Instagram'a giriş yapar"""
        try:
            if not self.driver:
                self.setup_driver()

            # Giriş bilgilerini doğrudan kullan
            username = self.username_input.text()
            password = self.password_input.text()
            
            # Instagram'a git
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)
            
            # Giriş formunu doldur
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(password)
            
            # Giriş yap butonuna tıkla
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            
            time.sleep(5)
            
            # Güvenlik kodu kontrolü
            if "security code" in self.driver.page_source.lower():
                logging.info("Güvenlik kodu gerekiyor - Browser görünür moda geçiliyor")
                
                # Headless modu kapat ve yeni pencere aç
                self.driver.quit()
                options = webdriver.FirefoxOptions()  # Headless olmayan yeni options
                
                if self.find_geckodriver():
                    service = Service(self.find_geckodriver())
                    self.driver = webdriver.Firefox(service=service, options=options)
                else:
                    self.driver = webdriver.Firefox(options=options)
                    
                self.wait = WebDriverWait(self.driver, 10)
                
                # Tekrar giriş yap
                self.driver.get("https://www.instagram.com/")
                time.sleep(5)
                
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                username_input.send_keys(username)
                
                password_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                password_input.send_keys(password)
                
                login_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                login_button.click()
                
                time.sleep(5)
                return "2FA_REQUIRED"
                
            # Giriş başarılı mı kontrol et
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
                )
                self.logged_in = True
                logging.info("Giriş başarılı!")
                return True
            except:
                logging.error("Giriş yapılamadı")
                return False
                
        except Exception as e:
            logging.error(f"Giriş hatası: {str(e)}")
            return False

    def submit_2fa_code(self, code):
        """Güvenlik kodunu gönderir"""
        try:
            # Kod giriş alanını bul ve gönder
            code_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "verificationCode"))
            )
            code_input.send_keys(code)
            
            verify_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button']"))
            )
            verify_button.click()
            
            time.sleep(5)
            
            # Giriş başarılı mı kontrol et
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
                )
                self.logged_in = True
                logging.info("Doğrulama başarılı!")
                
                # Doğrulama başarılıysa tekrar headless moda geç
                self.driver.quit()
                options = webdriver.FirefoxOptions()
                options.add_argument('--headless')  # Headless modu aç
                
                if self.find_geckodriver():
                    service = Service(self.find_geckodriver())
                    self.driver = webdriver.Firefox(service=service, options=options)
                else:
                    self.driver = webdriver.Firefox(options=options)
                    
                self.wait = WebDriverWait(self.driver, 10)
                
                # Instagram'a tekrar giriş yap
                self.driver.get("https://www.instagram.com/")
                return True
                
            except:
                logging.error("Doğrulama başarısız")
                return False
                
        except Exception as e:
            logging.error(f"Doğrulama hatası: {str(e)}")
            return False

    def check_user_story(self, username):
        """Belirtilen kullanıcının hikayelerini kontrol eder"""
        try:
            if not self.logged_in:
                logging.error("Giriş yapılmamış")
                return False
            
            # Profil URL'sini oluştur
            profile_url = f"https://www.instagram.com/{username}/"
            logging.info(f"Profil sayfasına gidiliyor: {profile_url}")
            
            # Profil sayfasına git
            self.driver.get(profile_url)
            time.sleep(5)  # Sayfanın yüklenmesi için daha uzun bekle
            
            # URL kontrolü yap
            current_url = self.driver.current_url
            if username not in current_url:
                logging.error(f"Profil sayfasına ulaşılamadı. Şu anki URL: {current_url}")
                return False
            
            try:
                # Ana main elementini bul
                main_element = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
                logging.info("Ana element bulundu")
                
                # Header elementini bul
                header = main_element.find_element(By.TAG_NAME, "header")
                logging.info("Header elementi bulundu")
                
                # Hikaye elementini kontrol et
                try:
                    story_element = header.find_element(By.CSS_SELECTOR, "div[role='button'] canvas")
                    logging.info("Hikaye elementi bulundu!")
                    
                    # Bildirim gönder
                    self.send_notification(f"{username} kullanıcısının hikayesi var!")
                    webbrowser.open("https://kosmosvize.com.tr")
                    return True
                    
                except:
                    logging.info(f"{username} kullanıcısının hikayesi yok")
                    return False
                    
            except TimeoutException:
                logging.error(f"{username} profili yüklenemedi")
                return False
            
        except Exception as e:
            logging.error(f"Hikaye kontrol hatası: {str(e)}")
            self.logged_in = False
            return False

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

    def close(self):
        """Tarayıcıyı kapatır"""
        if self.driver:
            self.driver.quit() 