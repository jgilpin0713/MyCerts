from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

class employee_certification(db.Model):
    ___tablename__ = "emp_cert", 

    id = db.Column(db.Integer, primary_key = True, autoincrement = True) 
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id", ondelete = "cascade")) 
    cert_id = db.Column(db.Integer, db.ForeignKey("certs.id", ondelete = "cascade"))
    received = db.Column(db.Date, nullable = False)
    due_date = db.Column(db.Date)

    def __init__(self, employee_id, cert_id, received, due_date):
        self.employee_id = employee_id
        self.cert_id = cert_id
        self.received = received
        self.due_date = due_date

employee_location = db.Table("emp_loc", 
db.Column("id", db.Integer, primary_key = True, autoincrement = True),
db.Column("employee_id", db.Integer, db.ForeignKey("employees.id", ondelete = "cascade")), 
db.Column("location_id", db.Integer, db.ForeignKey("locations.id", ondelete = "cascade")))


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
    
    
    locations = db.relationship("Location", secondary = employee_location, cascade = "all, delete")
    certs = db.relationship("Cert", secondary = "employee_certification",  cascade = "all, delete")

    

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
        
    def __init__(self, username, password, email, first_name, last_name, hire_date, is_admin):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.hire_date = hire_date
        self.is_admin = is_admin
        

class Location(db.Model):

    __tablename__ = "locations"
    
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    site_name = db.Column(db.String(30), nullable = False, unique = True)
    city = db.Column(db.String(25))
    state = db.Column(db.String(2), nullable = False) 
    
    employees = db.relationship("Employee", secondary = employee_location, cascade = "all, delete")
     
    def __init__(self, site_name, city, state):
        self.site_name = site_name
        self.city = city
        self.state = state

class Cert(db.Model):
    __tablename__ = "certs"
    
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    cert_name = db.Column(db.Text, nullable = False, unique = 1)
    hours = db.Column(db.Integer, nullable = False)
    is_required = db.Column(db.Boolean, nullable = False)
    expire = db.Column(db.Boolean, nullable = False)
    good_for_time = db.Column(db.Integer) ## how long is good for - calculation needed
    good_for_unit = db.Column(db.String (10))
    
    
    employees = db.relationship("Employee", secondary = "employee_certification", cascade = "all, delete")
    
    def __init__(self, cert_name, hours, is_required, expire, good_for_time, good_for_unit):
        self.cert_name = cert_name
        self.hours = hours
        self.is_required = is_required
        self.expire = expire
        self.good_for_time = good_for_time
        self.good_for_unit = good_for_unit

class Training(db.Model):
    __tablename__ = "trainings"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.Text, nullable = False)
    city = db.Column(db.String(30))
    state = db.Column(db.String(2), nullable = False)
    room = db.Column(db.String(30), nullable = False)
    hours = db.Column(db.Integer, nullable = False)
    date = db.Column(db.Date, nullable = False)
    time = db.Column(db.Time, nullable = False)

    def __init__(self, name, city, state, room, hours, date, time):
        self.name = name
        self.city = city
        self.state = state
        self.room = room
        self.hours = hours
        self.date = date
        self.time = time

def connect_db(app):
    """Connect to the database"""
    db.app = app
    db.init_app(app) 



