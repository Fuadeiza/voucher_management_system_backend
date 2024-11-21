# Voucher Management System API

A FastAPI-based system for managing company vouchers, with features for admin and attendant management.

## Features

- 👤 Admin Management
- 🏢 Company Management
- 🏪 Branch Management
- 👥 Attendant Management
- 🎫 Voucher Creation and Management
- 🔐 JWT Authentication
- 📊 Usage Statistics

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)

## Prerequisites

- Python 3.9+
- PostgreSQL
- pip (Python package installer)

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd voucher_management_system
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a .env file
```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_DB=voucher_db
DATABASE_URL=postgresql://your_user:your_password@localhost/voucher_db
JWT_SECRET_KEY=your_secret_key
```

5. Initialize the database
```bash
# Create database tables
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Project Structure

```
├── alembic/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── admin.py
│   │           ├── attendant.py
│   │           ├── branch.py
│   │           ├── company.py
│   │           └── voucher.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── schema/
│   │   ├── __init__.py
│   │   └── schema.py
│   └── main.py
├── requirements.txt
└── .env
```

## Running the Application

1. Start the server
```bash
uvicorn app.main:app --reload
```

2. Access the documentation:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Admin Routes
- POST `/api/v1/admin/login` - Admin login
- POST `/api/v1/admin/create` - Create admin account
- GET `/api/v1/admin/` - List all admins

### Branch Routes
- GET `/api/v1/branch/` - List all branches
- POST `/api/v1/branch/create` - Create new branch
- GET `/api/v1/branch/{branch_id}` - Get branch details

### Company Routes
- GET `/api/v1/company/` - List all companies
- POST `/api/v1/company/create` - Create new company
- GET `/api/v1/company/{company_id}` - Get company details
- GET `/api/v1/company/{company_id}/stats` - Get company voucher statistics

### Attendant Routes
- POST `/api/v1/attendant/login` - Attendant login
- POST `/api/v1/attendant/create` - Create attendant account
- GET `/api/v1/attendant/` - List all attendants
- GET `/api/v1/attendant/{attendant_id}` - Get attendant details
- GET `/api/v1/attendant/branch/{branch_id}` - List branch attendants

### Voucher Routes
- POST `/api/v1/voucher/create` - Create new voucher
- POST `/api/v1/voucher/verify/{code}` - Verify voucher
- POST `/api/v1/voucher/use/{code}` - Use voucher
- POST `/api/v1/voucher/invalidate/{code}` - Invalidate voucher
- POST `/api/v1/voucher/revert/{code}` - Revert voucher usage
- GET `/api/v1/voucher/company/{company_id}/stats` - Get company voucher stats

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Development

### Adding New Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Running Tests
```bash
pytest
```

## License

[Your License]

## Contributors

[Your Name]