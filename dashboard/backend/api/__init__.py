"""Centralized API imports for all endpoints."""

# This file ensures all API modules are imported and available
# Each API module should provide a register_*_routes function

# Import registration functions
from .healthy import register_healthy_routes
from .botconfig import register_botconfig_routes

# List of all available registration functions
# Add new registration functions here as APIs are created
API_REGISTRARS = [
    register_healthy_routes,
    register_botconfig_routes,
    # register_users_routes,  # Example for future APIs
    # register_products_routes,  # Example for future APIs
]

def register_all_routes(app):
    """Register all API routes from all modules."""
    for registrar in API_REGISTRARS:
        registrar(app)