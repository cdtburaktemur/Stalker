# Instagram Hikaye Takip Servisi

Bu servis, belirtilen Instagram kullanıcısının hikayelerini otomatik olarak kontrol eder ve hikaye paylaşıldığında bildirim gönderir.

## Proje Dosyaları

1. **instagram_story_checker.py**: Ana kontrol sınıfı
   - Instagram'a giriş yapma
   - Hikaye kontrolü
   - Bildirim gönderme
   - Tarayıcı yönetimi

2. **instagram_story_service.py**: Windows servis yapılandırması
   - Servis kurulumu ve yönetimi
   - Arka plan çalışma mantığı
   - Log yönetimi

3. **story_checker_gui.py**: Kullanıcı arayüzü (opsiyonel)
   - Giriş bilgileri formu
   - Durum göstergesi
   - Log görüntüleme

4. **main.py**: GUI başlatıcı (opsiyonel)

## Kurulum Adımları

### 1. Gerekli Paketlerin Kurulumu
bash
pip install pywin32 selenium winotify

### 2. Firefox ve Geckodriver Kurulumu
- Firefox tarayıcısını yükleyin
- [Geckodriver'ı indirin](https://github.com/mozilla/geckodriver/releases)
- Geckodriver.exe dosyasını Python Scripts klasörüne kopyalayın:

C:\Users\[KullanıcıAdınız]\AppData\Local\Programs\Python\Python3x\Scripts


### 3. Servis Yapılandırması
`instagram_story_service.py` dosyasında kullanıcı bilgilerini güncelleyin:


### 3. Servis Yapılandırması
`instagram_story_service.py` dosyasında kullanıcı bilgilerini güncelleyin:


## Servis Kurulumu ve Yönetimi

### Servis Kurulumu
PowerShell'i yönetici olarak açın ve şu komutları çalıştırın:


### Servisi Başlatma
powershell
python instagram_story_service.py start

### Servisi Durdurma
powershell
python instagram_story_service.py stop

### Servisi Kaldırma
powershell
python instagram_story_service.py remove


## Servis Özellikleri

- Windows başlangıcında otomatik çalışır
- Her dakika hikaye kontrolü yapar
- Hikaye bulunduğunda:
  - Windows bildirimi gönderir
  - Kosmos vize sayfasını açar
- Arka planda sessizce çalışır
- Windows Olay Günlüğü'ne kayıt tutar

## Log ve Durum Kontrolü

### Windows Hizmetleri
1. Windows + R tuşlarına basın
2. `services.msc` yazıp Enter'a basın
3. "Instagram Hikaye Takip Servisi"ni bulun

### Olay Görüntüleyici
1. Windows + R tuşlarına basın
2. `eventvwr.msc` yazıp Enter'a basın
3. Windows Günlükleri > Application altında logları görüntüleyin

## Kod Detayları

### instagram_story_checker.py

python
Ana kontrol sınıfı
class InstagramStoryChecker:
def init(self):
self.driver = None
self.wait = None
self.logged_in = False


### instagram_story_service.py

python
Windows servis sınıfı
class InstagramStoryService(win32serviceutil.ServiceFramework):
svc_name = "InstagramStoryService"
svc_display_name = "Instagram Hikaye Takip Servisi"


## Sorun Giderme

### Servis Başlatma Sorunları
- Kullanıcı bilgilerinin doğruluğunu kontrol edin
- Firefox ve geckodriver kurulumunu kontrol edin
- Windows Olay Görüntüleyici'den hata mesajlarını inceleyin

### Bildirim Sorunları
- Windows bildirim ayarlarını kontrol edin
- Servisin çalıştığından emin olun
- Olay Görüntüleyici'den logları kontrol edin

### Bağlantı Sorunları
- İnternet bağlantısını kontrol edin
- Instagram'ın erişilebilir olduğunu doğrulayın
- Proxy ayarlarını kontrol edin

## Güvenlik Notları

1. Kullanıcı bilgilerini güvenli bir şekilde saklayın
2. Instagram'ın bot algılama sistemine yakalanmamak için:
   - Çok sık kontrol yapmaktan kaçının
   - IP değişikliklerinde dikkatli olun
   - Şüpheli aktivitelerden kaçının

## Teknik Gereksinimler

- Python 3.x
- Windows 10/11
- Firefox tarayıcısı
- Yönetici hakları (servis kurulumu için)
- İnternet bağlantısı

## Lisans ve Sorumluluk Reddi

Bu yazılım eğitim amaçlıdır. Instagram'ın kullanım koşullarına ve politikalarına uygun kullanılmalıdır. Yazılımın kullanımından doğacak sorunlardan kullanıcı sorumludur.

Bu README.md dosyası projenin tüm detaylarını, kurulum adımlarını, kullanım talimatlarını ve sorun giderme bilgilerini içermektedir.