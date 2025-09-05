from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
try:
    from flask_mail import Mail
except Exception:
    Mail = None
from config import config
import os
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cors = CORS()
mail = Mail() if Mail else None


def create_app(config_name='default'):
    """Application factory pattern."""
    # Auto-select testing config when running under pytest unless explicitly overridden
    try:
        import os as _os
        if config_name == 'default' and _os.environ.get('PYTEST_CURRENT_TEST'):
            config_name = 'testing'
    except Exception:
        pass

    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    # Ensure remember cookie uses configured duration
    login_manager.remember_cookie_duration = app.config.get('REMEMBER_COOKIE_DURATION')
    migrate.init_app(app, db)
    cors.init_app(app)
    if mail:
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

    # Ensure upload base directory exists
    try:
        import os
        base_upload = app.config.get('UPLOAD_FOLDER', 'uploads')
        abs_base = os.path.join(app.root_path, '..', base_upload)
        os.makedirs(abs_base, exist_ok=True)
    except Exception as e:
        app.logger.warning(f"Could not ensure upload directory exists: {e}")
    
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
        # Sync PostgreSQL enums to include all Python Enum values
        try:
            if db.engine.dialect.name == 'postgresql':
                from sqlalchemy import text
                # Sync CarCategory enum
                try:
                    from app.models.car import CarCategory
                    with db.engine.begin() as conn:
                        existing_values = set(
                            row[0]
                            for row in conn.execute(
                                text(
                                    """
                                    SELECT e.enumlabel
                                    FROM pg_type t
                                    JOIN pg_enum e ON t.oid = e.enumtypid
                                    WHERE t.typname = :type_name
                                    """
                                ),
                                {"type_name": "carcategory"},
                            )
                        )
                        for member in CarCategory:
                            if member.value not in existing_values:
                                conn.execute(
                                    text("ALTER TYPE carcategory ADD VALUE IF NOT EXISTS :val"),
                                    {"val": member.value},
                                )
                except Exception as e:
                    # Log and continue; app should still start
                    app.logger.warning(f"Enum sync warning (CarCategory): {e}")

                # Ensure idempotency unique index exists for PayAdvantage payments
                try:
                    with db.engine.begin() as conn:
                        conn.execute(
                            text(
                                """
                                CREATE UNIQUE INDEX IF NOT EXISTS uq_payments_gateway_txn_payadvantage
                                ON payments (booking_id, gateway, gateway_transaction_id)
                                WHERE gateway = 'payadvantage' AND gateway_transaction_id IS NOT NULL
                                """
                            )
                        )
                except Exception as e:
                    app.logger.warning(f"Idempotency index creation skipped: {e}")
        except Exception as e:
            app.logger.warning(f"Enum sync skipped: {e}")
    
    return app