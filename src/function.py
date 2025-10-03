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
    {"title": "Любознательный", "min_points": 25, "background": "#FFFFFF"},
    {"title": "Активный участник", "min_points": 50, "background": "#FF5B5B"},
    {"title": "Эксперт", "min_points": 100, "background": "#9C9DFF"},
    {"title": "Мастер", "min_points": 200, "background": "#EF89FF"},
    {"title": "Гуру", "min_points": 500, "background": "#FF4BE7"},
]

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