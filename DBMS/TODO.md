# TODO: Build Flask Emergency Management App

## 1. Remove duplicate models.py ✅
- Delete the root models.py file to avoid duplication with app/models.py.

## 2. Add missing forms in app/forms.py ✅
- Add AffectedIndividualForm for Affected_Individual model.
- Add DonationForm for Donation model.
- Add EvacuationForm for Evacuation model.
- Update TeamForm to include resource assignment if needed.

## 3. Add missing routes in app/routes.py
- Add update_team and delete_team routes.
- Add update_task and delete_task routes.
- Add full CRUD routes for Affected_Area (areas, new_area, update_area, delete_area).
- Add full CRUD routes for Affected_Individual (individuals, new_individual, update_individual, delete_individual).
- Add full CRUD routes for Donation (donations, new_donation, update_donation, delete_donation).
- Add full CRUD routes for Evacuation (evacuations, new_evacuation, update_evacuation, delete_evacuation).
- Add routes for assigning resources to teams (e.g., team/<id>/assign_resource).

## 4. Create missing templates
- Create app/templates/affected_areas.html (list areas).
- Create app/templates/affected_area_form.html (form for areas).
- Create app/templates/affected_individuals.html (list individuals).
- Create app/templates/affected_individual_form.html (form for individuals).
- Create app/templates/donations.html (list donations).
- Create app/templates/donation_form.html (form for donations).
- Create app/templates/evacuations.html (list evacuations).
- Create app/templates/evacuation_form.html (form for evacuations).
- Create app/templates/team_resource_form.html (for assigning resources to teams).

## 5. Update existing templates
- Update app/templates/base.html to include navigation links for new entities.
- Update app/templates/teams.html and team_form.html to include resource assignments if applicable.

## 6. Run database migrations
- Execute `flask db upgrade` to apply model changes to the database.

## 7. Test the application
- Run the app with `python run.py`.
- Create an admin user with `flask create-admin admin password`.
- Test login, CRUD operations for all entities, and relationships.
