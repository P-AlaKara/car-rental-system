from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from config import config
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cors = CORS()
mail = Mail()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import main, auth, dashboard, bookings, users, cars, drivers, payments, reports, admin
    
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(bookings.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(cars.bp)
    app.register_blueprint(drivers.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(admin.admin_bp)
    
    # Register API blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register Xero blueprint
    from app.routes.xero import xero_bp
    app.register_blueprint(xero_bp)
    
    # Register webhooks
    from app.routes.webhooks import webhooks_bp
    app.register_blueprint(webhooks_bp)
    
    # Add route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        import os
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(os.path.join(app.root_path, '..', upload_folder), filename)
    
    # Add context processor to make datetime and models available in templates
    @app.context_processor
    def inject_globals():
        from app.models import Booking, Car, User, Payment, Driver
        return {
            'datetime': datetime,
            'Booking': Booking,
            'Car': Car,
            'User': User,
            'Payment': Payment,
            'Driver': Driver
        }
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app