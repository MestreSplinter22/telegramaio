# Centralized API Structure

This directory contains all API endpoints for the TelegramaIO application.

## Structure

Each API module should follow this pattern:

```python
# Create a folder for your API (e.g., users, products, transactions)
# Inside the folder, create __init__.py with the following structure:

"""Description of your API module."""

from fastapi import FastAPI

def register_your_api_routes(app: FastAPI):
    """Register your API routes."""
    
    @app.get("/api/your-endpoint")
    async def your_endpoint():
        return {"message": "Hello from your API"}
```

## Adding New APIs

1. Create a new folder in `backend/api/` with your API name
2. Create `__init__.py` inside the folder following the pattern above
3. Add the registration function to the main API system in `backend/api/__init__.py`
4. Import and register the routes in `dashboard.py`

## Current APIs

- **healthy**: Health check endpoint (`/api/healthy`)
  - File: `backend/api/healthy/__init__.py`
  - Purpose: Basic API health check and database connectivity test

- **botconfig**: Bot configuration management (`/api/botconfig`)
  - File: `backend/api/botconfig/__init__.py`
  - Purpose: CRUD operations for BotConfig table using Reflex ORM
  - Endpoints:
    - `POST /api/botconfig` - Create new configuration
    - `GET /api/botconfig` - Get all configurations
    - `GET /api/botconfig/{key}` - Get configuration by key
    - `PUT /api/botconfig/{key}` - Update configuration by key
    - `DELETE /api/botconfig/{key}` - Delete configuration by key