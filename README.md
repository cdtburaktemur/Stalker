# Instagram Hikaye Takipçisi

Instagram'da belirtilen kullanıcının hikayelerini otomatik olarak kontrol eden ve yeni hikaye paylaşıldığında bildirim gönderen bir Python uygulaması.

## Özellikler

- Instagram hesabına otomatik giriş
- İki faktörlü doğrulama desteği
- Belirli aralıklarla hikaye kontrolü (1-30 dakika arası ayarlanabilir)
- Windows bildirim sistemi entegrasyonu
- Sistem tepsisinde çalışabilme
- Şifrelenmiş giriş bilgileri saklama
- Görsel ilerleme çubuğu ve durum bildirimleri
- Şifre görünürlük kontrolü

## Kurulum

1. Gerekli Python paketlerini yükleyin:

```bash
pip install selenium
```

```bash
pip install selenium winotify cryptography PyQt5
```

2. Firefox ve Geckodriver'ı yükleyin:
   - [Firefox'u buradan indirin](https://www.mozilla.org/firefox/new/)
   - [Geckodriver'ı buradan indirin](https://github.com/mozilla/geckodriver/releases)
   - Geckodriver'ı Python Scripts klasörüne kopyalayın

## Kullanım

1. Programı başlatın:

```bash
python main.py 
``` 

2. Instagram giriş bilgilerinizi ve takip edilecek kullanıcı adını girin
3. Kontrol aralığını seçin (1-30 dakika)
4. "Takibi Başlat" butonuna tıklayın

Program sistem tepsisinde çalışmaya devam edecek ve yeni hikaye paylaşıldığında bildirim gönderecektir.

## Güvenlik

- Giriş bilgileri yerel olarak şifrelenerek saklanır
- Şifreler açık metin olarak tutulmaz
- İki faktörlü doğrulama desteklenir

## Notlar

- Program çalışırken pencereyi kapatırsanız, sistem tepsisinde çalışmaya devam eder
- Sistem tepsisi ikonuna çift tıklayarak pencereyi tekrar açabilirsiniz
- "Takibi Durdur" butonu ile programı durdurabilirsiniz

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

