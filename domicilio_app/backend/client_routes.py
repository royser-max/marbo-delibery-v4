from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Food, Order, OrderItem
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

client_bp = Blueprint('client', __name__)

@client_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        # Todos los registros serán clientes
        role = 'client'
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('El usuario ya existe.')
            return render_template('register.html')
        login_user(user)
        return redirect('/menu')
    return render_template('register.html')

@client_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            # Solo dos usuarios pueden ser dueños
            owner_users = ['dueno1', 'dueno2']
            login_user(user)
            if user.role == 'client':
                return redirect('/menu')
            elif user.role == 'owner' and user.username in owner_users:
                # Siempre redirigir con GET
                return redirect(url_for('owner.owner_dashboard'))
            elif user.role == 'admin':
                return redirect('/admin')
            else:
                flash('Acceso no autorizado para este usuario.')
                return redirect('/login')
        flash('Usuario o contraseña incorrectos.')
    return render_template('login.html')

@client_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@client_bp.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    if current_user.role != 'client':
        return redirect('/login')
    foods = Food.query.all()
    total = None
    if request.method == 'POST':
        address = request.form['address']
        description = request.form.get('description', '')
        customer_name = request.form['customer_name']
        items = []
        total = 0
        for food in foods:
            qty = int(request.form.get(f'quantity_{food.id}', 0))
            if qty > 0:
                items.append({'food': food, 'quantity': qty})
                total += food.price * qty
        if not items:
            flash('Debes seleccionar al menos un alimento.')
            return render_template('client_menu.html', foods=foods, total=0)
        # Crear pedido
        order = Order(user_id=current_user.id, address=address, customer_name=customer_name, description=description, total=total, status='pendiente')
        db.session.add(order)
        db.session.commit()
        for item in items:
            order_item = OrderItem(order_id=order.id, food_id=item['food'].id, quantity=item['quantity'])
            db.session.add(order_item)
        db.session.commit()
        flash(f'Pedido realizado correctamente. Total a pagar: ${total}')
        # Emitir evento para actualizar pedidos en tiempo real
        # socketio.emit('update_pedidos')
        return redirect('/menu')
    return render_template('client_menu.html', foods=foods, total=total)

@client_bp.route('/mis_pedidos')
@login_required
def mis_pedidos():
    if current_user.role != 'client':
        return redirect('/login')
    from models import Order, OrderItem, Food
    # Mostrar solo pedidos pendientes del usuario
    pedidos = Order.query.filter_by(user_id=current_user.id).filter(Order.status != 'completado').all()
    pedidos_info = []
    for pedido in pedidos:
        items = OrderItem.query.filter_by(order_id=pedido.id).all()
        detalle = []
        for item in items:
            food = Food.query.get(item.food_id)
            detalle.append({'nombre': food.name, 'cantidad': item.quantity, 'precio': food.price})
        pedidos_info.append({'pedido': pedido, 'detalle': detalle})
    return render_template('mis_pedidos.html', pedidos=pedidos_info)
