"""
Hotel PMS API Routes
"""
from . import webhooks, bookings, rooms, reports, health, crud, passport, housekeeping

__all__ = ["bookings", "webhooks", "rooms", "reports", "health", "crud", "passport"]
