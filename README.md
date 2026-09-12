# CyBreach Analytics Engine

The CyBreach Analytics Engine is a backend service that collects, stores, and provides analytics data for the CyBreach Arena platform.

## Technologies

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pydantic Settings
- Alembic

## Features

- Analytics record creation and management
- Dashboard analytics
- Credit flow analysis
- User engagement analysis
- Resilience score
- Resilience score trend
- Monthly analytics reports
- Pagination
- Filtering by tenant, report month, date range, and score
- Input validation
- Error handling
- CORS configuration
- Swagger API documentation

## Project Structure

    CyBreach-AnalyticsEngine/
    ├── app/
    │   ├── api/
    │   │   └── analytics_engine_routes.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── exceptions.py
    │   │   └── settings.py
    │   ├── database/
    │   │   └── db_connection.py
    │   ├── models/
    │   │   └── analytics_metrics.py
    │   ├── schemas/
    │   │   └── analytics_schema.py
    │   ├── services/
    │   │   └── analytics_engine_service.py
    │   └── main.py
    ├── alembic/
    ├── alembic.ini
    ├── requirements.txt
    └── README.md

## API Endpoints

### Analytics CRUD

- `POST /api/v1/analytics`
- `GET /api/v1/analytics`
- `GET /api/v1/analytics/{id}`
- `GET /api/v1/analytics/tenant/{tenant_id}`
- `PUT /api/v1/analytics/{id}`
- `DELETE /api/v1/analytics/{id}`

### Analytics Services

- `GET /api/v1/analytics/dashboard/{tenant_id}`
- `GET /api/v1/analytics/credit-flow/{tenant_id}`
- `GET /api/v1/analytics/engagement/{tenant_id}`
- `GET /api/v1/analytics/score/{tenant_id}`
- `GET /api/v1/analytics/score-trend/{tenant_id}`
- `GET /api/v1/analytics/report/{tenant_id}`

## Analytics Data

Each analytics record contains information such as:

- Tenant details
- Resilience score
- Credit balance and usage
- Total and active users
- Total visits
- Average session duration
- Average response time
- Uptime percentage
- Error count
- Additional metrics
- Report month
- Created and updated timestamps

## Pagination and Filtering

The analytics listing API supports pagination and filtering.

Available parameters include:

- `skip`
- `limit`
- `tenant_id`
- `report_month`
- `start_date`
- `end_date`
- `min_score`
- `max_score`

Example:

    GET /api/v1/analytics?skip=0&limit=10&tenant_id=tenant_123

## Database

The Analytics Engine uses SQLite as the database and SQLAlchemy as the ORM.

The database connection is configured through the application settings and environment variables.

Alembic is included for database migration management.

## Running the Application

Install the required dependencies:

    pip install -r requirements.txt

Start the FastAPI application:

    uvicorn app.main:app --reload

The API will be available at:

    http://127.0.0.1:8000

## API Documentation

Swagger UI:

    http://127.0.0.1:8000/api/docs

ReDoc:

    http://127.0.0.1:8000/api/redoc

## Architecture

The Analytics Engine follows a layered backend architecture:

    Client Request
          ↓
    FastAPI Routes
          ↓
    Service Layer
          ↓
    SQLAlchemy ORM
          ↓
    SQLite Database
          ↓
    JSON Response

## Error Handling

The application provides structured error responses for validation, missing records, and database-related errors.

Common response codes include:

- `200` – Successful request
- `201` – Resource created
- `400` – Bad request
- `404` – Resource not found
- `422` – Validation error
- `500` – Internal server error
