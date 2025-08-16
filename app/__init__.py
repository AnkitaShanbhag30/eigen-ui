from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Get the project root directory (parent of app directory)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    app = Flask(__name__, 
                static_folder=os.path.join(project_root, "static"), 
                template_folder=os.path.join(project_root, "templates"))
    
    # Enable CORS for the app
    CORS(app, resources={r"/*": {"origins": [
        "http://localhost:5174",
        "https://localhost:3000"
    ]}}, supports_credentials=False)
    
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