from app import create_app
from app.models import create_tables

app = create_app()
with app.app_context():
    create_tables()
application = create_app()
