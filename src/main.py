import os
import sys
# DON\"T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from src.models.user import db
from src.models.replay import Replay
from src.routes.user import user_bp
from src.routes.replay import replay_bp
from src.utils.circular_buffer import CircularVideoBuffer
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# habilita CORS para permitir requisições do frontend
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(replay_bp, url_prefix='/api/replay')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'db.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def serve_root():
    return render_template('index.html')

@app.route('/<path:path>')
def serve_path(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # usar render_template para servir o index.html da pasta templates
        return render_template('index.html')

@app.route('/style.css')
def serve_css():
    """serve CSS from templates folder"""
    return send_from_directory(app.template_folder, 'style.css', mimetype='text/css')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

