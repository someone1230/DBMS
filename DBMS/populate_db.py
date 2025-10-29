from app import create_app, db
from app.models import *
from datetime import date
import random

app = create_app()

with app.app_context():
    # Clear existing data except user
    db.session.query(Team_Has_Resource).delete()
    db.session.query(event_requires_task).delete()
    db.session.query(task_doneby_team).delete()
    db.session.query(Evacuation).delete()
    db.session.query(Donation).delete()
    db.session.query(Affected_Individual).delete()
    db.session.query(Affected_Area).delete()
    db.session.query(Team).delete()
    db.session.query(Task).delete()
    db.session.query(Resource).delete()
    db.session.query(Emergency_Event).delete()
    db.session.commit()

    # Insert Emergency_Events
    events = []
    disaster_types = ['Flood', 'Earthquake', 'Hurricane', 'Fire', 'Tornado', 'Tsunami', 'Volcano', 'Drought']
    for i in range(20):
        event = Emergency_Event(disaster_type=random.choice(disaster_types))
        db.session.add(event)
        events.append(event)
    db.session.commit()

    # Insert Affected_Areas
    areas = []
    locations = ['Downtown', 'Suburb A', 'Rural Area', 'Coastal Zone', 'Mountain Region', 'City Center', 'Industrial Park', 'Residential Block']
    damage_extents = ['Minor', 'Moderate', 'Severe', 'Total']
    for i in range(20):
        area = Affected_Area(
            location=random.choice(locations) + f' {i+1}',
            population=random.randint(100, 10000),
            damage_extent=random.choice(damage_extents),
            start_date=date.today(),
            event_id=random.choice(events).eme_id
        )
        db.session.add(area)
        areas.append(area)
    db.session.commit()

    # Insert Affected_Individuals
    for i in range(20):
        individual = Affected_Individual(
            name=f'Person {i+1}',
            injury_type=random.choice(['Broken Bone', 'Burn', 'Cut', 'Concussion', None]),
            severity=random.choice(['Mild', 'Moderate', 'Severe', None]),
            area_id=random.choice(areas).area_id
        )
        db.session.add(individual)
    db.session.commit()

    # Insert Donations
    for i in range(20):
        donation = Donation(
            name=f'Donor {i+1}',
            type=random.choice(['Money', 'Supplies', 'Food', 'Medicine']),
            amount=random.uniform(100, 10000) if random.choice([True, False]) else None,
            area_id=random.choice(areas).area_id
        )
        db.session.add(donation)
    db.session.commit()

    # Insert Teams
    teams = []
    for i in range(20):
        team = Team(
            team_name=f'Team {i+1}',
            team_leader=f'Leader {i+1}',
            personnel=random.randint(5, 50),
            equipment=random.choice(['Vehicles, Tools', 'Medical Kits', 'Communication Devices', 'Heavy Machinery'])
        )
        db.session.add(team)
        teams.append(team)
    db.session.commit()

    # Insert Evacuations
    for i in range(20):
        evacuation = Evacuation(
            destination=f'Safe Zone {i+1}',
            location=random.choice(locations),
            transport=random.choice(['Bus', 'Truck', 'Helicopter', 'Boat']),
            area_id=random.choice(areas).area_id,
            team_id=random.choice(teams).team_id if random.choice([True, False]) else None
        )
        db.session.add(evacuation)
    db.session.commit()

    # Insert Tasks
    tasks = []
    task_names = ['Search and Rescue', 'Medical Aid', 'Food Distribution', 'Shelter Setup', 'Debris Removal', 'Water Supply', 'Power Restoration', 'Communication Setup']
    for i in range(20):
        task = Task(task_name=random.choice(task_names) + f' {i+1}')
        db.session.add(task)
        tasks.append(task)
    db.session.commit()

    # Insert Resources
    resources = []
    resource_types = ['Water', 'Food', 'Medicine', 'Blankets', 'Generators', 'Vehicles', 'Fuel', 'Tools']
    for i in range(20):
        resource = Resource(type=random.choice(resource_types))
        db.session.add(resource)
        resources.append(resource)
    db.session.commit()

    # Insert event_requires_task
    for event in events:
        for task in random.sample(tasks, random.randint(1, 5)):
            if not db.session.query(event_requires_task).filter_by(event_id=event.eme_id, task_id=task.task_id).first():
                db.session.execute(event_requires_task.insert().values(event_id=event.eme_id, task_id=task.task_id))
    db.session.commit()

    # Insert task_doneby_team
    for task in tasks:
        for team in random.sample(teams, random.randint(1, 3)):
            if not db.session.query(task_doneby_team).filter_by(task_id=task.task_id, team_id=team.team_id).first():
                db.session.execute(task_doneby_team.insert().values(task_id=task.task_id, team_id=team.team_id))
    db.session.commit()

    # Insert team_has_resource
    for team in teams:
        for resource in random.sample(resources, random.randint(1, 5)):
            if not Team_Has_Resource.query.filter_by(team_id=team.team_id, res_id=resource.res_id).first():
                team_resource = Team_Has_Resource(team_id=team.team_id, res_id=resource.res_id, quantity=random.randint(1, 100))
                db.session.add(team_resource)
    db.session.commit()

    print("Database populated with ~20 entries in each table.")
