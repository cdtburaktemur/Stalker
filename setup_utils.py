import os
import sys
import shutil
import winshell
from win32com.client import Dispatch

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

        print(f"Program başarıyla {target_dir} dizinine kopyalandı.")
    except Exception as e:
        print(f"Program Files dizinine kopyalama sırasında hata oluştu: {str(e)}")

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
        shortcut.Targetpath = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "InstagramStoryChecker", "main.py")
        shortcut.WorkingDirectory = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "InstagramStoryChecker")
        shortcut.IconLocation = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "InstagramStoryChecker", "icon.ico")  # Icon dosyan varsa
        shortcut.save()

        print("Başlat menüsüne kısayol başarıyla oluşturuldu.")
    except Exception as e:
        print(f"Kısayol oluşturma sırasında hata oluştu: {str(e)}")

def main():
    # Tek seferlik işlemler için bayrak dosyasını kontrol et
    if not os.path.exists(FLAG_FILE):
        copy_to_program_files()
        create_start_menu_shortcut()

        # Bayrak dosyasını oluştur
        with open(FLAG_FILE, "w") as flag:
            flag.write("Setup işlemleri tamamlandı.")
        print(f"Tek seferlik işlemler yapıldı ve bayrak dosyası oluşturuldu.")
    else:
        print("Daha önce kurulum yapılmış, bu nedenle işlem yapılmadı.")

if __name__ == "__main__":
    main()
