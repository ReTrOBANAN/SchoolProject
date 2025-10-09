import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import select, update
from sqlalchemy.orm import Session
import hashlib
import json
import random
import base64
import init
from datetime import datetime, timedelta

levels = [
    {"title": "Новичок", "min_points": 0, "background": "#DBDBDB"},
    {"title": "Любознательный", "min_points": 25, "background": "#FFFFFF"},
    {"title": "Активный участник", "min_points": 50, "background": "#FF5B5B"},
    {"title": "Эксперт", "min_points": 100, "background": "#9C9DFF"},
    {"title": "Мастер", "min_points": 200, "background": "#EF89FF"},
    {"title": "Гуру", "min_points": 500, "background": "#FF4BE7"},
]

letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# Временное хранилище для данных регистрации и кодов
registration_data = {}

def send(email, code):
    email_address = 'nobo0000x@mail.ru'
    email_password = 'V1GiVQ6tXZEOsrlpLyRc'

    recipient_email = email
    subject = 'Код для School Space'
    message_body = f'Здравствуйте!\n\nВаш код подтверждения: {code}\n\nСообщение сгенерировано автоматически и не требует ответа.'

    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))

        print("Пытаемся подключиться к серверу...")
        
        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.login(email_address, email_password)
        server.send_message(msg)
        server.quit()
        
        print("Письмо успешно отправлено!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Ошибка аутентификации: {e}")
        return False
        
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False

def generate_code():
    """Генерирует 6-значный код"""
    return ''.join(random.choice(letter) for _ in range(6))

def save_registration_data(email, name, login, code):
    """Сохраняет данные регистрации во временное хранилище"""
    registration_data[email] = {
        'name': name,
        'login': login,
        'code': code,
        'created_at': datetime.now()
    }
    print(f"Сохранены данные для {email}: код {code}")
    return True

def get_registration_data(email):
    """Получает данные регистрации"""
    if email in registration_data:
        data = registration_data[email]
        # Проверяем не истек ли код (10 минут)
        if datetime.now() - data['created_at'] < timedelta(minutes=10):
            return data
        else:
            # Удаляем просроченные данные
            del registration_data[email]
    return None

def delete_registration_data(email):
    """Удаляет данные регистрации"""
    if email in registration_data:
        del registration_data[email]
        return True
    return False

def is_code_valid(email, code):
    """Проверяет валидность кода"""
    data = get_registration_data(email)
    if data and data['code'] == code:
        return data  # Возвращаем данные для создания пользователя
    return None

def create_user(name, login, email):
    """Создает пользователя в базе данных"""
    with Session(init.engine) as conn:
        user = init.User(
            name=name,
            username=login,
            email=email,
            title="Новичок",
            background="#DBDBDB",
            min_points=0
        )
        conn.add(user)
        conn.commit()
        
        # Получаем ID созданного пользователя
        stmt = select(init.User).where(init.User.email == email)
        user_data = conn.execute(stmt).first()
        return user_data[0] if user_data else None

def upgrade(id):
    with Session(init.engine) as session:
        stmt = select(init.User).where(init.User.id == id)
        user = session.execute(stmt).scalar_one()
        if user:
            new_level = user.min_points + 1
            stmt = update(init.User).where(init.User.id == id).values(min_points=new_level)
            session.execute(stmt)
        session.commit()

def upgrade_title(id):
    with Session(init.engine) as session:
        stmt = select(init.User).where(init.User.id == id)
        user = session.execute(stmt).scalar_one()
        
        new_title = None
        new_background = None

        for i in reversed(levels):
            if user.min_points >= i["min_points"] and user.title != i["title"]:
                new_title = i["title"]
                new_background = i["background"]
                break
        
        if new_title:
            stmt = update(init.User).where(init.User.id == id).values(
                title=new_title, 
                background=new_background
            )
            session.execute(stmt)
            session.commit()

def encrypt(text):
    """Кодирование текста в base64"""
    return base64.b64encode(text.encode()).decode()

def decrypt(encrypted_text):
    """Декодирование текста из base64"""
    if not encrypted_text:
        return ""
    try:
        return base64.b64decode(encrypted_text.encode()).decode()
    except:
        return ""

def hash_password(password):
    """Хэширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Простая проверка email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_user_exists(login, email):
    """Проверяет существование пользователя с таким логином или email"""
    with Session(init.engine) as conn:
        # Проверяем логин
        stmt = select(init.User).where(init.User.username == login)
        if conn.execute(stmt).first():
            return "Пользователь с таким логином уже есть"
        
        # Проверяем email
        stmt = select(init.User).where(init.User.email == email)
        if conn.execute(stmt).first():
            return "Пользователь с такой почтой уже есть"
    
    return None