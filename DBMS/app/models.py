from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- User Loader and User Model (Unchanged) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# --- Association Tables for Many-to-Many Relationships ---
event_requires_task = db.Table('Event_Requires_Task',
    db.Column('event_id', db.Integer, db.ForeignKey('Emergency_Event.eme_id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('Task.task_id'), primary_key=True)
)

task_doneby_team = db.Table('Task_DoneBy_Team',
    db.Column('task_id', db.Integer, db.ForeignKey('Task.task_id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('Team.team_id'), primary_key=True)
)

# Using a model for this one to include the 'quantity' attribute
class Team_Has_Resource(db.Model):
    __tablename__ = 'Team_Has_Resource'
    team_id = db.Column(db.Integer, db.ForeignKey('Team.team_id'), primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('Resource.res_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    resource = db.relationship('Resource', back_populates='teams')
    team = db.relationship('Team', back_populates='resources')


# --- Main Entity Models ---

class Emergency_Event(db.Model):
    __tablename__ = 'Emergency_Event'
    eme_id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(100), nullable=False)
    affected_areas = db.relationship('Affected_Area', backref='event', lazy='dynamic', cascade="all, delete-orphan")
    tasks = db.relationship('Task', secondary=event_requires_task, lazy='subquery', backref=db.backref('events', lazy=True))
    
    def __repr__(self):
        return f'<Event {self.disaster_type}>'

class Affected_Area(db.Model):
    __tablename__ = 'Affected_Area'
    area_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    population = db.Column(db.Integer)
    damage_extent = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    event_id = db.Column(db.Integer, db.ForeignKey('Emergency_Event.eme_id'), nullable=False)
    individuals = db.relationship('Affected_Individual', backref='area', lazy='dynamic', cascade="all, delete-orphan")
    donations = db.relationship('Donation', backref='area', lazy='dynamic', cascade="all, delete-orphan")
    evacuations = db.relationship('Evacuation', backref='area', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Area {self.location}>'

class Affected_Individual(db.Model):
    __tablename__ = 'Affected_Individual'
    individual_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    injury_type = db.Column(db.String(100))
    severity = db.Column(db.String(50))
    area_id = db.Column(db.Integer, db.ForeignKey('Affected_Area.area_id'), nullable=False)

class Donation(db.Model):
    __tablename__ = 'Donation'
    donation_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    amount = db.Column(db.Numeric(10, 2))
    area_id = db.Column(db.Integer, db.ForeignKey('Affected_Area.area_id'), nullable=False)

class Team(db.Model):
    __tablename__ = 'Team'
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    team_leader = db.Column(db.String(100))
    personnel = db.Column(db.Integer)
    equipment = db.Column(db.String(255))
    evacuations = db.relationship('Evacuation', backref='team', lazy='dynamic')
    tasks = db.relationship('Task', secondary=task_doneby_team, lazy='subquery', backref=db.backref('teams', lazy=True))
    resources = db.relationship('Team_Has_Resource', back_populates='team', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Team {self.team_name}>'

class Evacuation(db.Model):
    __tablename__ = 'Evacuation'
    eva_id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    transport = db.Column(db.String(100))
    area_id = db.Column(db.Integer, db.ForeignKey('Affected_Area.area_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('Team.team_id'))

class Task(db.Model):
    __tablename__ = 'Task'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Task {self.task_name}>'

class Resource(db.Model):
    __tablename__ = 'Resource'
    res_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    teams = db.relationship('Team_Has_Resource', back_populates='resource', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Resource {self.type}>'