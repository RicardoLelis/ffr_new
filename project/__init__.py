#################
#### imports ####
#################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_uploads import UploadSet, IMAGES, configure_uploads

################
#### config ####
################

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

# Configure  the image uploading via flask-Uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

from  project.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


####################
#### blueprints ####
####################

from project.users.views import users_blueprint
from project.recipes.views import recipes_blueprint

# Register the blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(recipes_blueprint)