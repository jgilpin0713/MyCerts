from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()
   

class User(db.Model):
    """ Class for the Users of MyCerts"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(25), nullable = False)
    password = db.Column(db.Text)
    email = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.String(25), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    hire_date = db.Column(db.Date, nullable = False)
    admin = db.Column(db.Boolean, nullable = False)
    completed = db.Column(db.Integer)
    required = db.Column(db.Integer)

    location = db.relationship("Location", backref = "user", cascade = "all, delete", lazy = True)
    certs = db.relationship("Certs", backref = "user", cascade = "all, delete", lazy = True)
    
    
    def __repr__(self):
        """Representation"""
        return (self.first_name)


    @classmethod
    def register(cls, username, password, email, first_name, last_name, hire_date, admin): ## do i need to add location and permissions?
        """Register user with hashed password and return user"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username, 
            password = hashed_pwd, 
            email = email, 
            first_name = first_name, 
            last_name = last_name, 
            hire_date = hire_date,
            admin = admin )
            
        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user and password are correct"""
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False 
        

class Location(db.Model):

    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    site_name = db.Column(db.String(30), nullable = False, unique = True)
    city = db.Column(db.String(25))
    state = db.Column(db.String(2), nullable = False) 
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    #users = db.relationship("User", cascade = "all, delete") ##not sure about this relationship

    def __repr__(self):
        """Representation"""
        return (self.site_name)

    
        

class Certs(db.Model):
    __tablename__ = "certs"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    cert_name = db.Column(db.Text, nullable = False, unique = True)
    hours = db.Column(db.Integer, nullable = False)
    required = db.Column(db.Boolean, nullable = False)
    expire = db.Column(db.Boolean, nullable = False)
    good_for_time = db.Column(db.Integer) ## how long is good for - calculation needed
    good_for_unit = db.Column(db.String (10))
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    #user = db.relationship("User", cascade = "all, delete")

    def __repr__(self):
        """Representation"""
        return (self.cert_name)


class Training(db.Model):
    __tablename__ = "trainings"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.Text, nullable = False)
    city = db.Column(db.String(30))
    state = db.Column(db.String(2), nullable = False)
    room = db.Column(db.String(30), nullable = False)
    hour = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        """Representation"""
        return (self.name)


def connect_db(app):
    """Connect to the database"""
    db.app = app
    db.init_app(app) 



