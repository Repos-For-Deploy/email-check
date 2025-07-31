# run.py
from app import create_app
from app.models import create_tables
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    create_tables()
    
if __name__ == '__main__':
    app.run(debug=True)
