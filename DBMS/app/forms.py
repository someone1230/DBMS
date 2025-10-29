from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, DateField, DecimalField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

# --- FORMS FOR ALL ENTITIES ---

class EventForm(FlaskForm):
    disaster_type = StringField('Disaster Type', validators=[DataRequired(), Length(max=100)])
    tasks = SelectMultipleField('Required Tasks', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Event')

class TeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired(), Length(max=100)])
    team_leader = StringField('Team Leader', validators=[Length(max=100), Optional()])
    personnel = IntegerField('Personnel Count', validators=[Optional()])
    equipment = StringField('Equipment', validators=[Length(max=255), Optional()])
    tasks = SelectMultipleField('Assigned Tasks', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Team')
    
class TaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Save Task')

class ResourceForm(FlaskForm):
    type = StringField('Resource Type', validators=[DataRequired(), Length(max=100)])
    team_id = SelectMultipleField('Assigned Teams', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Resource')

class AffectedAreaForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired(), Length(max=255)])
    population = IntegerField('Population', validators=[Optional()])
    damage_extent = StringField('Damage Extent', validators=[Length(max=255), Optional()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    event_id = SelectField('Emergency Event', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Area')

class AffectedIndividualForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    injury_type = StringField('Injury Type', validators=[Length(max=100), Optional()])
    severity = StringField('Severity', validators=[Length(max=50), Optional()])
    area_id = SelectField('Affected Area', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Individual')

class DonationForm(FlaskForm):
    name = StringField('Donor Name', validators=[DataRequired(), Length(max=100)])
    type = StringField('Donation Type', validators=[Length(max=50), Optional()])
    amount = DecimalField('Amount', places=2, validators=[Optional()])
    area_id = SelectField('Affected Area', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Donation')

class EvacuationForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired(), Length(max=255)])
    location = StringField('Location', validators=[Length(max=255), Optional()])
    transport = StringField('Transport', validators=[Length(max=100), Optional()])
    area_id = SelectField('Affected Area', coerce=int, validators=[DataRequired()])
    team_id = SelectField('Assigned Team', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Evacuation')
