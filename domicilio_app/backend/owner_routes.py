from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Order, Food, OrderItem, DailyEarnings
from database import db
import os

owner_bp = Blueprint('owner', __name__)

OWNER_USERS = ['dueno1', 'dueno2']

@owner_bp.route('/owner', methods=['GET', 'POST'])
@login_required
def owner_dashboard():
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    orders = Order.query.filter(Order.status != 'completado').all()
    foods = Food.query.all()
    daily_total = sum([o.total for o in Order.query.filter_by(status='completado').all()])
    # Obtener historial de ganancias
    history = {e.date: e.amount for e in DailyEarnings.query.order_by(DailyEarnings.id.desc()).all()}
    return render_template('owner_dashboard.html', orders=orders, foods=foods, daily_total=daily_total, history=history)

@owner_bp.route('/owner/add_food', methods=['POST'])
@login_required
def add_food():
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    name = request.form['name']
    price = float(request.form['price'])
    image = request.files.get('image')
    image_path = None
    if image and image.filename:
        image_folder = os.path.join(os.path.dirname(__file__), 'static', 'images')
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join('static/images', image.filename)
        image.save(os.path.join(os.path.dirname(__file__), image_path))
    food = Food(name=name, price=price, image_path=image_path)
    db.session.add(food)
    db.session.commit()
    # socketio.emit('menu_updated')
    flash('Alimento agregado correctamente.')
    return redirect('/owner')

@owner_bp.route('/owner/complete_order/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    order = Order.query.get(order_id)
    if order and order.status != 'completado':
        order.status = 'completado'
        db.session.commit()
        # socketio.emit('order_completed')
        flash('Pedido completado.')
    return redirect('/owner')

@owner_bp.route('/owner/reset_day', methods=['POST'])
@login_required
def reset_day():
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    from datetime import datetime
    completed_orders = Order.query.filter_by(status='completado').all()
    total = sum([o.total for o in completed_orders])
    # Guardar el total en el historial de ganancias
    today = datetime.now().strftime('%Y-%m-%d')
    if total > 0:
        existing = DailyEarnings.query.filter_by(date=today).first()
        if existing:
            existing.amount = total
        else:
            earning = DailyEarnings(date=today, amount=total)
            db.session.add(earning)
        db.session.commit()
    # Eliminar pedidos y reiniciar
    OrderItem.query.delete()
    Order.query.delete()
    db.session.commit()
    # socketio.emit('orders_reset')
    flash(f'Día reiniciado. Ganancia guardada: ${total}')
    return redirect('/owner')

@owner_bp.route('/owner/reset_year', methods=['POST'])
@login_required
def reset_year():
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    from models import DailyEarnings
    DailyEarnings.query.delete()
    db.session.commit()
    # socketio.emit('yearly_reset')
    flash('Historial de ventas del año reiniciado.')
    return redirect('/owner')

@owner_bp.route('/owner/menu', methods=['GET'])
@login_required
def owner_menu():
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    foods = Food.query.all()
    return render_template('owner_menu.html', foods=foods)

@owner_bp.route('/owner/delete_food/<int:food_id>', methods=['POST'])
@login_required
def delete_food(food_id):
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    food = Food.query.get(food_id)
    if food:
        db.session.delete(food)
        db.session.commit()
        # socketio.emit('menu_updated')
        flash('Alimento eliminado.')
    return redirect('/owner/menu')

@owner_bp.route('/owner/edit_food/<int:food_id>', methods=['GET', 'POST'])
@login_required
def edit_food(food_id):
    if current_user.role != 'owner' or current_user.username not in OWNER_USERS:
        return "Acceso no autorizado"
    food = Food.query.get(food_id)
    if not food:
        flash('Alimento no encontrado.')
        return redirect('/owner/menu')
    if request.method == 'POST':
        food.name = request.form['name']
        food.price = float(request.form['price'])
        image = request.files.get('image')
        if image and image.filename:
            import os
            image_folder = os.path.join(os.path.dirname(__file__), 'static', 'images')
            os.makedirs(image_folder, exist_ok=True)
            image_path = os.path.join('static/images', image.filename)
            image.save(os.path.join(os.path.dirname(__file__), image_path))
            food.image_path = image_path
        db.session.commit()
        # socketio.emit('menu_updated')
        flash('Alimento actualizado.')
        return redirect('/owner/menu')
    return render_template('edit_food.html', food=food)
