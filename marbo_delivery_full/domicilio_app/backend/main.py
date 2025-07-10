from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
import os
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="backend/templates")

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# ================== VISTAS DEL CLIENTE ==================

@app.get("/menu", response_class=HTMLResponse)
def client_menu(request: Request):
    with engine.connect() as conn:
        foods = conn.execute(text("SELECT * FROM food")).fetchall()
    return templates.TemplateResponse("client_menu.html", {"request": request, "foods": foods})

@app.get("/mis_pedidos", response_class=HTMLResponse)
def mis_pedidos(request: Request):
    with engine.connect() as conn:
        pedidos = []  # Adaptar a tu modelo real
    return templates.TemplateResponse("mis_pedidos.html", {"request": request, "pedidos": pedidos})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
def register(request: Request, username: str = Form(...), password: str = Form(...)):
    with engine.connect() as conn:
        existing = conn.execute(text("SELECT * FROM user WHERE username=:u"), {"u": username}).fetchone()
        if existing:
            return templates.TemplateResponse("register.html", {"request": request, "error": "El usuario ya existe."})
        conn.execute(text("INSERT INTO user (username, password, role) VALUES (:u, :p, 'client')"), {"u": username, "p": password})
    return RedirectResponse(url="/menu", status_code=303)

# ================== VISTAS DEL DUEÑO ==================

@app.get("/owner", response_class=HTMLResponse)
def owner_dashboard(request: Request):
    with engine.connect() as conn:
        orders = conn.execute(text("SELECT * FROM order WHERE status != 'completado'")).fetchall()
        foods = conn.execute(text("SELECT * FROM food")).fetchall()
        daily_total = conn.execute(text("SELECT SUM(total) FROM order WHERE status = 'completado'")).scalar() or 0
        history = conn.execute(text("SELECT date, amount FROM daily_earnings ORDER BY id DESC")).fetchall()
    history_dict = {row.date: row.amount for row in history}
    return templates.TemplateResponse("owner_dashboard.html", {
        "request": request,
        "orders": orders,
        "foods": foods,
        "daily_total": daily_total,
        "history": history_dict
    })

@app.get("/owner/menu", response_class=HTMLResponse)
def owner_menu(request: Request):
    with engine.connect() as conn:
        foods = conn.execute(text("SELECT * FROM food")).fetchall()
    return templates.TemplateResponse("owner_menu.html", {"request": request, "foods": foods})

@app.post("/owner/add_food")
def add_food(request: Request, name: str = Form(...), price: float = Form(...)):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO food (name, price) VALUES (:name, :price)"), {"name": name, "price": price})
    return RedirectResponse(url="/owner", status_code=303)

@app.post("/owner/delete_food/{food_id}")
def delete_food(food_id: int):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM food WHERE id=:id"), {"id": food_id})
    return RedirectResponse(url="/owner/menu", status_code=303)

@app.get("/owner/edit_food/{food_id}", response_class=HTMLResponse)
def edit_food_form(request: Request, food_id: int):
    with engine.connect() as conn:
        food = conn.execute(text("SELECT * FROM food WHERE id=:id"), {"id": food_id}).fetchone()
    return templates.TemplateResponse("edit_food.html", {"request": request, "food": food})

@app.post("/owner/edit_food/{food_id}")
def edit_food(food_id: int, name: str = Form(...), price: float = Form(...)):
    with engine.connect() as conn:
        conn.execute(text("UPDATE food SET name=:name, price=:price WHERE id=:id"),
                     {"name": name, "price": price, "id": food_id})
    return RedirectResponse(url="/owner/menu", status_code=303)

@app.post("/owner/complete_order/{order_id}")
def complete_order(order_id: int):
    with engine.connect() as conn:
        conn.execute(text("UPDATE order SET status='completado' WHERE id=:id"), {"id": order_id})
    return RedirectResponse(url="/owner", status_code=303)

@app.post("/owner/reset_day")
def reset_day():
    with engine.connect() as conn:
        total = conn.execute(text("SELECT SUM(total) FROM order WHERE status = 'completado'")).scalar() or 0
        today = datetime.now().strftime('%Y-%m-%d')
        if total > 0:
            existing = conn.execute(text("SELECT * FROM daily_earnings WHERE date=:today"), {"today": today}).fetchone()
            if existing:
                conn.execute(text("UPDATE daily_earnings SET amount=:total WHERE date=:today"),
                             {"total": total, "today": today})
            else:
                conn.execute(text("INSERT INTO daily_earnings (date, amount) VALUES (:today, :total)"),
                             {"today": today, "total": total})
        conn.execute(text("DELETE FROM orderitem"))
        conn.execute(text("DELETE FROM order"))
    return RedirectResponse(url="/owner", status_code=303)

@app.post("/owner/reset_year")
def reset_year():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM daily_earnings"))
    return RedirectResponse(url="/owner", status_code=303)

