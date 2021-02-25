
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, DateField, RadioField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Optional, Length

class Login_Form(FlaskForm):
    """Form for logging in an exisiting user"""

    username = StringField("Username", validators= [InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class User_Form(FlaskForm):
    """Form for setting up a new user"""

    username = StringField("Username", validators= [InputRequired(), Length(max = 25)])
    password = PasswordField("Password", validators=[Length(min = 8, max = 80)])
    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid Email"), Length(max = 50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max = 25)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length (max = 30)])
    admin = BooleanField("Is this person an administrator?")
    hire_date = DateField("Date of Hire", validators=[InputRequired()])
    location = SelectField("Location", validators=[InputRequired()], coerce = int, choices = []) ## choices are the location already added 
    certs = SelectMultipleField("Certifications (Select all that Apply)", validators=[InputRequired()], coerce= int) ## choices are the certifications already added
    completed = IntegerField("Training Hours Completed", default = 0)
    required = IntegerField("Training Hours Required", validators=[InputRequired()])


class Cert_Form(FlaskForm):
    """Form for creating a new certification"""
    
    cert_name = StringField("Name of Certification", validators=[InputRequired()])
    hours = IntegerField("How many hours", validators = [InputRequired()])
    required = BooleanField("Is this Certification required?")
    expire = BooleanField("Does this certification expire?")
    good_for_time = IntegerField("How long is this certification good for?", validators=[Optional()])
    good_for_unit = RadioField("Select the appropriate length", validators = [Optional()], choices = ["days", "weeks", "months", "years"]) ## choices are days, months, years

class Training_Form(FlaskForm):
    """Form for creating a new upcoming training"""

    name = StringField("Name of the Training offered: ", validators=[InputRequired()])
    city = StringField("City: ", validators = [Optional(), Length(max = 30)])
    state = StringField("State: ", validators=[InputRequired(), Length (max =2)])
    room = StringField("Room: ", validators=[InputRequired(), Length(max=30)])
    hour = IntegerField("How many hours?", validators=[InputRequired()])


class Location_Form(FlaskForm):
    """Form for creating a new location"""

    site_name = StringField("Name of location", validators=[InputRequired(), Length(max = 30)])
    city = StringField("City", validators=[Optional(), Length(max = 25)])
    state = StringField("State", validators=[InputRequired(), Length(max = 2)])


class SignUp_Form(FlaskForm):
    """Sign up a new user"""

    username = StringField("Username", validators= [InputRequired(), Length(max = 25)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min = 8, max = 80)])
    email = StringField("Email", validators=[InputRequired(), Email(message = "Invalid Email"), Length(max = 50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max = 25)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length (max = 30)])
    hire_date = DateField("Date of Hire", validators=[InputRequired()])
    admin = BooleanField("Is this person an administrator?")


class Edit_User_Form(FlaskForm):
    """Form for setting up a new user"""

    #username = StringField("Username", validators= [InputRequired(), Length(max = 25)])
    #password = PasswordField("Password")
    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid Email"), Length(max = 50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max = 25)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length (max = 30)])
    admin = BooleanField("Is this person an administrator?")
    hire_date = DateField("Date of Hire", validators=[InputRequired()])
    location = SelectField("Location", validators=[InputRequired()], coerce = int, choices = []) ## choices are the location already added 
    certs = SelectMultipleField("Certifications (Select all that Apply)", validators=[InputRequired()], coerce= int) ## choices are the certifications already added
    completed = IntegerField("Training Hours Completed", default = 0)
    required = IntegerField("Training Hours Required", validators=[InputRequired()])