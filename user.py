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

    def save(self):
        # Veritabanını aç
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Kullanıcıyı ekle
        cursor.execute('''INSERT INTO users (username, first_name, last_name, password)
                          VALUES (?, ?, ?, ?)''',
                       (self.username, self.first_name, self.last_name, self.password))

        # Değişiklikleri kaydet ve veritabanını kapat
        conn.commit()
        conn.close()

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
                'password': user[4]
                # Diğer kullanıcı özelliklerini ekleyebilirsiniz
            }
            user_list.append(user_dict)

        return user_list


        


# Örnek kullanıcılar ekleyelim
#user1 = User('johndoe', 'John', 'Doe', '123456')
#user2 = User('janedoe', 'Jane', 'Doe', 'abcdef')
#user3 = User('james.smith', 'James', 'Smith', 'qwerty')

#user1.save()
#user2.save()
#user3.save()

# Tüm kullanıcıları al ve ekrana yazdır
print(User.get_all_users())

# Veritabanı bağlantısını kapat
conn.close()
