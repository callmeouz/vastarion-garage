# Vastarion Garage

**Backend API for Vehicle Management & Role-Based Access Control** — Register, manage, share vehicles, and track service history.

> Built with FastAPI, PostgreSQL, SQLAlchemy, and JWT-based authentication. Includes a minimal frontend interface for interaction.

---

## Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure signup/login with bcrypt password hashing |
| 🚗 **Vehicle Management** | Register vehicles with VIN, brand, model, year, mileage, color |
| 👥 **Access Sharing** | Share vehicles with other users (viewer / editor / driver roles) |
| 🔧 **Service Records** | Add, view, and delete maintenance history per vehicle |
| 🛡️ **Role-Based Access** | Owners have full control; editors can modify; viewers can read |
| 🗑️ **Soft Delete** | Vehicles are soft-deleted (recoverable) |
| 👤 **User Profile** | See your account info (email, role) in the navbar |

## Tech Stack & Architecture

| Layer / Domain | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy |
| **Migrations** | Alembic |
| **Database** | PostgreSQL |
| **Auth** | JWT (python-jose) |
| **Password Hashing** | bcrypt |
| **Testing** | Pytest |

## Project Structure

```
Vehicle Access/
├── main.py                 # FastAPI app entry point
├── app/
│   ├── models.py           # SQLAlchemy models (User, Vehicle, VehicleAccess, ServiceRecord)
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── crud.py             # Database operations
│   ├── utils.py            # Password hashing, JWT token creation
│   ├── dependencies.py     # Auth dependency (get_current_user)
│   └── database.py         # DB engine & session
├── routers/
│   ├── auth.py             # POST /auth/signup, POST /auth/login
│   ├── vehicles.py         # CRUD + sharing + service records
│   └── users.py            # GET /users/me
├── static/
│   └── index_yeni.html     # Single-page frontend
├── alembic/                # Database migrations
├── tests/
│   └── test_api.py         # API tests
├── requirements.txt
├── .env.example
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL

### Installation

```bash
# Clone the repository
git clone https://github.com/callmeouz/vastarion-garage.git
cd vastarion-garage

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials and a secret key
```

### Database Setup

```bash
# Create the database in PostgreSQL
psql -U postgres -c "CREATE DATABASE vehicle_db;"

# Run migrations
alembic upgrade head
```

### Run the Server

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000/static/index_yeni.html](http://localhost:8000/static/index_yeni.html) in your browser.

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create a new account |
| POST | `/auth/login` | Login and get JWT token |

### Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vehicles/` | Register a new vehicle |
| GET | `/vehicles/my-vehicles` | List your vehicles |
| GET | `/vehicles/shared-with-me` | List vehicles shared with you |
| DELETE | `/vehicles/{vin}` | Soft-delete a vehicle |
| PUT | `/vehicles/{vin}` | Update vehicle details (owner only) |

### Vehicle Sharing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vehicles/{vin}/share` | Share a vehicle with a user |
| GET | `/vehicles/{vin}/access` | List who has access |
| DELETE | `/vehicles/{vin}/access/{user_id}` | Revoke access |

### Service Records
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vehicles/{vin}/service-records` | Add a service record |
| GET | `/vehicles/{vin}/service-records` | View service history |
| DELETE | `/vehicles/{vin}/service-records/{id}` | Delete a service record |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |

## Security

- Passwords hashed with **bcrypt**
- JWT tokens with configurable expiration
- Environment variables for secrets (`.env`)
- Input validation via Pydantic
- Role-based endpoint authorization

## Tests

```bash
python -m pytest tests/test_api.py -v
```

15 tests covering:
- Auth (signup, login, password validation, duplicate check)
- Vehicles (create, list, update, delete, unauthorized access)
- Users (profile endpoint)
- Healthcheck

## Architectural Decisions

This project implements production-oriented backend practices:

- JWT-based authentication with bcrypt password hashing
- Role-Based Access Control (owner, editor, viewer)
- Soft-delete pattern to prevent accidental data loss
- Migration-based schema management with Alembic
- Modular router separation (auth, vehicles, users)
- Environment-based configuration using `.env`
- Strict input validation with Pydantic v2

The goal was to design a secure, maintainable, and scalable backend service
that goes beyond simple CRUD operations.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact & Creator

**Oğuzhan Yılmaz** - GitHub: [@callmeouz](https://github.com/callmeouz)
- Email: [oguzhanyilmaz.159@gmail.com](mailto:oguzhanyilmaz.159@gmail.com)

*Developed by Oğuzhan Yılmaz.*
