from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    
    # Ensure all data directories exist
    os.makedirs('data/brands', exist_ok=True)
    os.makedirs('data/assets', exist_ok=True)
    os.makedirs('data/drafts', exist_ok=True)
    os.makedirs('data/kits', exist_ok=True)
    
    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)
    
    return app 