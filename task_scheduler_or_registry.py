import os
import sys
import subprocess
import winreg

def create_task_scheduler():
    """Windows Görev Zamanlayıcı'da bilgisayar açıldığında programı başlatmak için görev oluşturur"""
    try:
        python_path = sys.executable
        script_path = os.path.abspath(__file__)
        script_directory = os.path.dirname(script_path)
        main_script = os.path.join(script_directory, "main.py")

        task_name = "InstagramStoryCheckerTask"

        # Görev zamanlayıcı komutunu çalıştır
        subprocess.run([
            "schtasks", "/create", "/f",
            "/tn", task_name,
            "/tr", f'"{python_path}" "{main_script}"',
            "/sc", "onlogon",
            "/rl", "highest"
        ], check=True)

        print(f"{task_name} başarıyla oluşturuldu.")
    except subprocess.CalledProcessError as e:
        print(f"Görev oluşturulurken hata oluştu: {str(e)}")

def create_registry_key():
    """Kayıt Defteri'ne bilgisayar açıldığında programı başlatacak anahtar ekler"""
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key_value = "InstagramStoryChecker"

        python_path = sys.executable
        script_path = os.path.abspath(__file__)
        script_directory = os.path.dirname(script_path)
        main_script = os.path.join(script_directory, "main.py")
        value = f'"{python_path}" "{main_script}"'

        # Kayıt defterine anahtar ekle
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, key_value, 0, winreg.REG_SZ, value)

        print(f"{key_value} başarıyla kayıt defterine eklendi.")
    except Exception as e:
        print(f"Kayıt defteri anahtarı oluşturulurken hata oluştu: {str(e)}")

def main():
    choice = input("Bilgisayar açıldığında programı başlatmak için yöntem seçin (1: Görev Zamanlayıcı, 2: Kayıt Defteri): ")

    if choice == "1":
        create_task_scheduler()
    elif choice == "2":
        create_registry_key()
    else:
        print("Geçersiz seçim. Lütfen 1 veya 2 girin.")

if __name__ == "__main__":
    main()
