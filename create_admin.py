from app import create_app
from app.extensions import db
from app.models import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists.")
        else:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_confirmed=True  # Optional: skip email confirmation
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username and password: admin")

if __name__ == '__main__':
    create_admin_user() 