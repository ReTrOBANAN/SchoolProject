from fastapi import FastAPI, Request, Form, Response, requests, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime

from requests import session
from sqlalchemy import delete, and_, update
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import update

import init
import function
import sqlite3
import uvicorn
import uuid

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

app = FastAPI()
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

levels = [
    {"title": "Новичок", "min_points": 0, "background": "#DBDBDB"},
    {"title": "Любознательный", "min_points": 25, "background": "#FFFFFF"},
    {"title": "Активный участник", "min_points": 50, "background": "#B5FF8A"},
    {"title": "Эксперт", "min_points": 100, "background": "#9C9DFF"},
    {"title": "Мастер", "min_points": 200, "background": "#EF89FF"},
    {"title": "Гуру", "min_points": 500, "background": "#FF4BE7"},
]

@app.get("/logout", tags="Выход")
async def logout(request: Request):
    # Создаем редирект-ответ
    redirect = RedirectResponse(url="/", status_code=303)
    # Устанавливаем куки
    redirect.delete_cookie(key="id")
    redirect.delete_cookie(key="name")
    redirect.delete_cookie(key="username")
    return redirect

@app.get("/register", tags="Регистрация")
async def register(request: Request):
    if request.cookies.get("id"):
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("register.html", {"request": request})

@app.post("/doregister", tags="Регистрация")
async def doregister(
    request: Request,
    name: str = Form(...),
    login: str = Form(...),
    email: str = Form(...),
):
    # Валидация email
    if not function.is_valid_email(email):
        return JSONResponse({"error": "Неверный формат email"}, status_code=400)
    
    # Проверяем существование пользователя
    error = function.check_user_exists(login, email)
    if error:
        return JSONResponse({"error": error}, status_code=400)
    
    # Генерируем код
    code = function.generate_code()
    print(code)
    
    # Сохраняем данные во временное хранилище
    if not function.save_registration_data(email, name, login, code):
        return JSONResponse({"error": "Ошибка сохранения данных"}, status_code=500)
    
    # Отправляем код
    if not function.send(email, code):
        function.delete_registration_data(email)  # Удаляем данные если отправка не удалась
        return JSONResponse({"error": "Ошибка отправки email"}, status_code=500)
    
    redirect = RedirectResponse(url="/emailregister", status_code=303)
    redirect.set_cookie(key="verification_email", value=email, httponly=True, max_age=600)  # 10 минут
    return redirect

@app.get("/emailregister", tags="Регистрация")
async def email_verification_page(request: Request):
    return templates.TemplateResponse("email.html", {"request": request})

@app.post("/doemailregister", tags="Регистрация")
async def doemailregister(
    request: Request,
    code: str = Form(...),
):
    email = request.cookies.get("verification_email")
    
    if not email:
        return JSONResponse({"error": "Сессия истекла. Пройдите регистрацию заново."}, status_code=400)
    
    # Проверяем код и получаем данные регистрации
    user_data = function.is_code_valid(email, code)
    if not user_data:
        return JSONResponse({"error": "Неверный или просроченный код"}, status_code=400)
    
    # Создаем пользователя в базе данных
    user = function.create_user(
        name=user_data['name'],
        login=user_data['login'],
        email=email
    )
    
    if not user:
        return JSONResponse({"error": "Ошибка создания пользователя"}, status_code=500)
    
    # Удаляем использованные данные
    function.delete_registration_data(email)
    
    # Успешная регистрация
    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie(key="id", value=str(user.id))
    redirect.set_cookie(key="name", value=function.encrypt(user.name))
    redirect.set_cookie(key="username", value=function.encrypt(user.username))
    redirect.delete_cookie("verification_email")
    
    return redirect

@app.get("/login", tags="Логин")
async def login(request: Request):
    if request.cookies.get("id"):
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

@app.post("/dologin", tags="Логин")
async def dologin(
    request: Request,
    auth: str = Form(...),  # Логин или email
):
    with Session(init.engine) as conn:
        # Ищем пользователя по логину или email
        stmt = select(init.User).where(
            (init.User.username == auth) | (init.User.email == auth)
        )
        data = conn.execute(stmt).first()
        
        if not data:
            return JSONResponse({"error": "Пользователь не найден"}, status_code=400)
        
        user = data[0]
        email = user.email
        
        # Генерируем код (используем существующую функцию)
        code = function.generate_code()
        
        # Сохраняем данные для логина во временное хранилище
        # Используем ту же функцию, но с другим префиксом в ключе
        login_key = f"login_{email}"
        if not function.save_registration_data(login_key, user.name, user.username, code):
            return JSONResponse({"error": "Ошибка сохранения данных"}, status_code=500)
        
        # Отправляем код (существующая функция)
        if not function.send(email, code):
            function.delete_registration_data(login_key)
            return JSONResponse({"error": "Ошибка отправки email"}, status_code=500)
    
    redirect = RedirectResponse(url="/emaillogin", status_code=303)
    redirect.set_cookie(key="login_email", value=email, httponly=True, max_age=600)
    return redirect

@app.get("/emaillogin", tags="Логин")
async def email_login_page(request: Request):
    return templates.TemplateResponse("emaillogin.html", {"request": request})

@app.post("/doemaillogin", tags="Логин")
async def doemaillogin(
    request: Request,
    code: str = Form(...),
):
    email = request.cookies.get("login_email")
    
    if not email:
        return JSONResponse({"error": "Сессия истекла. Пройдите авторизацию заново."}, status_code=400)
    
    # Проверяем код (используем существующую функцию с префиксом)
    login_key = f"login_{email}"
    user_data = function.is_code_valid(login_key, code)
    if not user_data:
        return JSONResponse({"error": "Неверный или просроченный код"}, status_code=400)
    
    # Получаем ID пользователя из базы
    with Session(init.engine) as conn:
        stmt = select(init.User).where(init.User.email == email)
        user = conn.execute(stmt).first()
        
        if not user:
            return JSONResponse({"error": "Пользователь не найден"}, status_code=400)
    
    # Удаляем использованные данные
    function.delete_registration_data(login_key)
    
    # Успешная авторизация
    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie(key="id", value=str(user[0].id))
    redirect.set_cookie(key="name", value=function.encrypt(user[0].name))
    redirect.set_cookie(key="username", value=function.encrypt(user[0].username))
    redirect.delete_cookie("login_email")
    
    return redirect

@app.get("/add", tags="Добавить вопрос")
async def add(request: Request):
    if request.cookies.get("id"):
        return templates.TemplateResponse("add_question.html", {"request": request})
    else:
        return RedirectResponse(url="/login", status_code=303)

@app.post("/doadd", tags=["Добавить вопрос"])
async def doadd(
    request: Request,
    subject: str = Form(...),
    grade: str = Form(...),
    description: str = Form(...),
):
    try:
        with Session(init.engine) as conn:
            question = init.Question(
                owner=function.decrypt(request.cookies.get("username")),
                owner_name=function.decrypt(request.cookies.get("name")),
                subject=subject,
                grade=grade,
                description=description,
            )
            conn.add(question)
            conn.commit()  # Важно: commit после добавления
            function.upgrade(request.cookies.get("id"))
            function.upgrade_title(request.cookies.get("id"))
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        print(f"Ошибка при добавлении вопроса: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)

@app.get("/api/answers", tags=["API"])
async def get_answers():
    with Session(init.engine) as conn:
        stmt = select(
            init.Comment.id,
            init.Comment.question_id,
            init.Comment.owner,
            init.Comment.description,
            init.Comment.created_at,
        ).order_by(init.Comment.id.desc())
        data = conn.execute(stmt).fetchall()

        questions = []
        for row in data:
            stmt = select(init.User.name).where(init.User.username == row.owner)
            data = conn.execute(stmt).fetchall()
            questions.append({
                "id": row.id,
                "question_id": row.question_id,
                "name": data[0].name,
                "username": row.owner,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })
        return JSONResponse(content=questions)

@app.get("/api/questions", tags=["API"])
async def get_questions():
    with Session(init.engine) as conn:
        stmt = select(
            init.Question.id,
            init.Question.owner,
            init.Question.owner_name,
            init.Question.subject,
            init.Question.grade,
            init.Question.description,
            init.Question.created_at,
        ).order_by(init.Question.id.desc())
        data = conn.execute(stmt).fetchall()

        questions = []
        for row in data:
            questions.append({
                "id": row.id,
                "username": row.owner,
                "name": row.owner_name,
                "subject": row.subject,  
                "grade": row.grade,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })
        return JSONResponse(content=questions)
    
@app.get("/api/users", tags=["API"])
async def get_questions():
    with Session(init.engine) as conn:
        stmt = select(
            init.User.min_points,
            init.User.username,
            init.User.background,
            init.User.title,
        )
        data = conn.execute(stmt).fetchall()

        questions = []
        for row in data:
            questions.append({
                "min_points": row.min_points,
                "username": row.username,
                "background": data[0].background,
                "title": row.title,
            })
        return JSONResponse(content=questions)

@app.get("/", tags="Главная")
async def main(request: Request):
        if request.cookies.get("id"):
            return templates.TemplateResponse("main.html", {"request": request,
                                                            "username": function.decrypt(request.cookies.get("username")),
                                                            "name": function.decrypt(request.cookies.get("name")),})
        else:
            return templates.TemplateResponse("main.html", {"request": request,
                                                            "username": None,
                                                            "name": None,})  
 
@app.get("/question/{note_id}", tags=["Страница вопроса"])
async def question_page(request: Request, note_id: int):
    if request.cookies.get("id"):
        with Session(init.engine) as conn:
            # Получаем вопрос
            stmt = select(
                init.Question.owner,
                init.Question.owner_name,
                init.Question.subject,
                init.Question.grade,
                init.Question.description,
                init.Question.id,
                init.Question.created_at,
            ).where(init.Question.id == note_id)
            question_data = conn.execute(stmt).fetchone()
            
            if not question_data:
                return RedirectResponse(url="/", status_code=303)
                
            result = [
                question_data.owner,
                question_data.owner_name,
                question_data.subject,
                question_data.grade,
                question_data.description,
                question_data.id,
                question_data.created_at
            ]
            
        with Session(init.engine) as conn:
            # Получаем комментарии
            stmt = select(
                init.Comment.owner,
                init.Comment.description
            ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
            comment_data = conn.execute(stmt).fetchall()
            
            comments = [
                {"owner": row.owner, "description": row.description}
                for row in comment_data
            ]
        
        return templates.TemplateResponse("answer.html", {
            "username": function.decrypt(request.cookies.get("username")),
            "name": function.decrypt(request.cookies.get("name")),
            "request": request,
            "result": result,
            "comments": comments,
        })
    
    else:
        with Session(init.engine) as conn:
            # Получаем вопрос
            stmt = select(
                init.Question.owner,
                init.Question.owner_name,
                init.Question.subject,
                init.Question.grade,
                init.Question.description,
                init.Question.id,
                init.Question.created_at,
            ).where(init.Question.id == note_id)
            question_data = conn.execute(stmt).fetchone()
            
            if not question_data:
                return RedirectResponse(url="/", status_code=303)
                
            result = [
                question_data.owner,
                question_data.owner_name,
                question_data.subject,
                question_data.grade,
                question_data.description,
                question_data.id,
                question_data.created_at
            ]
            
            # Получаем комментарии
            stmt = select(
                init.Comment.owner,
                init.Comment.description
            ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
            comment_data = conn.execute(stmt).fetchall()
            
            comments = [
                {"owner": row.owner, "description": row.description}
                for row in comment_data
            ]
        
        return templates.TemplateResponse("answer.html", {
            "request": request,
            "result": result,
            "comments": comments,
        })

    
@app.post("/addcomment", tags="Добавить комментарий")
async def addcomment(
    request: Request,
    comment: str = Form(...),
    id: int = Form(...),
):
    print(comment, id)
    with Session(init.engine) as conn:
        comments = init.Comment(
            question_id=id,
            owner=function.decrypt(request.cookies.get("username")),
            description=comment,
        )
        conn.add(comments)
        conn.commit()
        function.upgrade(request.cookies.get("id"))
        function.upgrade_title(request.cookies.get("id"))
        return RedirectResponse(url=f'/question/{id}', status_code=303)
    
@app.get("/profile/{username}", tags=["Профиль"])
async def profile(request: Request, username: str):
    with Session(init.engine) as conn:
            stmt = select(
                init.User.id,
                init.User.name,
                init.User.title,
                init.User.background,
            ).where(init.User.username == username)
            data = conn.execute(stmt).fetchall()
            account = [data[0].id, data[0].name, username, data[0].title, data[0].background]
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "account": account}
    )

@app.post("/delete", tags=["Удаление вопроса"])
async def delete_question(
    request: Request,
    description: str = Form(...),
    owner: str = Form(...),
    id: int = Form(...),
):
    print(description, owner)
    current_user = function.decrypt(request.cookies.get("username"))
    
    if current_user == owner:
        with Session(init.engine) as session:
            # Правильное использование delete
            stmt = delete(init.Question).where(
                    init.Question.description == description,
                    init.Question.owner == current_user,
                    init.Question.id == id,
            )
            session.execute(stmt)
            stmt = delete(init.Comment).where(
                init.Comment.question_id == id,
            )
            session.execute(stmt)
            session.commit()  # Не забывайте скобки!
        
        return RedirectResponse("/", status_code=303)    
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/change", tags=["Изменение вопроса"])
async def change_question(
    request: Request,
    description: str = Form(...),
    new_description: str = Form(...),
    owner: str = Form(...),
    grade: str = Form(...),
    subject: str = Form(...),
    id: str = Form(...),
):
    print(f"Старое описание: {description}, Новое описание: {new_description}, Владелец: {owner}")
    current_user = function.decrypt(request.cookies.get("username"))
    
    # Проверка прав доступа
    if current_user != owner:
        return RedirectResponse("/", status_code=303)
    
    # Валидация новых данных
    if not new_description.strip():
        # Новое описание пустое
        return RedirectResponse("/", status_code=303)
    
    if new_description.strip() == description.strip():
        # Описание не изменилось
        return RedirectResponse("/", status_code=303)
    
    # Дополнительная проверка: убедимся, что вопрос действительно существует
    # и принадлежит пользователю
    with Session(init.engine) as session:
        # Сначала находим вопрос
        question = session.get(init.Question, id)
        
        if not question:
            # Вопрос не найден
            return RedirectResponse("/", status_code=303)
        
        if question.owner != current_user:
            # Вопрос не принадлежит пользователю
            return RedirectResponse("/", status_code=303)
        
        # Обновляем вопрос
        stmt = update(init.Question).where(
            init.Question.id == id,
            init.Question.owner == current_user  # Дополнительная защита
        ).values(
            description=new_description.strip(),  # Убираем лишние пробелы
            grade=grade,
            subject=subject
            # owner не меняем, он остается тем же
        )
        
        session.execute(stmt)
        session.commit()
    
    return RedirectResponse("/", status_code=303)

@app.post("/delete_answers", tags=["Удаление вопроса"])
async def delete_answers(
    request: Request,
    description: str = Form(...),
    owner: str = Form(...),
    id: int = Form(...),
):
    print(description, owner)
    current_user = function.decrypt(request.cookies.get("username"))
    
    if current_user == owner:
        with Session(init.engine) as session:
            # Правильное использование delete
            stmt = delete(init.Comment).where(
                    init.Comment.description == description,
                    init.Comment.owner == current_user,
                    init.Comment.id == id,
            )
            session.execute(stmt)
            session.commit()  # Не забывайте скобки!
        
        return RedirectResponse("/", status_code=303)    
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/change_answer", tags=["Изменение вопроса"])
async def change_answer(
    request: Request,
    description: str = Form(...),
    new_description: str = Form(...),
    owner: str = Form(...),
    id: str = Form(...),
):
    current_user = function.decrypt(request.cookies.get("username"))
    
    # Проверка прав доступа
    if current_user != owner:
        return RedirectResponse("/", status_code=303)
    
    # Валидация новых данных
    if not new_description.strip():
        # Новое описание пустое
        return RedirectResponse("/", status_code=303)
    
    if new_description.strip() == description.strip():
        # Описание не изменилось
        return RedirectResponse("/", status_code=303)
    
    # Дополнительная проверка: убедимся, что вопрос действительно существует
    # и принадлежит пользователю
    with Session(init.engine) as session:
        # Сначала находим вопрос
        question = session.get(init.Comment, id)
        
        if not question:
            # Вопрос не найден
            return RedirectResponse("/", status_code=303)
        
        if question.owner != current_user:
            # Вопрос не принадлежит пользователю
            return RedirectResponse("/", status_code=303)
        
        # Обновляем вопрос
        stmt = update(init.Question).where(
            init.Question.id == id,
            init.Question.owner == current_user  # Дополнительная защита
        ).values(
            description=new_description.strip(),  # Убираем лишние пробелы
            # owner не меняем, он остается тем же
        )
        
        session.execute(stmt)
        session.commit()
    
    return RedirectResponse("/", status_code=303)

@app.post("/douserupload")
async def douserupload(
        request: Request,
        name: str =  Form(...),
        image: UploadFile = File(...)
):
    if request.cookies.get("id") != "1":
        return RedirectResponse(url="/", status_code=303)
    unique_filename = f"{uuid.uuid4()}_{image.filename}"

    # Полный путь для сохранения (например: static/uploads/abc123_image.jpg)
    file_path = UPLOAD_DIR / unique_filename

    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        # Читаем содержимое загруженного файла и записываем в новый файл
        buffer.write(await image.read())

    # Закрываем загруженный файл (важно!)
    await image.close()

    db_image_path = unique_filename


    with sqlite3.connect("kb.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, image_path) VALUES (?,?)",
                       (name, db_image_path))
        conn.commit()

    # Возвращаем пользователя на главную страницу
    return RedirectResponse(url="/", status_code=303)

@app.get("/upload", tags=["Загрузить аву"])
async def upload_form(request: Request):
    return templates.TemplateResponse(
        "add_ava.html", 
        {"request": request}
    )

if __name__ == "__main__":
    init.Base.metadata.create_all(init.engine)
    uvicorn.run("main:app", reload=True)