# Aurora Motors - Car Rental Management System

A modern, full-featured car rental management system built with Flask (Python) for the backend and vanilla JavaScript for the frontend.

## Features

### Customer Features
- 🚗 Browse available vehicles
- 📅 Make online bookings
- 💳 Secure payment processing
- 📊 View booking history
- 👤 Manage profile

### Admin Features
- 📈 Comprehensive dashboard with analytics
- 🚙 Fleet management (add/edit/remove vehicles)
- 👥 User management
- 📋 Booking management
- 💰 Payment tracking and processing
- 👨‍✈️ Driver management
- 📊 Detailed reports and analytics
- 🔧 Maintenance tracking

## Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database management
- **Flask-Login** - User authentication
- **Flask-Migrate** - Database migrations
- **JWT** - API authentication
- **SQLite/PostgreSQL** - Database

### Frontend
- **HTML5/CSS3** - Modern, responsive design
- **JavaScript** - Interactive functionality
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone or navigate to the NEW-BUILD directory:**
```bash
cd NEW-BUILD
```

2. **Create a virtual environment:**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables:**
```bash
cp .env.example .env
```
Edit the `.env` file with your configuration settings.

6. **Initialize the database:**
```bash
python run.py init_db
```

7. **Seed the database with sample data (optional):**
```bash
python run.py seed_db
```

8. **Run the application:**
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Webhooks

Pay Advantage webhook endpoint:

- URI: `/webhooks/payadvantage`
- Full URL: `${APP_URL}/webhooks/payadvantage`
- Healthcheck: `${APP_URL}/webhooks/payadvantage/health`

Configure environment variables:

- `PAY_ADVANTAGE_API_URL` (optional)
- `PAY_ADVANTAGE_USERNAME`
- `PAY_ADVANTAGE_PASSWORD`
- `PAY_ADVANTAGE_WEBHOOK_SECRET` (used for HMAC verification)

Signature verification:

- The app validates `X-PayAdvantage-Signature` (or `X-PayAdvantage-Signature-SHA256`) header containing an HMAC-SHA256 of the raw body using `PAY_ADVANTAGE_WEBHOOK_SECRET`. Accepts either `<hex>` or `sha256=<hex>` format.

## Default Credentials

### Admin Account
- **Email:** admin@auroramotors.com
- **Password:** admin123

### Sample Customer Accounts (if seeded)
- **Email:** customer1@example.com
- **Password:** password123

**Important:** Change the default passwords after first login!

## Project Structure

```
NEW-BUILD/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── models/            # Database models
│   │   ├── user.py       # User model
│   │   ├── car.py        # Car model
│   │   ├── booking.py    # Booking model
│   │   ├── payment.py    # Payment model
│   │   ├── driver.py     # Driver model
│   │   └── maintenance.py # Maintenance model
│   ├── routes/            # Route blueprints
│   │   ├── auth.py       # Authentication routes
│   │   ├── main.py       # Main/public routes
│   │   ├── dashboard.py  # Admin dashboard routes
│   │   ├── bookings.py   # Booking management
│   │   ├── cars.py       # Fleet management
│   │   ├── users.py      # User management
│   │   ├── drivers.py    # Driver management
│   │   ├── payments.py   # Payment processing
│   │   ├── reports.py    # Reports and analytics
│   │   └── api.py        # REST API endpoints
│   └── utils/             # Utility functions
│       └── decorators.py  # Custom decorators
├── static/                # Static files
│   ├── css/              # Stylesheets
│   │   └── style.css     # Main stylesheet
│   ├── js/               # JavaScript files
│   │   └── main.js       # Main JavaScript
│   └── uploads/          # User uploads
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   └── pages/            # Page templates
├── migrations/            # Database migrations
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── run.py               # Application entry point
├── .env.example         # Environment variables template
└── README.md            # This file
```

## API Endpoints

The application includes a RESTful API for integration with external services.

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Resources
- `GET /api/cars` - List available cars
- `GET /api/bookings` - List user bookings
- `POST /api/bookings` - Create new booking
- `GET /api/payments` - List payments

## Database Models

### User
- Authentication and profile management
- Role-based access control (Customer, Driver, Manager, Admin)

### Car
- Vehicle information and specifications
- Availability tracking
- Pricing tiers (daily, weekly, monthly)

### Booking
- Reservation management
- Status tracking
- Pricing calculations

### Payment
- Transaction processing
- Multiple payment methods
- Refund handling

### Driver
- Driver profiles and credentials
- Assignment to bookings
- Performance tracking

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- JWT tokens for API access
- CSRF protection
- Input validation
- SQL injection prevention via ORM

## Deployment

### Production Considerations

1. **Database:** Switch from SQLite to PostgreSQL
2. **Secret Keys:** Generate strong secret keys
3. **HTTPS:** Enable SSL/TLS
4. **Environment:** Set `FLASK_ENV=production`
5. **Server:** Use Gunicorn or uWSGI
6. **Reverse Proxy:** Configure Nginx or Apache

### Example Gunicorn Command
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Troubleshooting

### Common Issues

1. **Database errors:** Run `python run.py init_db` to recreate tables
2. **Import errors:** Ensure virtual environment is activated
3. **Port already in use:** Change port in `.env` or use `PORT=5001 python run.py`

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please contact:
- Email: support@auroramotors.com
- Documentation: [Link to docs]

## Acknowledgments

- Flask community
- Contributors and testers
- Open source libraries used

---

**Aurora Motors** - Your trusted partner for car rentals 🚗