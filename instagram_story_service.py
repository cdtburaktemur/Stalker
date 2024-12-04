import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import sys
from instagram_story_checker import InstagramStoryChecker

class InstagramStoryService(win32serviceutil.ServiceFramework):
    _svc_name_ = "InstagramStoryService"
    _svc_display_name_ = "Instagram Hikaye Takip Servisi"
    _svc_description_ = "Instagram hikayelerini kontrol eden Windows servisi"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.checker = None
        self.username = "KULLANICI_ADI"  # Instagram kullanıcı adınız
        self.password = "SIFRE"          # Instagram şifreniz
        self.target_username = "TAKIP_EDILECEK_KULLANICI"  # Takip edilecek kullanıcı

    def SvcStop(self):
        """Servis durdurma isteği geldiğinde çalışır"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.checker:
            self.checker.close()

    def SvcDoRun(self):
        """Servis başlatıldığında çalışır"""
        try:
            self.checker = InstagramStoryChecker()
            self.checker.setup_driver()
            
            if self.checker.login(self.username, self.password):
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STARTED,
                    (self._svc_name_, 'Instagram girişi başarılı')
                )
                
                # Ana kontrol döngüsü
                while True:
                    # Durma sinyali geldi mi kontrol et
                    if win32event.WaitForSingleObject(self.stop_event, 0) == win32event.WAIT_OBJECT_0:
                        break
                        
                    try:
                        # Hikaye kontrolü yap
                        self.checker.check_user_story(self.target_username)
                    except Exception as e:
                        servicemanager.LogErrorMsg(f"Hikaye kontrol hatası: {str(e)}")
                        
                    # 60 saniye bekle
                    time.sleep(60)
                    
            else:
                servicemanager.LogErrorMsg("Instagram girişi başarısız!")
                
        except Exception as e:
            servicemanager.LogErrorMsg(f"Servis hatası: {str(e)}")
        finally:
            if self.checker:
                self.checker.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(InstagramStoryService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(InstagramStoryService) 