from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from app import db, limiter
from app.models import User, Emergency_Event, Affected_Area, Affected_Individual, Donation, Team, Task, Resource, Evacuation, Team_Has_Resource
from app.forms import LoginForm, RegistrationForm, EventForm, TeamForm, TaskForm, ResourceForm, AffectedAreaForm, AffectedIndividualForm, DonationForm, EvacuationForm

bp = Blueprint('main', __name__)

# --- DECORATOR FOR ADMIN ACCESS ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access is required for this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- MAIN AND AUTHENTICATION ROUTES (Unchanged) ---
@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Welcome')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    # ... registration logic remains the same ...
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


# --- EMERGENCY EVENT CRUD (Updated for M:N with Tasks) ---
@bp.route('/events')
@login_required
def events():
    all_events = Emergency_Event.query.all()
    return render_template('events.html', events=all_events)

@bp.route('/event/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_event():
    form = EventForm()
    form.tasks.choices = [(t.task_id, t.task_name) for t in Task.query.order_by('task_name').all()]
    if form.validate_on_submit():
        event = Emergency_Event(disaster_type=form.disaster_type.data)
        for task_id in form.tasks.data:
            task = Task.query.get(task_id)
            event.tasks.append(task)
        db.session.add(event)
        db.session.commit()
        flash('The event has been created!', 'success')
        return redirect(url_for('main.events'))
    return render_template('event_form.html', title='New Event', form=form)

@bp.route('/event/<int:event_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_event(event_id):
    event = Emergency_Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    form.tasks.choices = [(t.task_id, t.task_name) for t in Task.query.order_by('task_name').all()]
    if form.validate_on_submit():
        event.disaster_type = form.disaster_type.data
        event.tasks.clear()
        for task_id in form.tasks.data:
            task = Task.query.get(task_id)
            event.tasks.append(task)
        db.session.commit()
        flash('The event has been updated!', 'success')
        return redirect(url_for('main.events'))
    elif request.method == 'GET':
        form.tasks.data = [task.task_id for task in event.tasks]
    return render_template('event_form.html', title='Update Event', form=form)

@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Emergency_Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('The event has been deleted!', 'success')
    return redirect(url_for('main.events'))


# --- TEAM CRUD (Updated for M:N with Tasks) ---
@bp.route('/teams')
@login_required
def teams():
    all_teams = Team.query.all()
    return render_template('teams.html', teams=all_teams)

@bp.route('/team/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_team():
    form = TeamForm()
    form.tasks.choices = [(t.task_id, t.task_name) for t in Task.query.order_by('task_name').all()]
    if form.validate_on_submit():
        team = Team(team_name=form.team_name.data, team_leader=form.team_leader.data, personnel=form.personnel.data, equipment=form.equipment.data)
        for task_id in form.tasks.data:
            task = Task.query.get(task_id)
            team.tasks.append(task)
        db.session.add(team)
        db.session.commit()
        flash('The team has been created!', 'success')
        return redirect(url_for('main.teams'))
    return render_template('team_form.html', title='New Team', form=form)

@bp.route('/team/<int:team_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team)
    form.tasks.choices = [(t.task_id, t.task_name) for t in Task.query.order_by('task_name').all()]
    if form.validate_on_submit():
        team.team_name = form.team_name.data
        team.team_leader = form.team_leader.data
        team.personnel = form.personnel.data
        team.equipment = form.equipment.data
        team.tasks.clear()
        for task_id in form.tasks.data:
            task = Task.query.get(task_id)
            team.tasks.append(task)
        db.session.commit()
        flash('The team has been updated!', 'success')
        return redirect(url_for('main.teams'))
    elif request.method == 'GET':
        form.tasks.data = [task.task_id for task in team.tasks]
    return render_template('team_form.html', title='Update Team', form=form)

@bp.route('/team/<int:team_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('The team has been deleted!', 'success')
    return redirect(url_for('main.teams'))


# --- TASK CRUD ---
@bp.route('/tasks')
@login_required
def tasks():
    all_tasks = Task.query.all()
    return render_template('tasks.html', tasks=all_tasks)

@bp.route('/task/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(task_name=form.task_name.data)
        db.session.add(task)
        db.session.commit()
        flash('The task has been created!', 'success')
        return redirect(url_for('main.tasks'))
    return render_template('task_form.html', title='New Task', form=form)

@bp.route('/task/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.task_name = form.task_name.data
        db.session.commit()
        flash('The task has been updated!', 'success')
        return redirect(url_for('main.tasks'))
    return render_template('task_form.html', title='Update Task', form=form)

@bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('The task has been deleted!', 'success')
    return redirect(url_for('main.tasks'))


# --- RESOURCE CRUD ---
@bp.route('/resources')
@login_required
def resources():
    all_resources = Resource.query.all()
    return render_template('resources.html', resources=all_resources)

@bp.route('/resource/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_resource():
    form = ResourceForm()
    form.team_id.choices = [(t.team_id, t.team_name) for t in Team.query.order_by('team_name').all()]
    if form.validate_on_submit():
        resource = Resource(type=form.type.data)
        db.session.add(resource)
        db.session.flush()  # to get res_id
        for team_id in form.team_id.data:
            team_resource = Team_Has_Resource(team_id=team_id, res_id=resource.res_id, quantity=1)
            db.session.add(team_resource)
        db.session.commit()
        flash('The resource has been created!', 'success')
        return redirect(url_for('main.resources'))
    return render_template('resource_form.html', title='New Resource', form=form)

@bp.route('/resource/<int:res_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_resource(res_id):
    resource = Resource.query.get_or_404(res_id)
    form = ResourceForm(obj=resource)
    form.team_id.choices = [(t.team_id, t.team_name) for t in Team.query.order_by('team_name').all()]
    if form.validate_on_submit():
        resource.type = form.type.data
        resource.team_id = form.team_id.data if form.team_id.data else None
        db.session.commit()
        flash('The resource has been updated!', 'success')
        return redirect(url_for('main.resources'))
    elif request.method == 'GET':
        form.type.data = resource.type
        form.team_id.data = resource.team_id
    return render_template('resource_form.html', title='Update Resource', form=form)

@bp.route('/resource/<int:res_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_resource(res_id):
    resource = Resource.query.get_or_404(res_id)
    db.session.delete(resource)
    db.session.commit()
    flash('The resource has been deleted!', 'success')
    return redirect(url_for('main.resources'))


# --- AFFECTED AREA CRUD ---
@bp.route('/areas')
@login_required
def areas():
    all_areas = Affected_Area.query.all()
    return render_template('affected_areas.html', areas=all_areas)

@bp.route('/area/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_area():
    form = AffectedAreaForm()
    form.event_id.choices = [(e.eme_id, e.disaster_type) for e in Emergency_Event.query.order_by('disaster_type').all()]
    if form.validate_on_submit():
        area = Affected_Area(
            location=form.location.data,
            population=form.population.data,
            damage_extent=form.damage_extent.data,
            start_date=form.start_date.data,
            event_id=form.event_id.data
        )
        db.session.add(area)
        db.session.commit()
        flash('The area has been created!', 'success')
        return redirect(url_for('main.areas'))
    return render_template('affected_area_form.html', title='New Area', form=form)

@bp.route('/area/<int:area_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_area(area_id):
    area = Affected_Area.query.get_or_404(area_id)
    form = AffectedAreaForm(obj=area)
    form.event_id.choices = [(e.eme_id, e.disaster_type) for e in Emergency_Event.query.order_by('disaster_type').all()]
    if form.validate_on_submit():
        area.location = form.location.data
        area.population = form.population.data
        area.damage_extent = form.damage_extent.data
        area.start_date = form.start_date.data
        area.event_id = form.event_id.data
        db.session.commit()
        flash('The area has been updated!', 'success')
        return redirect(url_for('main.areas'))
    return render_template('affected_area_form.html', title='Update Area', form=form)

@bp.route('/area/<int:area_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_area(area_id):
    area = Affected_Area.query.get_or_404(area_id)
    db.session.delete(area)
    db.session.commit()
    flash('The area has been deleted!', 'success')
    return redirect(url_for('main.areas'))


# --- AFFECTED INDIVIDUAL CRUD ---
@bp.route('/individuals')
@login_required
def individuals():
    all_individuals = Affected_Individual.query.all()
    return render_template('affected_individuals.html', individuals=all_individuals)

@bp.route('/individual/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_individual():
    form = AffectedIndividualForm()
    form.area_id.choices = [(a.area_id, a.location) for a in Affected_Area.query.order_by('location').all()]
    if form.validate_on_submit():
        individual = Affected_Individual(
            name=form.name.data,
            injury_type=form.injury_type.data,
            severity=form.severity.data,
            area_id=form.area_id.data
        )
        db.session.add(individual)
        db.session.commit()
        flash('The individual has been created!', 'success')
        return redirect(url_for('main.individuals'))
    return render_template('affected_individual_form.html', title='New Individual', form=form)

@bp.route('/individual/<int:individual_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_individual(individual_id):
    individual = Affected_Individual.query.get_or_404(individual_id)
    form = AffectedIndividualForm(obj=individual)
    form.area_id.choices = [(a.area_id, a.location) for a in Affected_Area.query.order_by('location').all()]
    if form.validate_on_submit():
        individual.name = form.name.data
        individual.injury_type = form.injury_type.data
        individual.severity = form.severity.data
        individual.area_id = form.area_id.data
        db.session.commit()
        flash('The individual has been updated!', 'success')
        return redirect(url_for('main.individuals'))
    return render_template('affected_individual_form.html', title='Update Individual', form=form)

@bp.route('/individual/<int:individual_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_individual(individual_id):
    individual = Affected_Individual.query.get_or_404(individual_id)
    db.session.delete(individual)
    db.session.commit()
    flash('The individual has been deleted!', 'success')
    return redirect(url_for('main.individuals'))


# --- DONATION CRUD ---
@bp.route('/donations')
@login_required
def donations():
    all_donations = Donation.query.all()
    return render_template('donations.html', donations=all_donations)

@bp.route('/donation/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_donation():
    form = DonationForm()
    form.area_id.choices = [(a.area_id, a.location) for a in Affected_Area.query.order_by('location').all()]
    if form.validate_on_submit():
        donation = Donation(
            name=form.name.data,
            type=form.type.data,
            amount=form.amount.data,
            area_id=form.area_id.data
        )
        db.session.add(donation)
        db.session.commit()
        flash('The donation has been created!', 'success')
        return redirect(url_for('main.donations'))
    return render_template('donation_form.html', title='New Donation', form=form)

@bp.route('/donation/<int:donation_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    form = DonationForm(obj=donation)
    form.area_id.choices = [(a.area_id, a.location) for a in Affected_Area.query.order_by('location').all()]
    if form.validate_on_submit():
        donation.name = form.name.data
        donation.type = form.type.data
        donation.amount = form.amount.data
        donation.area_id = form.area_id.data
        db.session.commit()
        flash('The donation has been updated!', 'success')
        return redirect(url_for('main.donations'))
    return render_template('donation_form.html', title='Update Donation', form=form)

@bp.route('/donation/<int:donation_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    flash('The donation has been deleted!', 'success')
    return redirect(url_for('main.donations'))


# --- EVACUATION CRUD ---
@bp.route('/evacuations')
@login_required
def evacuations():
    all_evacuations = Evacuation.query.all()
    return render_template('evacuations.html', evacuations=all_evacuations)

@bp.route('/evacuation/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_evacuation():
    form = EvacuationForm()
    form.area_id.choices = [(a.area_id, a.location) for a in Affected_Area.query.order_by('location').all()]
    form.team_id.choices = [(t.team_id, t.team_name) for t in Team.query.order_by('team_name').all()]
    if form.validate_on_submit():
        evacuation = Evacuation(
            destination=form.destination.data,
            location=form.location.data,
            transport=form.transport.data,
            area_id=form.area_id.data,
            team_id=form.team_id.data if form.team_id.data else None
        )
        db.session.add(evacuation)
        db.session.commit()
        flash('The evacuation has been created!', 'success')
        return redirect(url_for('main.evacuations'))
    return render_template('evacuation_form.html', title='New Evacuation', form=form)

@bp.route('/evacuation/<int:eva_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_evacuation(eva_id):
    evacuation = Evacuation.query.get_or_404(eva_id)
    form = EvacuationForm(obj=evacuation)
    form.area_id.choices = [(a.area_id, a.location) for a in Affected_Area.query.order_by('location').all()]
    form.team_id.choices = [(t.team_id, t.team_name) for t in Team.query.order_by('team_name').all()]
    if form.validate_on_submit():
        evacuation.destination = form.destination.data
        evacuation.location = form.location.data
        evacuation.transport = form.transport.data
        evacuation.area_id = form.area_id.data
        evacuation.team_id = form.team_id.data if form.team_id.data else None
        db.session.commit()
        flash('The evacuation has been updated!', 'success')
        return redirect(url_for('main.evacuations'))
    return render_template('evacuation_form.html', title='Update Evacuation', form=form)

@bp.route('/evacuation/<int:eva_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_evacuation(eva_id):
    evacuation = Evacuation.query.get_or_404(eva_id)
    db.session.delete(evacuation)
    db.session.commit()
    flash('The evacuation has been deleted!', 'success')
    return redirect(url_for('main.evacuations'))
