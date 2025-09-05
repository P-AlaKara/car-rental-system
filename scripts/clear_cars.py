import os
import sys
import click
from flask import Flask


def create_app_from_env():
    """Import the Flask app using the configured environment."""
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from app import create_app, db  # noqa: E402
    config_name = os.environ.get('FLASK_ENV') or os.environ.get('FLASK_CONFIG') or 'default'
    app = create_app(config_name)
    return app, db


def delete_s3_asset(url):
    try:
        from app.services.storage import get_storage
        from flask import current_app
        storage = get_storage()
        return storage.delete(url)
    except Exception:
        return False


@click.command()
@click.option('--hard', is_flag=True, default=False, help='Hard delete cars; otherwise mark inactive.')
@click.option('--purge-assets', is_flag=True, default=False, help='Delete images/documents from storage too.')
def main(hard: bool, purge_assets: bool):
    app, db = create_app_from_env()
    from app.models import Car, Booking, Payment, VehiclePhoto, BookingPhoto, Maintenance  # noqa: E402

    with app.app_context():
        if purge_assets:
            cars = Car.query.all()
            for car in cars:
                # Delete main image
                if car.main_image:
                    delete_s3_asset(car.main_image)
                # Delete gallery images
                if car.images:
                    for img in car.images:
                        delete_s3_asset(img)
                # Delete document assets
                if car.documents:
                    for doc in car.documents:
                        url = doc.get('url') if isinstance(doc, dict) else None
                        if url:
                            delete_s3_asset(url)

        # Remove dependent records referencing bookings
        booking_ids = [b.id for b in Booking.query.all()]
        if booking_ids:
            VehiclePhoto.query.filter(VehiclePhoto.booking_id.in_(booking_ids)).delete(synchronize_session=False)
            BookingPhoto.query.filter(BookingPhoto.booking_id.in_(booking_ids)).delete(synchronize_session=False)
            Payment.query.filter(Payment.booking_id.in_(booking_ids)).delete(synchronize_session=False)

        # Remove maintenance linked to cars
        Maintenance.query.delete(synchronize_session=False)

        if hard:
            # Hard delete bookings then cars
            Booking.query.delete(synchronize_session=False)
            Car.query.delete(synchronize_session=False)
        else:
            # Soft delete cars
            for car in Car.query.all():
                car.is_active = False
        db.session.commit()
        click.echo('Cars cleared successfully.')


if __name__ == '__main__':
    main()

