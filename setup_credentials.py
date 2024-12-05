from cryptography.fernet import Fernet
import os

def create_key():
    """Yeni bir şifreleme anahtarı oluşturur ve kaydeder"""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

def encrypt_credentials(username, password, key):
    """Kullanıcı adı ve şifreyi şifreler"""
    f = Fernet(key)
    credentials = f"{username}:{password}"
    encrypted_data = f.encrypt(credentials.encode())
    with open("encrypted_credentials.txt", "wb") as enc_file:
        enc_file.write(encrypted_data)

def decrypt_credentials(key):
    """Şifrelenmiş bilgileri çözer"""
    try:
        f = Fernet(key)
        with open("encrypted_credentials.txt", "rb") as enc_file:
            encrypted_data = enc_file.read()
        decrypted_data = f.decrypt(encrypted_data).decode()
        username, password = decrypted_data.split(":")
        return username, password
    except FileNotFoundError:
        raise Exception("Kaydedilmiş giriş bilgileri bulunamadı")
    except Exception as e:
        raise Exception(f"Giriş bilgileri çözülemedi: {str(e)}")

def load_key():
    """Şifreleme anahtarını yükler"""
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        raise Exception("Şifreleme anahtarı bulunamadı")
    except Exception as e:
        raise Exception(f"Anahtar yüklenemedi: {str(e)}")

def setup_credentials():
    """Kullanıcıdan bilgileri alır ve şifreler"""
    print("Instagram giriş bilgilerini ayarlama")
    print("-" * 30)
    
    username = input("Instagram kullanıcı adınız: ")
    password = input("Instagram şifreniz: ")
    
    # Şifreleme anahtarı oluştur
    key = create_key()
    
    # Bilgileri şifrele ve kaydet
    encrypt_credentials(username, password, key)
    
    print("\nGiriş bilgileri güvenli bir şekilde kaydedildi.")

if __name__ == "__main__":
    setup_credentials() 