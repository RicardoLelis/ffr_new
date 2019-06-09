from project import db
from sqlalchemy.ext.hybrid import hybrid_method


class Recipe(db.Model):

    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    recipe_title = db.Column(db.String, nullable=False)
    recipe_description = db.Column(db.String, nullable=False)

    def __init__(self, title, description):
        self.recipe_title = title
        self.recipe_description = description
    
    def __repr__(self):
        return '<title {}'.format(self.name)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_plaintext = db.Column(db.String, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, email, password_plaintext):
        self.email = email
        self.password_plaintext = password_plaintext
        self.authenticated = False
    
    @hybrid_method
    def  is_correct_password(self, password_plaintext):
        return self.password_plaintext == password_plaintext
    
    @property
    def  is_authenticated(self):
        """Return True if the user is authenticated"""
        return self.authenticated
    
    @property
    def is_active(self):
        """Always True, as all users are active"""
        return True
    
    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported"""
        return False
    
    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirementes."""
        """Requires use of Python3"""
        return str(self.id)
    

    def __repr__(self):
        return '<User {0}>'.format(self.name)
