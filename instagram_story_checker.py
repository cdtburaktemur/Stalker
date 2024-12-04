from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from winotify import Notification
import webbrowser  # Varsayılan tarayıcıda URL açmak için
import time

class InstagramStoryChecker:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logged_in = False
        
    def setup_driver(self):
        """Tarayıcı ayarlarını yapılandırır"""
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')  # Tarayıcıyı görünmez modda çalıştır
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self, username, password):
        """Instagram'a giriş yapar"""
        try:
            if not self.driver:
                self.setup_driver()
                
            self.driver.get("https://www.instagram.com/")
            time.sleep(2)  # Sayfanın yüklenmesi için bekle
            
            # Giriş alanlarını bekle
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            # Bilgileri gir
            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            
            # Giriş butonuna tıkla
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[type='submit']"
            )
            login_button.click()
            
            # Giriş başarılı mı kontrol et
            time.sleep(5)  # Giriş işlemi için bekle
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
            )
            self.logged_in = True
            return True
            
        except TimeoutException:
            print("Giriş yapılamadı - Timeout")
            return False
        except Exception as e:
            print(f"Giriş hatası: {str(e)}")
            return False
            
    def check_user_story(self, username):
        """Belirtilen kullanıcının hikayelerini kontrol eder"""
        try:
            if not self.logged_in:
                return False
                
            # Kullanıcı profiline git
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(3)  # Sayfanın yüklenmesi için bekle
            
            try:
                # Ana main elementini bul
                main_element = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
                
                # Header elementini bul
                header = main_element.find_element(By.TAG_NAME, "header")
                
                # Menü dışındaki canvas elementlerini kontrol et
                stories = []
                canvas_elements = header.find_elements(By.TAG_NAME, "canvas")
                
                for canvas in canvas_elements:
                    # Canvas'ın üst elementlerinde menü rolü olan div var mı kontrol et
                    try:
                        menu_parent = canvas.find_element(By.XPATH, "./ancestor::div[@role='menu']")
                    except:
                        # Menü rolü olan üst element bulunamadıysa bu canvas'ı listeye ekle
                        stories.append(canvas)
                
                if stories:
                    self.send_notification(f"{username} kullanıcısının hikayesi var!")
                    # Kosmos vize sayfasını varsayılan tarayıcıda aç
                    webbrowser.open("https://kosmosvize.com.tr")
                    return True
                
                print(f"{username} kullanıcısının hikayesi yok")
                return False
                
            except TimeoutException:
                print(f"{username} profili bulunamadı veya erişilemiyor")
                return False
                
        except Exception as e:
            print(f"Hikaye kontrol hatası: {str(e)}")
            self.logged_in = False
            return False
            
    def send_notification(self, message):
        """Windows için masaüstü bildirimi gönderir"""
        try:
            toast = Notification(
                app_id="Instagram Hikaye Takipçisi",
                title="Instagram Hikaye Bildirimi",
                msg=message,
                duration="short"
            )
            toast.show()
        except Exception as e:
            print(f"Bildirim hatası: {str(e)}")
            
    def close(self):
        """Tarayıcıyı kapatır"""
        if self.driver:
            self.driver.quit() 