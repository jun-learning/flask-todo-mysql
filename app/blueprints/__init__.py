'''
Blueprints Package
'''
from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp

__all__ = ['main_bp', 'auth_bp']