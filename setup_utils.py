import os
import sys
import shutil
import winshell
from win32com.client import Dispatch
import logging

FLAG_FILE = "setup_done.flag"  # Tek seferlik işlemler için kullanılacak bayrak dosyası

def copy_to_program_files():
    """Program Files altında bir dizin oluşturur ve scripti oraya kopyalar"""
    try:
        # Program Files dizinini al
        program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        target_dir = os.path.join(program_files, "InstagramStoryChecker")

        # Eğer dizin yoksa oluştur
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Şu anki scriptin bulunduğu dizin ve hedef dizin
        current_script = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_script)

        # Tüm dosyaları hedef dizine kopyala
        for item in os.listdir(current_directory):
            source = os.path.join(current_directory, item)
            destination = os.path.join(target_dir, item)
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(source, destination)

        logging.info(f"Program başarıyla {target_dir} dizinine kopyalandı.")
        return True
    except Exception as e:
        logging.error(f"Program Files dizinine kopyalama sırasında hata oluştu: {str(e)}")
        return False

def create_start_menu_shortcut():
    """Başlat menüsüne kısayol oluşturur"""
    try:
        # Başlat menüsü dizinini al
        start_menu = winshell.start_menu()
        shortcut_path = os.path.join(start_menu, "InstagramStoryChecker.lnk")

        # Program Files'taki ana dizin ve ikonun yolu
        program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        target_dir = os.path.join(program_files, "InstagramStoryChecker")
        icon_path = os.path.join(target_dir, "icon.ico")

        # Kısayol oluştur
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = os.path.join(target_dir, "main.py")
        shortcut.WorkingDirectory = target_dir
        shortcut.IconLocation = icon_path
        shortcut.save()

        logging.info("Başlat menüsüne kısayol başarıyla oluşturuldu.")
        return True
    except Exception as e:
        logging.error(f"Kısayol oluşturma sırasında hata oluştu: {str(e)}")
        return False

def create_startup_shortcut():
    """Windows başlangıcında çalıştırmak için kısayol oluşturur"""
    try:
        # Başlangıç klasörünü al
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "InstagramStoryChecker.lnk")

        # Program Files'taki yol
        program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        target_dir = os.path.join(program_files, "InstagramStoryChecker")
        icon_path = os.path.join(target_dir, "icon.ico")

        # Kısayol oluştur
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = os.path.join(target_dir, "main.py")
        shortcut.WorkingDirectory = target_dir
        shortcut.IconLocation = icon_path
        shortcut.save()

        logging.info("Başlangıç klasörüne kısayol başarıyla oluşturuldu.")
        return True
    except Exception as e:
        logging.error(f"Başlangıç kısayolu oluşturma sırasında hata oluştu: {str(e)}")
        return False

def main():
    """Tüm kurulum işlemlerini gerçekleştirir"""
    success = True
    
    # Program Files'a kopyala
    if not copy_to_program_files():
        success = False
        
    # Başlat menüsü kısayolu oluştur
    if not create_start_menu_shortcut():
        success = False
        
    # Başlangıç kısayolu oluştur
    if not create_startup_shortcut():
        success = False
        
    # Bayrak dosyasını oluştur
    if success:
        with open(FLAG_FILE, "w") as flag:
            flag.write("Setup işlemleri tamamlandı.")
        logging.info("Kurulum işlemleri başarıyla tamamlandı.")
    else:
        logging.error("Kurulum işlemleri sırasında hatalar oluştu.")
        
    return success

if __name__ == "__main__":
    main()
