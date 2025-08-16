from flask import Flask, send_from_directory
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
    
    # Serve static files from data directory
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    
    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(data_dir, filename, conditional=True)
    
    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)
    
    return app 