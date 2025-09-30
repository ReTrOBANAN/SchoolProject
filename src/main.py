from fastapi import FastAPI, Request, Form, Response, requests
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime

from requests import session
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import update

import init
import function
import sqlite3
import uvicorn

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

levels = [
    {"title": "Новичок", "min_points": 0, "background": "#DBDBDB"},
    {"title": "Любознательный", "min_points": 25, "background": "#FFFFFF"},
    {"title": "Активный участник", "min_points": 50, "background": "#FF5B5B"},
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
    password: str = Form(...),
):
    with Session(init.engine) as conn:
        stmt = select(init.User).where(init.User.username == login)
        data = conn.execute(stmt).fetchall()
        if data:
            return JSONResponse({"error": "Пользователь с таким логином уже есть"}, status_code=400)

        else:
            user = init.User(
                name=name,
                username=login,
                password=function.hash_password(password),
                title="Участник",
                background="#DBDBDB",
                min_points=0
            )
            conn.add(user)
            conn.commit()
    conn = Session(init.engine)
    stmt = select(init.User).where(init.User.username == login)
    id = conn.execute(stmt).fetchall()[0][0].id
    conn.commit()
    conn.close()
    redirect = RedirectResponse(url="/", status_code=303)
    # Устанавливаем куки
    redirect.set_cookie(key="id", value=str(id))
    redirect.set_cookie(key="name", value=function.encrypt(name))
    redirect.set_cookie(key="username", value=function.encrypt(login))
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
    auth: str = Form(...),
    password: str = Form(...)
):
    error = True
    with Session(init.engine) as conn:
        stmt = select(init.User).where(init.User.username == auth)
        data = conn.execute(stmt).fetchall()
        if data and data[0][0].password == function.hash_password(password):
            # Создаем редирект-ответ
            redirect = RedirectResponse(url="/", status_code=303)
            # Устанавливаем куки
            redirect.set_cookie(key="id", value=str(data[0][0].id))
            redirect.set_cookie(key="name", value=function.encrypt(data[0][0].name))
            redirect.set_cookie(key="username", value=function.encrypt(data[0][0].username))
            return redirect
        else:
            return JSONResponse({"error": "Неверный логин или пароль"}, status_code=400)

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
            # Проверка существующего вопроса
            stmt = select(init.Question).where(
                init.Question.description == description
            )
            data = conn.execute(stmt).first()
            
            if data:
                print("Такой вопрос уже есть!")
                # Возможно, стоит вернуть сообщение об ошибке вместо редиректа
                return RedirectResponse(url="/?error=question_exists", status_code=303)
            else:
                # Добавление нового вопроса
                question = init.Question(
                    owner=function.decrypt(request.cookies.get("username")),
                    owner_name=function.decrypt(request.cookies.get("name")),
                    subject=subject,
                    grade=grade,
                    description=description,
                )
                conn.add(question)
                conn.commit()  # Важно: commit после добавления
            
            # # Обновление баллов пользователя
            # user_id = request.cookies.get("id")
            # if not user_id:
            #     return RedirectResponse(url="/login", status_code=303)
                
            # select_stmt = select(init.User).where(init.User.id == user_id)
            # user_data = conn.execute(select_stmt).first()
            
            # if not user_data:
            #     return RedirectResponse(url="/login", status_code=303)
                
            # user = user_data[0] if isinstance(user_data, tuple) else user_data
            # min_points = int(user.min_points) + 1
            
            # # Обновление уровня пользователя
            # # Предполагается, что levels - это список словарей с ключами 'title', 'min_points', 'background'
            # for level in levels:
            #     if (level.get('title') != user.title and 
            #         level.get('min_points') <= min_points):
                    
            #         update_stmt = (
            #             update(init.User)
            #             .where(init.User.id == user_id)
            #             .values(
            #                 title=level.get('title'),
            #                 background=level.get('background'),
            #                 min_points=min_points
            #             )
            #         )
            #         conn.execute(update_stmt)
            #         conn.commit()
            #         break  # Прерываем цикл после первого подходящего уровня
            
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        print(f"Ошибка при добавлении вопроса: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)

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
 
@app.get("/question/{note_id}", tags="Страница вопроса")
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
            ).where(init.Question.id == note_id)
            data = conn.execute(stmt).fetchall()
            
            if not data:
                return RedirectResponse(url="/", status_code=303)
                
            result = [data[0].owner, data[0].owner_name, data[0].subject, data[0].grade, data[0].description, data[0].id]
            
        with Session(init.engine) as conn:
            # Получаем комментарии - исправленный запрос
            stmt = select(
                init.Comment.owner,
                init.Comment.description
            ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
            data = conn.execute(stmt).fetchall()
            
            comments = []
            for row in data:
                comments.append({
                    "owner": row.owner,  # Теперь row имеет атрибуты owner и description
                    "description": row.description
                })
            
        return templates.TemplateResponse("answer.html", {
            "request": request,
            "result": result,
            "comments": comments,
        })
    else:
        return RedirectResponse(url="/login", status_code=303)
    
@app.post("/addcomment", tags="Добавить комментарий")
async def addcomment(
    request: Request,
    comment: str = Form(...),
    id: int = Form(...),
):
    with Session(init.engine) as conn:
        comments = init.Comment(
            question_id=id,
            owner=function.decrypt(request.cookies.get("username")),
            description=comment,
        )
        conn.add(comments)
        conn.commit()
        return RedirectResponse(url=f'/question/{id}', status_code=303)
    
@app.get("/profile/{username}", tags=["Профиль"])
async def profile(request: Request, username: str):
    with Session(init.engine) as conn:
            stmt = select(
                init.User.id,
                init.User.name,
            ).where(init.User.username == username)
            data = conn.execute(stmt).fetchall()
            account = [data[0].id, data[0].name, username]
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "account": account}
    )

if __name__ == "__main__":
    init.Base.metadata.create_all(init.engine)
    uvicorn.run("main:app", reload=True)