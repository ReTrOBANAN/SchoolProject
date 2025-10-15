from fastapi import FastAPI, Request, Form, Response, requests
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime
from sqlalchemy import delete as sql_delete, and_
from sqlalchemy.orm import Session

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
        )
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
            stmt = select(
                init.Question.id,
                init.Question.owner,
                init.Question.owner_name,
                init.Question.subject,
                init.Question.grade,
                init.Question.description,
                init.Question.created_at,
            ).where(init.Question.owner == username).order_by(init.Question.id.desc())
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
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "account": account, "questions": questions}
    )

@app.post("/delete", tags=["Удаление вопроса"])
async def delete_question(
    request: Request,
    owner: str = Form(...),
    question_id: str = Form(...),
):
    print(question_id)
    current_user = function.decrypt(request.cookies.get("username"))
    if current_user == owner:
        with Session(init.engine) as session:
            # Правильное использование delete
            stmt = sql_delete(init.Question).where(
                and_(
                    init.Question.owner == current_user,
                    init.Question.id == question_id, 
                )
            )
            session.execute(stmt)
            stmt = sql_delete(init.Comment).where(
                and_(
                    init.Comment.question_id == question_id,
                )
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
    subject: str = Form(...),
    grade: str = Form(...),
    id: int = Form(...),
):
    current_user = function.decrypt(request.cookies.get("username"))
    if current_user == owner:
        print(description)
        with Session(init.engine) as session:
            if new_description:
                # Обновление вопроса
                stmt = update(init.Question).where(
                    and_(
                        init.Question.description == description,
                        init.Question.owner == current_user,
                        init.Question.id == id,
                    )
                ).values(description=new_description, grade=grade, subject=subject)
            else:
                stmt = update(init.Question).where(
                    and_(
                        init.Question.description == description,
                        init.Question.owner == current_user,
                        init.Question.id == id,
                    )
                ).values(grade=grade, subject=subject)
            session.execute(stmt)
            session.commit()
        
        return RedirectResponse("/", status_code=303)    
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/delete_answer", tags=["Удаление вопроса"])
async def delete_answer(
    request: Request,
    owner: str = Form(None),
    id: str = Form(None),
    questionId: str = Form(None),
):
    current_user = function.decrypt(request.cookies.get("username"))
    if current_user == owner:
        with Session(init.engine) as session:
            # Правильное использование delete
            stmt = sql_delete(init.Comment).where(
                and_(
                    init.Comment.owner == current_user,
                    init.Comment.id == id, 
                )
            )
            session.execute(stmt)
            session.commit()  # Не забывайте скобки!
        
        return RedirectResponse(f"/question/{questionId}", status_code=303)    
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/change_answer", tags=["Изменение вопроса"])
async def change_answer(
    request: Request,
    new_description: str = Form(...),
    owner: str = Form(...),
    id: int = Form(...),
):
    print(new_description, owner, id)
    current_user = function.decrypt(request.cookies.get("username"))
    if current_user == owner:
        if new_description:
            with Session(init.engine) as session:
                stmt = update(init.Comment).where(
                        and_(
                            init.Comment.owner == current_user,
                            init.Comment.id == id,
                        )
                    ).values(description=new_description)
            session.execute(stmt)
            session.commit()
            
            return RedirectResponse("/", status_code=303) 
        else:
            return RedirectResponse("/", status_code=303)
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/report_question", tags=["репорты"])
async def report_question(
    request: Request,
    questionId: str = Form(None),
    reson: str = Form(None),
):
    print(questionId, reson)
    with Session(init.engine) as conn:
            reporq = init.Reportq(
                question_id = questionId,
                reson = reson,
            )
            conn.add(reporq)
            conn.commit()  # Важно: commit после добавления
    return RedirectResponse(f"/question/{questionId}", status_code=303)

@app.post("/report_answer", tags=["репорты"])
async def report_answer(
    request: Request,
    answerId: str = Form(None),
    questionId: str = Form(None),
    complaint_type: str = Form(None),
):
    print(answerId, questionId, complaint_type)
    with Session(init.engine) as conn:
            repora = init.Reporta(
                answer_id = answerId,
                reson = complaint_type,
            )
            conn.add(repora)
            conn.commit()  # Важно: commit после добавления
    return RedirectResponse(f"/question/{questionId}", status_code=303)
        


if __name__ == "__main__":
    init.Base.metadata.create_all(init.engine)
    uvicorn.run("main:app", reload=True)