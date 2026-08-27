# Oson Savdo Backend

A FastAPI backend for inventory, sales, users, providers, and store statistics. The service uses PostgreSQL, SQLAlchemy, Alembic migrations, and JWT-based authentication.

## Oson Savdo Backend (O'zbekcha)

Ombor, savdo, foydalanuvchilar, ta'minotchilar va do'kon statistikasi uchun FastAPI backend xizmati. Loyiha PostgreSQL, SQLAlchemy, Alembic migratsiyalari va JWT autentifikatsiyasidan foydalanadi.

## Features / Imkoniyatlar

- User management with `SUPERUSER`, `ADMIN`, and `STAFF` roles
- JWT bearer authentication
- Store, category, product, and barcode management
- Provider and provider-payment management
- Inventory receiving, sales, debt payments, and sales history
- Store sales summaries and inventory statistics
- PostgreSQL database with Alembic migrations
- Docker and Docker Compose support

## Technology Stack / Texnologiyalar

- Python 3.9
- FastAPI and Uvicorn
- SQLAlchemy and Alembic
- PostgreSQL 16
- Pydantic
- JWT via `python-jose`
- Docker Compose

## Project Structure / Loyiha tuzilishi

```text
app.py                 FastAPI application entry point
routes/                User, product, sales, and statistics endpoints
auth/                  Password and JWT authentication
dependencies/          Database and authorization dependencies
store/                 SQLAlchemy models and Pydantic schemas
alembic/               Database migration scripts
Dockerfile             API image definition
docker-compose.yml     API and PostgreSQL services
log_config.yaml        Uvicorn logging configuration
```

## Configuration / Sozlamalar

Copy `.env.example` to `.env` and set real values. Never commit `.env`.

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE
JWT_SECRET=your-long-random-jwt-secret
JWT_ALGORITHM=HS256
SESSION_SECRET=your-different-long-random-session-secret
```

When using Docker Compose, the API automatically connects to the `db` service. PostgreSQL container credentials can be customized with:

```env
POSTGRES_DB=oson_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

Keep the database values consistent with the `DATABASE_URL` used by the API.

## Run with Docker / Docker orqali ishga tushirish

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`.

Interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The API container waits for PostgreSQL, runs `alembic upgrade head`, and then starts Uvicorn with `log_config.yaml`.

## Run Locally / Lokal ishga tushirish

1. Create and activate a Python 3.9 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env` with a reachable PostgreSQL database.
4. Apply migrations:

```bash
alembic upgrade head
```

5. Start the API:

```bash
uvicorn app:my_app --reload --log-config log_config.yaml
```

## Authentication Flow / Autentifikatsiya tartibi

1. Create the initial superuser with `POST /super-user-create`.
2. Obtain a bearer token with `POST /token` using OAuth2 form fields:
   - `username`
   - `password`
3. Send the token in the request header:

```text
Authorization: Bearer <access-token>
```

The API uses role-based access for administrative, staff, inventory, sales, and statistics operations.

## Main Endpoints / Asosiy endpointlar

| Area | Endpoints |
| --- | --- |
| Authentication | `POST /token`, `POST /super-user-create` |
| Users | `/staffs`, `/admin-user-create`, `/staff-user-create`, password reset and delete endpoints |
| Products | `/product`, `/product-create`, `/product-update`, `/product-delete` |
| Categories | `/categories`, `/category-create`, `/category-update` |
| Providers | `/providers`, `/provider-create`, `/provider-edit`, `/providerpay` |
| Inventory | `/product-enter`, `/products-in`, inventory reports |
| Sales | `/sale`, `/sales`, `/salepay`, `/sale-delete` |
| Statistics | `/stores/sales-summary`, `/inventory/value`, and related reports |

Use Swagger UI at `/docs` for complete request and response schemas.

## Database Migrations / Ma'lumotlar bazasi migratsiyalari

Migration files in `alembic/versions/` and the Alembic configuration belong in the repository. The PostgreSQL data volume is managed by Docker and should not be committed.

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

## Logging / Loglar

Uvicorn uses `log_config.yaml`. Docker Compose logs are available with:

```bash
docker compose logs -f api
```

The configured file handler writes `uvicorn.log` inside the API container.

## License

No license has been specified for this project yet.
