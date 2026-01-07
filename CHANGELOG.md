# Changelog

All notable changes to the Hotel PMS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- JWT authentication for API endpoints
- Real-time WebSocket server
- Push notifications
- Multi-property support

---

## [0.2.0] - 2026-01-07

### Added

#### 🛂 Passport OCR Service (Production Ready)
- **MRZ (Machine Readable Zone) Parsing**
  - Full TD3 passport format support (44 chars x 2 lines)
  - Automatic extraction of: Full name, Surname, Given names, Passport number, Nationality, Date of birth, Gender, Expiry date, Issuing country
  - Check digit validation for data integrity
  - Confidence scoring based on validation results
- **OCR Backends**
  - Tesseract OCR (local, free) - requires `tesseract` installed
  - Google Cloud Vision API (placeholder for future integration)
- **Manual MRZ Entry**
  - Fallback interface for manual input when OCR fails
  - Validation of passport number format by country
- **Demo Mode**
  - Sample MRZ parsing for testing without real passport images
- **API Endpoints**
  - `POST /api/v1/passport/parse-mrz` - Parse MRZ text
  - `POST /api/v1/passport/demo` - Demo MRZ parsing
  - `POST /api/v1/passport/parse-image` - Parse passport image (requires Tesseract)

#### 🧹 Housekeeping & Maintenance Module (Production Ready)
- **Room Status Grid**
  - Visual status display: Clean 🟢, Occupied 🔵, Cleaning 🟡, Maintenance 🔴
  - One-click status updates
- **Task Assignment System**
  - Priority levels: Low, Normal, High, Urgent
  - Task types: checkout_clean, turndown, deep_clean, inspection
  - Staff assignment and tracking
- **Maintenance Issue Tracking**
  - Severity levels: Low, Medium, High, Urgent
  - Issue types: missing_item, damage, repair_needed
  - Image attachments (stored as paths/URLs)
  - Resolution tracking with notes
- **Staff Management**
  - Role-based assignments (housekeeping, maintenance)
  - Availability tracking
- **Backend API Endpoints**
  - `GET/POST /api/v1/housekeeping/tasks` - CRUD for cleaning tasks
  - `GET/POST /api/v1/housekeeping/issues` - Maintenance issues
  - `GET/PUT /api/v1/housekeeping/rooms/{id}/status` - Room status
  - `GET/POST /api/v1/housekeeping/staff` - Staff management

#### 📱 Mobile Responsive Design (Production Ready)
- **Bottom Navigation Bar** for mobile devices (< 768px)
- **Hamburger Menu** for sidebar toggle
- **Touch-Friendly Elements** (44px minimum touch targets)
- **iOS Safe Area Support** (env() inset values)
- **Responsive Breakpoints**
  - Desktop: > 1024px
  - Tablet: 768px - 1024px
  - Phone: < 768px
  - Small phone: < 480px

#### 💬 Auto-Response System (Mock/Demo)
- **8 Predefined Response Templates** for common guest issues:
  - Late check-in, WiFi problems, AC issues, Noise complaints
  - Hot water, Cleaning requests, Lock issues, General inquiry
- **Issue Type Detection** from guest messages
- **Staff Action Flagging** for issues requiring attention

#### 🔄 Real-time Updates Foundation (Mock/Demo)
- WebSocket simulation mode (polling fallback: 30s interval)
- Broadcast update events architecture
- Ready for real WebSocket implementation

---

## [0.1.0] - 2026-01-06

### Added

#### 🏗️ Project Initialization
- **FastAPI Backend Structure**
  - CORS middleware configured
  - API versioning (`/api/v1`)
  - Swagger UI (`/docs`) and ReDoc (`/redoc`)
- **SQLAlchemy ORM Models**
  - `Property` - Property/building information
  - `Room` - Room with TTLock integration
  - `Booking` - Booking from Channel Manager
  - `Guest` - Guest with passport data and XNC export status
  - `AccessCode` - Smart lock passcodes
  - `Staff` - User with roles (admin, owner, housekeeping, maintenance)
  - `HousekeepingLog` - Cleaning activity log
  - `MaintenanceIssue` - Issue tracking
- **Alembic Migration Configuration**
- **Environment Configuration** with `.env` support

#### 📊 Admin Dashboard (Frontend - Production Ready)
- **Modern Dark Theme** with glassmorphism effects
- **Dashboard Home**
  - Stats cards: Total Bookings, Today Check-ins, Today Check-outs, Occupancy Rate
  - Quick Actions: Sync Booking, Send Passcodes, Export XNC, Manage Locks
  - Today's Activity table with booking status
- **Bookings Management**
  - Full booking list with filters (Status, OTA)
  - Booking details modal
  - Status updates (Check-in, Check-out)
- **Room Status Grid**
  - Visual room cards with status colors
  - Click-to-update status
- **Guest Management**
  - Guest list with passport info
  - XNC export status tracking
- **XNC Report Generation**
  - Date picker for report date
  - Format selection (CSV, XML)
  - Pending guests selection
- **Smart Lock Management**
  - Lock status overview (battery, online status)
  - Remote unlock capability (UI only - requires real TTLock)
  - Passcode viewing

#### 🔌 Core Services

##### Channex Service (Mock Implementation)
**Status: 🧪 MOCK - Requires real API credentials**

Current mock features:
- Property listing
- Booking sync simulation
- Message sending simulation
- Webhook event simulation
- Feed polling simulation

**To enable production:**
1. Register at [Channex.io](https://channex.io)
2. Get API key from Staging/Production dashboard
3. Configure `.env`:
   ```
   CHANNEX_API_KEY=your_real_api_key
   CHANNEX_PROPERTY_ID=your_property_id
   CHANNEX_WEBHOOK_SECRET=your_webhook_secret
   ```
4. Set up webhook endpoint in Channex dashboard pointing to `/api/v1/webhooks/channex`

##### TTLock Service (Mock Implementation)
**Status: 🧪 MOCK - Requires real hardware and developer account**

Current mock features:
- Lock listing with battery/status simulation
- Passcode generation (random 6-digit codes)
- Lock/unlock command simulation
- Gateway listing

**To enable production:**
1. Purchase TTLock smart locks and G2 Gateway
2. Register developer account at [TTLock Open Platform](https://euopen.ttlock.com)
3. Create application and get credentials
4. Configure `.env`:
   ```
   TTLOCK_CLIENT_ID=your_client_id
   TTLOCK_CLIENT_SECRET=your_client_secret
   TTLOCK_USERNAME=your_ttlock_email
   TTLOCK_PASSWORD_MD5=md5_hash_of_password  # Use ttlock_service.md5_password()
   ```
5. Pair locks with gateway using TTLock app

##### Telegram Service (Stub Implementation)
**Status: 📝 STUB - Logs instead of sending messages**

Current stub features:
- Health check returning "stub"
- All notification methods log to console
- No actual messages sent

**To enable production:**
1. Create bot via [@BotFather](https://t.me/botfather) on Telegram
2. Get bot token
3. Create a group/channel and add bot
4. Get chat ID
5. Configure `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```
6. Replace `TelegramServiceStub` with real implementation using `python-telegram-bot`

##### XNC Service (Production Ready)
**Status: ✅ PRODUCTION - Generates valid NA17 format reports**

Features:
- NA17 template format (Thông tư 04/2015/TT-BCA)
- CSV export (primary - portal compatible)
- XML export (alternative)
- Printable text format for manual submission
- Vietnamese date formatting
- Gender translation
- Automatic file naming with timestamps

**Usage:**
1. Configure property info in API request
2. Select guests for export
3. Generate report (CSV recommended for portal upload)
4. Upload to [XNC Portal](https://hochiminh.xuatnhapcanh.gov.vn)

#### 📡 Backend API
- **CRUD Endpoints**: Properties, Rooms, Bookings, Guests, Locks
- **Dashboard Statistics**: `/api/v1/crud/stats`
- **Health Check**: `/health` with service status
- **Webhook Endpoints**: `/api/v1/webhooks/channex`

#### 💾 Database
- **SQLite** for local development (auto-created)
- **PostgreSQL** ready for production
- **Sample Data Seeding**: `init_db.py`

---

## [0.0.1] - 2026-01-05

### Added
- Initial project structure
- Requirements specification
- README documentation

---

## Feature Status Summary

| Feature | Status | Requirements to Enable |
|---------|--------|------------------------|
| **Frontend Dashboard** | ✅ Production | None - works out of the box |
| **Mobile Responsive** | ✅ Production | None |
| **Passport OCR - MRZ Parsing** | ✅ Production | None - pure Python |
| **Passport OCR - Image** | ⚠️ Requires Tesseract | Install Tesseract OCR |
| **Housekeeping Module** | ✅ Production | None |
| **XNC Report Export** | ✅ Production | None |
| **Booking Sync (Channex)** | 🧪 Mock | Channex API credentials |
| **Smart Lock (TTLock)** | 🧪 Mock | TTLock hardware + credentials |
| **Telegram Notifications** | 📝 Stub | Telegram Bot token |
| **Auto-Response System** | 🧪 Mock | Channex for real messages |
| **Real-time WebSocket** | 📝 Planned | Server implementation |
| **JWT Authentication** | 📝 Planned | Implementation needed |

---

## Future Roadmap

### v0.3.0 (Planned)
- [ ] PostgreSQL production database with migrations
- [ ] JWT authentication and role-based access
- [ ] Telegram Bot real integration with notification templates
- [ ] Real TTLock API integration with error handling

### v0.4.0 (Planned)
- [ ] Channex live integration with webhook handling
- [ ] Real-time WebSocket server (Socket.IO)
- [ ] Push notifications (Web Push API)
- [ ] Multi-property support with property switching

### v1.0.0 (Target)
- [ ] Production deployment on VPS
- [ ] XNC portal integration verified with real data
- [ ] Complete API documentation with examples
- [ ] User access control (roles/permissions)
- [ ] Reporting & analytics dashboard
- [ ] Backup & recovery system
- [ ] Mobile app (React Native) - optional

---

## Expansion Recommendations

### Short-term Improvements
1. **Enable PostgreSQL** - Migrate from SQLite for production stability
2. **Add Telegram Bot** - Immediate notifications for new bookings
3. **Implement JWT Auth** - Secure the API endpoints

### Medium-term Enhancements
1. **Integrate Channex** - Automate booking sync from OTAs
2. **Add TTLock Hardware** - Full smart lock automation
3. **Build Mobile App** - React Native for on-the-go management

### Long-term Vision
1. **AI-powered Pricing** - Dynamic rate optimization
2. **Guest Communication Hub** - Unified messaging across OTAs
3. **Revenue Analytics** - Business intelligence dashboard
4. **Multi-language Support** - Vietnamese, English, Chinese, Korean

---

[Unreleased]: https://github.com/your-org/hotel-pms/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/your-org/hotel-pms/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-org/hotel-pms/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/your-org/hotel-pms/releases/tag/v0.0.1
