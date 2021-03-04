import os

from flask import Flask, render_template, redirect, request, session, g, flash, json
from models import connect_db, db, Cert, Training, Employee, Location, employee_certification
from forms import Login_Form, User_Form, Cert_Form, Training_Form, Location_Form, SignUp_Form, Edit_User_Form, Reset_Pwd_Form, Add_Cert_Form, Email_Form, Edit_Hours_Form, Add_Loc_Form
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, date
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
import smtplib
from email.message import EmailMessage

bcrypt = Bcrypt()

CURR_USER_KEY = "curr_user"
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
    

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (os.environ.get("DATABASE_URL", "postgres:///mycerts"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "You can do this")

connect_db(app)
#db.drop_all()
#db.create_all()

toolbar = DebugToolbarExtension(app)  


@app.route("/")
def display():
    """Show Homepage, sign up and login buttons"""

    #still needs some cleanup on imagry and what the site is about. 

    return render_template("index.html")   

##################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = Employee.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def login(employee):
    """Login user."""

    session[CURR_USER_KEY] = employee.id

def logout():
    """ Logout user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        
@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Login form to login"""

    form = Login_Form()

    if form.validate_on_submit():
        employee = Employee.authenticate(
            username = form.username.data, 
            password = form.password.data)

        if employee:
            login(employee)
            flash(f"Hello {employee.first_name}!", "success")
            return redirect(f"/mycerts/{employee.id}")

        flash("Invalid Username or Password", "danger")

    return render_template("login.html", form = form)

@app.route("/sign-up", methods = ["GET", "POST"])
def sign_up():
    """Handle the signup of a new user, create a new user, add to DB, Redirect to mycerts page
    If the form is not valid, show form. If there is a user with the same email
    flash message and re present the form"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = SignUp_Form()

    if form.validate_on_submit():
        try:
            employee = Employee.register(
                username = form.username.data,
                password = form.password.data, 
                email = form.email.data, 
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                hire_date = form.hire_date.data,
                is_admin = form.is_admin.data
                )
            
            db.session.commit()

        except IntegrityError:
            flash("Email already in use", "danger")
            return render_template("sign-up.html", form = form)
        login(employee)
        msg = EmailMessage()
        msg['Subject'] = "BLAH"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = f"{employee.email}"
        msg.set_content('This is the plain text for the email')
        msg.add_alternative("""\
            <h1> Welcome to My Certs!</h1>
                """, subtype = "html")

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return redirect (f"/mycerts/{employee.id}")

    else:   

        return render_template("sign-up.html", form = form)

@app.route("/logout")
def logout_user():
    """Logout user"""

    logout()
    flash("You have successfully logged out.", "success")

    return redirect("/login")

@app.route("/password", methods = ["GET", "POST"])
def email_search():
    """ Reset users password"""
    
    form = Email_Form()

    if form.validate_on_submit():
        email = form.email.data
        employee = Employee.query.filter_by(email=email).first()
        flash("Now, reset your password", "success")
        return redirect(f"/password_reset/{employee.id}")

    else:
        return render_template("password.html", form=form)

@app.route("/password_reset/<int:employee_id>", methods = ["GET", "POST"])
def reset_password(employee_id):
    """ Reset users password"""

    employee = Employee.query.get(employee_id)

    form = Reset_Pwd_Form(obj = employee)


    if form.validate_on_submit():
        employee.username = form.username.data
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode("UTF-8")
        employee.password = hashed_pwd

        db.session.commit()

        
        
        flash("Your password has been reset", "success")
        
        msg = EmailMessage()
        msg['Subject'] = "BLAH"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = f'{employee.email}'
        msg.set_content('This is the plain text for the email')
        msg.add_alternative("""\
            <h1>Your Password has been reset! </h1>
            """, subtype = "html")

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return redirect("/login")
    else:
        return render_template("password.html", form=form)

#######################################################################
# user routes

@app.route("/mycerts/<int:employee_id>")
def display_certs(employee_id):
    """Display certs for user logged in"""

    if not g.user:
        flash("Please Login to continue.", "danger")
        return redirect("/")

    employee = Employee.query.get_or_404(employee_id)
   
    certs = employee_certification.query.filter_by(employee_id = employee_id).all()
    
    return render_template("users/display_cert.html", employee = employee, certs = certs)

@app.route("/hours/<int:employee_id>")
def display_hours(employee_id):
    """Display training hours with graph for user logged in"""

    if not g.user:
        flash("Please Login to continue.", "danger")
        return redirect("/")
    
    employee = Employee.query.get_or_404(employee_id)

    labels = json.dumps( ["Completed", "Required"])
    data = json.dumps([employee.completed, employee.required])
 
    return render_template("users/display_hours.html", employee = employee, labels = labels, data = data)

@app.route("/training")
def display_training():
    """Display training classes coming up"""

    if not g.user:
        flash("Please Login to continue.", "danger")
        return redirect("/")

    trainings = Training.query.all()

    return render_template("users/show_training.html", trainings = trainings)

##########################################################################
#admin dashboard routes

@app.route("/administrator")
def show_all_information():
    """Display Admin options along with list of Users"""
    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    ## What should go on this page.... Directions? Graph? Summary?

    
    return render_template("admin.html")

@app.route("/employees")
def show_all_employees():
    """Display Admin options along with list of Users"""
    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    employees = Employee.query.all()
      
    ## right now this is ALL users... 
    
    return render_template("employee_display.html", employees = employees)

@app.route("/locations")
def show_all_locations():
    """Display Admin options along with list of Users"""
    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    locations = Location.query.all()
      
      ## this is ALL locations
    
    return render_template("locations_display.html", locations = locations)

@app.route("/certifications")
def show_all_certifications():
    """Display Admin options along with list of Users"""
    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    
    certs = Cert.query.all()
    ## all possible certs...
    
    return render_template("certs_display.html", certs = certs)

@app.route("/trainings")
def show_all_training():
    """Display Admin options along with list of Users"""
    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    
    training = Training.query.all()

    
    return render_template("training_display.html", training = training)



#####################################################################################################
#add and edit routes

@app.route("/ad/add-user", methods = ["GET", "POST"])
def add_employee():
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    form = SignUp_Form()
    

    if form.validate_on_submit():
        try: 
            employee = Employee.register(
                username = form.username.data,
                password = form.password.data, 
                email = form.email.data, 
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                hire_date = form.hire_date.data, 
                is_admin = form.is_admin.data,
            )

            db.session.add(employee)

            db.session.commit()
        except IntegrityError:
            flash("Email already in use", "danger")
            return render_template("/admin/add_user.html", form = form)

        flash("Employee Added!", "success")
        return redirect("/administrator")
    else:

        return render_template("/admin/add_user.html", form = form)

@app.route("/ad/add-cert", methods = ["GET", "POST"])
def add_cert():
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    form = Cert_Form()

    if form.validate_on_submit():
        cert = Cert(
            cert_name = form.cert_name.data,
            hours = form.hours.data,
            required = form.required.data,
            expire = form.expire.data,
            good_for_time = form.good_for_time.data,
            good_for_unit = form.good_for_unit.data,
            
        )
        db.session.add(cert)
        db.session.commit()

        flash("Certification Added!", "success")
        return redirect("/administrator")

    else: 

        return render_template("/admin/add_cert.html", form = form)

@app.route("/ad/add-location", methods = ["GET", "POST"])
def add_location():
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")
    
    form = Location_Form()

    if form.validate_on_submit():
        try:
            location = Location(
                site_name = form.site_name.data,
                city = form.city.data,
                state = form.state.data
            )
            db.session.add(location)
            db.session.commit()
        except IntegrityError:
            flash("This location already exists", "danger")
            return render_template("/admin/add_location.html", form = form)
    
        flash("Location Added!", "success")
        return redirect("/administrator")
    else:
        return render_template("/admin/add_location.html", form = form)

@app.route("/ad/add-training", methods = ["GET", "POST"])
def add_training():
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    form = Training_Form()

    if form.validate_on_submit():
        training = Training(
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            room = form.room.data,
            hours = form.hours.data,
            date = form.date.data,
            time = form.time.data
        )
        db.session.add(training)
        db.session.commit()
        
        flash("Training Added!", "success")
        return redirect("/administrator")

    else: 

        return render_template("/admin/add_training.html", form = form)

@app.route("/ad/edit-user/<int:employee_id>", methods = ["GET", "POST"])
def edit_employee(employee_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    employee = Employee.query.get_or_404(employee_id)
    form = Edit_User_Form(obj = employee)
    
    #form.location.choices = db.session.query(Location.id, Location.site_name).all()
    
    #form.certs.choices = db.session.query(Certs.id , Certs.cert_name).all()

    if form.validate_on_submit():
        
        employee.email = form.email.data, 
        employee.first_name = form.first_name.data,
        employee.last_name = form.last_name.data,
        employee.hire_date = form.hire_date.data, 
        employee.is_admin = form.is_admin.data

        
        db.session.commit()
    
        flash(f"{employee.first_name} {employee.last_name} has been saved", "success")
        return redirect("/administrator")
    else:

        return render_template("/admin/edit_user.html", employee = employee, form = form)

@app.route("/ad/employee-certificaton/<int:employee_id>", methods = ["GET", "POST"])
def edit_employee_certifications(employee_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    employee = Employee.query.get_or_404(employee_id)
    
    form = Add_Cert_Form(obj = employee)
    
    form.cert.choices = db.session.query(Cert.id , Cert.cert_name).all()
   
    
    if form.validate_on_submit():
        
        cert = Cert.query.get(form.cert.data) 
        #data = form.received.data
        #received=employee_certification(received = data)
        
        #employee.certs.append(received)
        employee.certs.append(cert)
        #db.session.add(employee)
        
        #db.session.commit()

        if cert.expire:
            received = form.received.data
            year = received.year
            month = received.month
            day = received.day

            start_date = datetime(year = year, month = month, day = day)
            change_unit = cert.good_for_unit
            change_time = cert.good_for_time
            
            if change_unit == "days": 
                delta = timedelta(days = change_time)
            elif change_unit == "weeks":
                delta = timedelta(days = change_time * 7)
            elif change_unit == "months":
                delta = timedelta(days = change_time * 30)
            else:
                delta = timedelta(days = change_time * 365)

            due_date = start_date + delta
            dates = employee_certification(received = received, due_date = due_date)
        employee.certs.append(dates)
        
        db.session.add(employee)
        db.session.commit()
    
        flash(f"{employee.first_name} {employee.last_name} has been saved", "success")
        return redirect("/administrator")
    else:

        return render_template("/admin/employee_cert.html", employee = employee, form = form)

@app.route("/ad/employee-location/<int:employee_id>", methods = ["GET", "POST"])
def edit_employee_locations(employee_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    employee = Employee.query.get_or_404(employee_id)
    
    form = Add_Loc_Form(obj = employee)
    
    form.location.choices = db.session.query(Location.id, Location.site_name).all()
    
    
    if form.validate_on_submit():
        
        location = Location.query.get(form.location.data) 
        employee.locations.append(location)
        db.session.add(employee)
        
        db.session.commit()

        

        flash(f"{employee.first_name} {employee.last_name} has been saved", "success")
        return redirect("/administrator")
    else:
        
        return render_template("/admin/employee_cert.html", employee = employee, form = form)

@app.route("/ad/edit-hours/<int:employee_id>", methods = ["GET", "POST"])
def edit_employee_hours(employee_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    employee = Employee.query.get_or_404(employee_id)
    form = Edit_Hours_Form(obj = employee)

    if form.validate_on_submit():
        
        employee.completed = form.completed.data, 
        employee.required = form.required.data,
                
        db.session.commit()
    
        flash(f"{employee.first_name} {employee.last_name} has been saved", "success")
        return redirect("/administrator")
    else:

        return render_template("/admin/edit_hours.html", employee = employee, form = form)

@app.route("/ad/edit-cert/<int:cert_id>")
def edit_cert(cert_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    cert = Certs.query.get_or_404(cert_id)
    form = Cert_Form(obj=cert)

    if form.validate_on_submit():
        cert.cert_name = form.cert_name.data
        cert.hours = form.hours.data
        cert.required = form.required.data
        cert.expire = form.expire.data
        cert.good_for_time = form.good_for_time.data
        cert.good_for_unit = form.good_for_unit.data
        

        db.session.commit()
        flash(f"{cert.cert_name} has been updated")
        return redirect("/administrator")

    return render_template("/admin/edit_cert.html", form=form, cert = cert)

@app.route("/ad/edit-location/<int:location_id>")
def edit_locations(location_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    location = Location.query.get_or_404(location_id)
    form = Location_Form(obj = location)

    if form.validate_on_submit():
        location.site_name = form.site_name.data,
        location.city = form.city.data,
        location.state = form.state.data
        
        db.session.commit()
        flash(f"Location {site_name} has been updated")
        return redirect("/administrator")
    else:
        return render_template("/admin/edit_location.html", form = form, location = location)

@app.route("/ad/edit-training/<int:training_id>")
def edit_training(training_id):
    """Setup a user for certs"""

    if not g.user:
        flash("Please login to access", "danger")
        return redirect("/")
    
    if g.user.is_admin == False:
        flash ("Unauthorized", "danger")
        return redirect("/login")

    training = Training.query.get_or_404(training_id)
    form = Training_Form(obj = training)

    if form.validate_on_submit():
        training.name = form.name.data,
        training.city = form.city.data,
        training.state = form.state.data,
        training.room = form.room.data,
        training.hours = form.hours.data

        db.session.commit()
        flash(f"{training.name} has been updated")
        return redirect("/administrator")

    else:
        return render_template("/admin/edit_training.html", form = form, training = training)


#@app.teardown_request
#def teardown_request(exception):
#    if exception:
#        db.session.rollback()
#    db.session.remove()

@app.errorhandler(404)
def not_found(error):
  return render_template("/404.html")