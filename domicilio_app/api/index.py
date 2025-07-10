from vercel_wsgi import handle
from backend.app import app

def handler(environ, start_response):
    return handle(app, environ, start_response)
