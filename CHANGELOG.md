# Changelog

All notable changes to the Hotel PMS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- PostgreSQL database migration
- Telegram Bot notifications integration
- TTLock real API integration (pending developer account)
- Channex real API integration (pending staging account)
- JWT authentication for API endpoints
- XNC portal XML format validation
- Production deployment configuration

---

## [0.2.0] - 2026-01-07

### Added
- **Passport OCR Service**
  - MRZ (Machine Readable Zone) parsing for TD3 passports
  - Support for Tesseract OCR backend
  - Manual MRZ entry fallback
  - Apply extracted data to guest records
  - Demo mode for testing

- **Housekeeping & Maintenance Module**
  - Room cleaning status grid (Clean, Occupied, Cleaning, Maintenance)
  - Task assignment system with priority levels
  - Maintenance issue reporting and tracking
  - Staff management API
  - Backend API endpoints: `/housekeeping/tasks`, `/housekeeping/issues`, `/housekeeping/rooms`, `/housekeeping/staff`

- **Mobile Responsive Design**
  - Bottom navigation bar for mobile devices
  - Hamburger menu for sidebar toggle
  - Touch-friendly elements (44px minimum)
  - iOS safe area support
  - Tablet and phone breakpoints (1024px, 768px, 480px)

- **Auto-Response System**
  - 8 predefined response templates for common guest issues
  - Issue type detection (late checkin, wifi, AC, noise, etc.)
  - Staff action flagging for issues requiring attention

- **Real-time Updates Foundation**
  - WebSocket simulation mode
  - Broadcast update events
  - Polling fallback mechanism (30s interval)

---

## [0.1.0] - 2026-01-06

### Added
- **Project Initialization**
  - FastAPI backend structure
  - SQLAlchemy ORM models (Property, Room, Booking, Guest, AccessCode, Staff, HousekeepingLog, MaintenanceIssue)
  - Alembic migration configuration
  - Environment configuration with `.env` support

- **Core Services**
  - Channex service (booking sync) - mock implementation
  - TTLock service (passcode generation) - mock implementation
  - XNC service (immigration report export)
  - Telegram service (notifications) - stub implementation

- **Admin Dashboard (Frontend)**
  - Modern dark theme with glassmorphism effects
  - Dashboard with stats cards (bookings, check-ins, check-outs, occupancy)
  - Bookings management with filtering
  - Room status grid
  - Guest management
  - XNC report generation form
  - Smart lock management interface

- **Backend API**
  - CRUD endpoints for properties, rooms, bookings, guests, locks
  - Dashboard statistics endpoint
  - Health check endpoint
  - Webhook endpoints for Channex integration

- **Database**
  - SQLite for local development
  - Sample data seeding script (`init_db.py`)

---

## [0.0.1] - 2026-01-05

### Added
- Initial project structure
- Requirements specification
- README documentation

---

## Future Roadmap

### v0.3.0 (Planned)
- [ ] PostgreSQL production database
- [ ] JWT authentication
- [ ] Telegram Bot integration
- [ ] Real TTLock API integration

### v0.4.0 (Planned)
- [ ] Channex live integration
- [ ] Real-time WebSocket server
- [ ] Push notifications
- [ ] Multi-property support

### v1.0.0 (Target)
- [ ] Production deployment
- [ ] XNC portal integration verified
- [ ] Complete API documentation
- [ ] User access control (roles/permissions)
- [ ] Reporting & analytics dashboard
- [ ] Backup & recovery system

---

[Unreleased]: https://github.com/your-org/hotel-pms/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/your-org/hotel-pms/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-org/hotel-pms/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/your-org/hotel-pms/releases/tag/v0.0.1
