from database import db
from models import User
from werkzeug.security import generate_password_hash
from app import app

with app.app_context():
    for username in ["dueno1", "dueno2"]:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, password=generate_password_hash("1234"), role="owner")
            db.session.add(user)
    db.session.commit()
print("Usuarios dueños creados con contraseña: 1234")
