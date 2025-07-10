
from backend.database import db
from backend.models import Food, Order, OrderItem, User

def get_menu():
    return Food.query.all()

def create_order(user_id, address, customer_name, description, items, total):
    order = Order(user_id=user_id, address=address, customer_name=customer_name, description=description, total=total)
    db.session.add(order)
    db.session.commit()
    for item in items:
        db.session.add(OrderItem(order_id=order.id, food_id=item['food_id'], quantity=item['quantity']))
    db.session.commit()

def get_orders():
    return Order.query.all()

def mark_order_completed(order_id):
    order = Order.query.get(order_id)
    order.status = "completado"
    db.session.commit()
