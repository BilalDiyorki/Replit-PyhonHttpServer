from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
import base64

import sqlite3
import json

# Veritabanı bağlantısını oluştur
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Kullanıcı tablosunu oluştur
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    ozel_anahtar_base64 TEXT,
                    genel_anahtar_base64 TEXT,
                    password TEXT
                    )''')
conn.commit()


# Kullanıcı sınıfı
class User:

  def __init__(self, username, first_name, last_name, password):
    self.username = username
    self.first_name = first_name
    self.last_name = last_name
    self.password = password

    self.ozel_anahtar = rsa.generate_private_key(public_exponent=65537,
                                                 key_size=2048,
                                                 backend=default_backend())

    self.genel_anahtar = self.ozel_anahtar.public_key()

    # Özel anahtarı base64 formatına dönüştür
    self.ozel_anahtar_base64 = base64.b64encode(
      self.ozel_anahtar.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())).decode('utf-8')

    # Genel anahtarı base64 formatına dönüştür
    self.genel_anahtar_base64 = base64.b64encode(
      self.genel_anahtar.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)).decode(
          'utf-8')

    print(f" {self.username} kişisi için, anahtar çifti oluşturdu.")

  def save(self):
    # Veritabanını aç
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Kullanıcı tablosunu oluştur
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        first_name TEXT,
                        last_name TEXT,
                        ozel_anahtar_base64 TEXT,
                        genel_anahtar_base64 TEXT,
                        password TEXT
                        )''')
    conn.commit()

    print("users tablosu oluşturuldu.")

    # Kullanıcıyı ekle
    cursor.execute(
      '''INSERT INTO users (username, first_name, last_name, ozel_anahtar_base64, genel_anahtar_base64, password)
                          VALUES (?, ?, ?, ?, ?, ?)''',
      (self.username, self.first_name, self.last_name,
       self.ozel_anahtar_base64, self.genel_anahtar_base64, self.password))

    # Değişiklikleri kaydet ve veritabanını kapat
    conn.commit()
    conn.close()

  def get_genel_anahtar(self):
    return self.genel_anahtar

  def get_genel_anahtar_decode(self):
    # Genel anahtarı base64 formatından geri dönüştürme
    genel_anahtar_bytes = base64.b64decode(self.genel_anahtar_base64)
    genel_anahtar = serialization.load_pem_public_key(
      genel_anahtar_bytes, backend=default_backend())
    return genel_anahtar

  def get_ozel_anahtar_decode(self):
    # Özel anahtarı base64 formatından geri dönüştürme
    ozel_anahtar_bytes = base64.b64decode(self.ozel_anahtar_base64)
    ozel_anahtar = serialization.load_pem_private_key(
      ozel_anahtar_bytes, password=None, backend=default_backend())
    return ozel_anahtar

  def kaydet_genel_anahtar(self):
    dosya_adi = f"{self.username}_genel_anahtar.pem"
    with open(dosya_adi, "wb") as dosya:
      dosya.write(
        self.genel_anahtar.public_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PublicFormat.SubjectPublicKeyInfo))

  # Mesajı imzalama işlemi
  def imza_olustur(self, dosya_adi):
    with open(dosya_adi, "rb") as dosya:
      icerik = dosya.read()
      imza = self.ozel_anahtar.sign(
        icerik,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
      print(f"Gönderici {self.username}, mesajı imzaladı.")
      return imza

  # İmza doğrulama işlemi
  def imza_dogrula(self, gonderen_genel_anahtari, imza, dosya_adi):
    with open(dosya_adi, "rb") as dosya:
      icerik = dosya.read()
      try:
        gonderen_genel_anahtari.verify(
          imza, icerik,
          padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                      salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        print(f"{self.username} kişisi, imza doğruladı")
        return True
      except:
        print(f"{self.username} kişisi, imza doğrulama hatası.")
        return False

  def mesaj_sifrele_ve_kaydet(self, alicinin_genel_anahtari, alici_isim,
                              dosya_adi):
    with open(dosya_adi, "rb") as dosya:
      icerik = dosya.read()
      sifrelenmis_mesaj = alicinin_genel_anahtari.encrypt(
        icerik,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None))

      sifreli_dosya_adi = f"{alici_isim}_sifreli_mesaj.txt"
      with open(sifreli_dosya_adi, "wb") as sifreli_dosya:
        sifreli_dosya.write(sifrelenmis_mesaj)

      print(f"Mesaj şifrelendi ve '{sifreli_dosya_adi}' dosyasına kaydedildi.")

  def mesaj_coz_ve_kaydet(self):
    sifreli_dosya_adi = f"{self.username}_sifreli_mesaj.txt"
    with open(sifreli_dosya_adi, "rb") as sifreli_dosya:
      sifrelenmis_mesaj = sifreli_dosya.read()
      cozulmus_mesaj = self.ozel_anahtar.decrypt(
        sifrelenmis_mesaj,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None))
      cozulmus_dosya_adi = f"{self.username}_cozulmus_mesaj.txt"
      with open(cozulmus_dosya_adi, "wb") as cozulmus_dosya:
        cozulmus_dosya.write(cozulmus_mesaj)

      print(
        f"Şifreli mesaj çözüldü ve '{cozulmus_dosya_adi}' dosyasına kaydedildi."
      )

  @staticmethod
  def get_all_users():
    # Veritabanını aç
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Tüm kullanıcıları al
    cursor.execute('''SELECT * FROM users''')
    users = cursor.fetchall()

    # Veritabanını kapat
    conn.close()

    # Her bir kullanıcıyı bir sözlük içinde sakla
    user_list = []
    for user in users:
      user_dict = {
        'id': user[0],
        'username': user[1],
        'first_name': user[2],
        'last_name': user[3],
        'ozel_anahtar_base64': user[4],
        'genel_anahtar_base64': user[5],
        'password': user[6]
        # Diğer kullanıcı özelliklerini ekleyebilirsiniz
      }
      user_list.append(user_dict)

    return user_list


# Tüm kullanıcıları al ve ekrana yazdır
print(User.get_all_users())

# Veritabanı bağlantısını kapat
conn.close()
