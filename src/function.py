from requests import session
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import update
import hashlib
import json
import random
from functools import wraps
import base64
import init

levels = [
    {"title": "Новичок", "min_points": 0, "background": "#DBDBDB"},
    {"title": "Любознательный", "min_points": 1, "background": "#FFFFFF"},
    {"title": "Активный участник", "min_points": 2, "background": "#FF5B5B"},
    {"title": "Эксперт", "min_points": 20, "background": "#9C9DFF"},
    {"title": "Мастер", "min_points": 200, "background": "#EF89FF"},
    {"title": "Админ", "min_points": 500, "background": "#FF4BE7"},
]

def upgrade(id):
    with Session(init.engine) as session:
        user = session.execute(select(init.User).where(init.User.id == id)).scalar_one()
        if user:
            new_points = user.min_points + 1
            session.execute(
                update(init.User).where(init.User.id == id).values(min_points=new_points)
            )
        session.commit()


def upgrade_title(id):
    with Session(init.engine) as session:
        user = session.execute(select(init.User).where(init.User.id == id)).scalar_one()

        new_title = None
        new_background = None

        for level in levels:
            if user.min_points >= level["min_points"]:
                new_title = level["title"]
                new_background = level["background"]

        # если звание изменилось — обновляем
        if new_title and user.title != new_title:
            session.execute(
                update(init.User)
                .where(init.User.id == id)
                .values(title=new_title, background=new_background)
            )
            session.commit()

# кодирование пароля
def encrypt(text):
    return base64.b64encode(text.encode()).decode()

# декодирование пароля
def decrypt(encrypted_text):
    if not encrypted_text:
        return "Нельзя расшифровать None или пустую строку"
    return base64.b64decode(encrypted_text.encode()).decode()

# хэширование пароля
def hash_password(password):
    """хэширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()