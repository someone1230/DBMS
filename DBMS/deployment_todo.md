# TODO: Improvements and Deployment Guide for Flask Disaster Management App

This guide outlines the key improvements required before deploying the application to production. It focuses on security, reliability, performance, testing, and deployment best practices. Follow these steps sequentially to ensure a robust, secure deployment. Mark items as completed with [x] as you progress.

## 1. Security Enhancements
Security is critical for a disaster management app handling sensitive data like affected individuals and locations. Prioritize these to mitigate common web vulnerabilities.

- [ ] **Implement HTTPS**: Configure SSL/TLS certificates (use free Let's Encrypt via Certbot). Update app to enforce HTTPS redirects. In config.py, add `SESSION_COOKIE_SECURE = True` and `SESSION_COOKIE_HTTPONLY = True`.
- [ ] **Add Security Headers**: Install Flask-Talisman (`pip install Flask-Talisman`) and initialize it in app/__init__.py to set headers like Content-Security-Policy, X-Frame-Options, and Strict-Transport-Security.
- [ ] **Rate Limiting**: Install Flask-Limiter (`pip install Flask-Limiter`) and apply to login/register routes to prevent brute-force attacks. Example: `@limiter.limit("5 per minute")` on login.
- [ ] **Input Sanitization and Validation**: Enhance WTForms validators in forms.py (e.g., add EmailValidator for emails if added). Use bleach for HTML sanitization in any user-generated content.
- [ ] **Password Policies**: Update RegistrationForm to enforce stronger passwords (e.g., min length 8, include numbers/symbols via custom validator).
- [ ] **Role-Based Access**: Refine @admin_required decorator; add granular roles (e.g., 'viewer' for read-only access) in User model and routes.
- [ ] **Data Privacy**: Ensure compliance with GDPR/HIPAA if applicable; add consent fields to forms for personal data (e.g., Affected_Individual).
- [ ] **Secret Management**: Never commit .env; use platform secrets (e.g., Heroku Config Vars) for SECRET_KEY and DATABASE_URL.

## 2. Production Configuration
Separate development from production environments to avoid debug leaks.

- [ ] **Update config.py**: Add a ProductionConfig class inheriting from Config, with `DEBUG = False`, `TESTING = False`, and `SQLALCHEMY_RECORD_QUERIES = False`. Use `app.config.from_object('config.ProductionConfig')` in create_app for prod.
- [ ] **Environment-Specific Settings**: Create .env.prod and load based on FLASK_ENV (e.g., 'production'). Set PERMANENT_SESSION_LIFETIME to a shorter value in prod.
- [ ] **Disable Debug Mode**: In run.py, condition `debug=True` on `if __name__ == '__main__' and app.config['DEBUG']:` but use a WSGI server for prod (see Deployment Setup).

## 3. Database and Data Management
Ensure the database is production-ready and resilient.

- [ ] **Production DB Setup**: Migrate from SQLite (if used in dev) to PostgreSQL/MySQL. Set DATABASE_URL in .env (e.g., postgres://user:pass@host/db). Install psycopg2-binary for Postgres.
- [ ] **Run Migrations**: After setup, execute `flask db init` (if needed), `flask db migrate`, and `flask db upgrade` in prod. Add a post-deployment script for this.
- [ ] **Database Indexes and Optimization**: In models.py, add indexes to foreign keys (e.g., `db.Index('ix_affected_area_event_id', 'event_id')`). Use SQLAlchemy events for auto-indexing.
- [ ] **Backups and Recovery**: Set up automated backups (e.g., pg_dump for Postgres). Test restore process.
- [ ] **Seed Data**: Create a CLI command in run.py to seed initial data (e.g., default tasks/resources) for prod.

## 4. Dependencies and Environment
Lock and manage dependencies to avoid version conflicts.

- [ ] **Pin Dependencies**: Run `pip freeze > requirements.txt` after installing all (include gunicorn, etc.). Review for vulnerabilities with `pip-audit`.
- [ ] **Add .gitignore**: Ensure it includes `.env`, `*.pyc`, `__pycache__`, `instance/`, and `migrations/versions/*.py` (keep .ini).
- [ ] **Virtual Environment**: Document creation: `python -m venv venv; source venv/bin/activate; pip install -r requirements.txt`.

## 5. Error Handling, Logging, and Monitoring
Handle failures gracefully and log for debugging.

- [ ] **Custom Error Pages**: In routes.py, add `@bp.errorhandler(404)` and `@bp.errorhandler(500)` to render custom templates (create 404.html, 500.html in templates/).
- [ ] **Logging Setup**: In config.py, add `LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')`. Use Python's logging module; integrate with Sentry (`pip install sentry-sdk`) for error tracking.
- [ ] **Health Check Endpoint**: Add `@bp.route('/health')` returning JSON status (db connection, app uptime) for monitoring tools.
- [ ] **Input Error Handling**: In forms, add custom validation errors and flash them user-friendly.

## 6. Performance Optimizations
Scale for potential high traffic during disasters.

- [ ] **WSGI Server**: Replace dev server with Gunicorn (`pip install gunicorn`). Run as `gunicorn -w 4 -b 0.0.0.0:8000 run:app`.
- [ ] **Static Files**: Configure Nginx/Apache to serve app/static/. Compress CSS/JS.
- [ ] **Caching**: Install Flask-Caching (`pip install Flask-Caching`); cache query results (e.g., task lists) with Redis backend.
- [ ] **Database Optimization**: Use eager loading in queries (e.g., `Event.query.options(joinedload(Event.tasks))`) to reduce N+1 queries.
- [ ] **Pagination**: Add to list views (e.g., events()) using Flask-SQLAlchemy's paginate.

## 7. Testing
Verify functionality before deployment.

- [ ] **Unit Tests**: Create tests/ folder; use pytest (`pip install pytest pytest-flask`). Test models (e.g., User.set_password), forms validation, and route logic.
- [ ] **Integration Tests**: Test full CRUD flows with a test DB (use Flask's test_client). Cover relationships (e.g., assign task to event).
- [ ] **Security Tests**: Use Bandit for code scans, OWASP ZAP for vuln scanning.
- [ ] **Load Testing**: Use Locust to simulate users creating/updating records.
- [ ] **Run Tests**: Add `pytest` command; aim for 80% coverage with coverage.py.

## 8. Deployment Setup
Choose a platform and configure.

- [ ] **Platform Selection**: For simplicity, use Heroku (free tier); alternatives: AWS Elastic Beanstalk, DigitalOcean App Platform, or VPS with Docker.
- [ ] **Heroku-Specific** (if chosen):
  - Install Heroku CLI; `heroku create app-name`.
  - Add Procfile: `web: gunicorn run:app`.
  - Set config vars: `heroku config:set SECRET_KEY=prod_key DATABASE_URL=prod_url`.
  - Deploy: `git push heroku main`; run `heroku run flask db upgrade`.
- [ ] **Dockerization** (optional): Create Dockerfile (FROM python:3.9, COPY ., RUN pip install -r requirements.txt, CMD gunicorn), docker-compose.yml for local/prod.
- [ ] **Reverse Proxy**: Use Nginx: Configure to proxy to Gunicorn, serve static files, and handle SSL.
- [ ] **CI/CD**: Set up GitHub Actions: Lint (flake8), test (pytest), deploy on push to main.

## 9. Post-Deployment and Maintenance
Ensure ongoing reliability.

- [ ] **Monitoring**: Integrate New Relic or Datadog for app metrics; set alerts for errors/high CPU.
- [ ] **Backup Strategy**: Automate DB backups; store offsite (e.g., S3).
- [ ] **Scalability**: Prepare for horizontal scaling (multiple Gunicorn instances behind load balancer).
- [ ] **Documentation**: Update README.md with setup/run/deploy instructions, including diagrams of entity relationships.
- [ ] **User Feedback Loop**: Add a contact form or integrate analytics (Google Analytics) to track usage.

## General Deployment Steps
1. Complete all TODO items above.
2. Test locally in production mode: `export FLASK_ENV=production; python run.py`.
3. Deploy to staging environment first.
4. Smoke test: Login as admin, create sample data, verify relationships.
5. Go live; monitor logs for 24-48 hours.
6. Schedule regular updates: Dependency scans, security patches.

This prepares the app for secure, scalable deployment. Estimated effort: 1-2 weeks for a solo developer.
