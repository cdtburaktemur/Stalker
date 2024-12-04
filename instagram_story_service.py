import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import sys
import logging
from instagram_story_checker import InstagramStoryChecker

logging.basicConfig(
    filename="instagram_story_service.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class InstagramStoryService(win32serviceutil.ServiceFramework):
    _svc_name_ = "InstagramStoryService"
    _svc_display_name_ = "Instagram Hikaye Takip Servisi"
    _svc_description_ = "Instagram hikayelerini kontrol eden Windows servisi"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.checker = None

    def SvcStop(self):
        """Servis durdurma isteği geldiğinde çalışır"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        """Servis başlatıldığında çalışır"""
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        try:
            self.checker = InstagramStoryChecker()
            self.checker.setup_driver()

            if self.checker.login():
                logging.info("Instagram girişi başarılı, hikaye kontrol başlıyor...")

                # Ana kontrol döngüsü
                while win32event.WaitForSingleObject(self.stop_event, 1000) != win32event.WAIT_OBJECT_0:
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
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(InstagramStoryService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(InstagramStoryService)
