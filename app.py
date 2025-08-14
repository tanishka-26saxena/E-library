from flask import Flask
from models import db
import secrets , os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///lms.db'
    app.secret_key = secrets.token_hex(16)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'covers')
    db.init_app(app)
    with app.app_context():

        db.create_all()
        
        import routes
        import app_data
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    