from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

  

class Employee(db.Model):
    """ Class for the Users of MyCerts"""
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(25), nullable = False)
    password = db.Column(db.Text)
    email = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.String(25), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    hire_date = db.Column(db.Date, nullable = False)
    is_admin = db.Column(db.Boolean, nullable = False)
    completed = db.Column(db.Integer)
    required = db.Column(db.Integer)
    location = db.Column(db.Integer, db.ForeignKey("locations.id", ondelete='CASCADE'))
    certs = db.Column(db.Integer, db.ForeignKey("certs.id", ondelete='CASCADE'))

    
    #locations = db.relationship("Location", secondary = employee_location, backref = db.backref("locals", lazy = "dynamic"), cascade = "all, delete")
    #certs = db.relationship("Certs", secondary = employee_cert, backref = db.backref("certifications", lazy = "dynamic"), cascade = "all, delete")
    #location = db.relationship("Location", backref = "user", cascade = "all, delete", lazy = True)
    #certs = db.relationship("Certs", backref = "certification", cascade = "all, delete", lazy = True)
    

    @classmethod
    def register(cls, username, password, email, first_name, last_name, hire_date, is_admin): ## do i need to add location and permissions?
        """Register user with hashed password and return user"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        employee = Employee(
            username=username, 
            password = hashed_pwd, 
            email = email, 
            first_name = first_name, 
            last_name = last_name, 
            hire_date = hire_date,
            is_admin = is_admin )
            
        db.session.add(employee)

        return employee

    
    def password_reset(username, password):
        """Password RESET"""
        
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        employee = Employee(
            username = username,
            password = hashed_pwd,
        )

        return employee

    
    def authenticate(username, password):
        """Validate that user and password are correct"""
        employee = Employee.query.filter_by(username=username).first()

        if employee:
            is_auth = bcrypt.check_password_hash(employee.password, password)
            if is_auth:
                return employee
        
        return False 
        

class Location(db.Model):

    __tablename__ = "locations"
    
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    site_name = db.Column(db.String(30), nullable = False, unique = True)
    city = db.Column(db.String(25))
    state = db.Column(db.String(2), nullable = False) 
    
    emp_loc = db.relationship("Employee", backref = "locations", cascade = "all, delete", lazy = "dynamic")
    
    
    #users = db.relationship("User", cascade = "all, delete") ##not sure about this relationship
    #users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    def __repr__(self):
        """Representation"""
        return (self.site_name)

    
        

class Certs(db.Model):
    __tablename__ = "certs"
    
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    cert_name = db.Column(db.Text, nullable = False, unique = 1)
    hours = db.Column(db.Integer, nullable = False)
    required = db.Column(db.Boolean, nullable = False)
    expire = db.Column(db.Boolean, nullable = False)
    good_for_time = db.Column(db.Integer) ## how long is good for - calculation needed
    good_for_unit = db.Column(db.String (10))
    
    
    emp_cert = db.relationship("Employee", backref = "cert", cascade = "all, delete", lazy = True)
    
    
    #user = db.relationship("User", cascade = "all, delete")
    #certification_id = db.Column(db.Integer, db.ForeignKey("users.id"))
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
    hours = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        """Representation"""
        return (self.name)



def connect_db(app):
    """Connect to the database"""
    db.app = app
    db.init_app(app) 



