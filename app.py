import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User
from datetime import datetime
from controllers.init import register_blueprints

def create_app():
    app = Flask(__name__, template_folder="templates")
    
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently, no production config is set up")
    else:
        print("Starting local development")
        app.config.from_object(LocalDevelopmentConfig())

    db.init_app(app)
    app.app_context().push()
    register_blueprints(app)
    return app

app = create_app()

with app.app_context():
    db.create_all() 
    
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", password="admin123", fullname="Administrator", qualification="N/A", dateofbirth=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), is_admin=True)
        db.session.add(admin)
        db.session.commit()




from controllers.auth import *
app.secret_key = '123'
@app.route("/")
def homepage():
    return render_template("homepage.html")

if __name__ == "__main__":
    app.run()

