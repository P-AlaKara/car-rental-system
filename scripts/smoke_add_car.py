from app import create_app, db
from app.models import Car, CarCategory, CarStatus


def main():
    app = create_app('testing')
    with app.app_context():
        db.create_all()

        # Clean slate
        Car.query.delete()
        db.session.commit()

        # Add with uppercase category
        car1 = Car(
            make='Test', model='Upper', year=2025,
            license_plate='UPP001', vin='VINUPP001',
            category=CarCategory.from_any('HATCHBACK'),
            seats=5, transmission='Automatic', fuel_type='Gasoline',
            daily_rate=50.0, weekly_rate=300.0, status=CarStatus.AVAILABLE
        )

        # Add with lowercase category
        car2 = Car(
            make='Test', model='Lower', year=2025,
            license_plate='LOW001', vin='VINLOW001',
            category=CarCategory.from_any('suv'),
            seats=5, transmission='Automatic', fuel_type='Gasoline',
            daily_rate=60.0, weekly_rate=360.0, status=CarStatus.AVAILABLE
        )

        db.session.add_all([car1, car2])
        db.session.commit()

        rows = Car.query.order_by(Car.id).all()
        for c in rows:
            print(f"{c.id}:{c.full_name}:{c.category.value}")


if __name__ == '__main__':
    main()

