from flask_vercel import make_handler
from backend.app import app

handler = make_handler(app)
