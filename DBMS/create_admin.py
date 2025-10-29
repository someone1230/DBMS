from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    if User.query.filter_by(username='admin').first():
        print("Admin user already exists.")
    else:
        admin = User(username='admin', role='admin')
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        print("Admin user 'admin' created with password 'password'.")
