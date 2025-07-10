from flask import Flask

from client_routes import client_bp
from owner_routes import owner_bp
from auth import login_manager
from database import db
from flask import render_template, redirect
from flask_login import login_required, current_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'client.login'
login_manager.login_message = 'Por favor, inicia sesión para continuar.'

# Página de inicio
@app.route('/')
def home():
    return render_template('login.html')

# Panel de admin
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Acceso no autorizado"
    return render_template('admin_dashboard.html')

app.register_blueprint(client_bp)
app.register_blueprint(owner_bp)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
