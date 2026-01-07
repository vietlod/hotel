# 🏨 Hotel PMS - Property Management System

Hệ thống quản lý khách sạn/căn hộ dịch vụ tích hợp Channel Manager, Smart Lock và báo cáo XNC.

**Version:** 0.2.0  
**Status:** Development/Staging  
**Frontend URL:** https://hotel.khoviet.com  
**Backend Port:** 8002  
**Database Port:** 5434 (PostgreSQL)

---

## 🚀 Features Overview

### ✅ Production Ready Features

| Feature | Description |
|---------|-------------|
| **Admin Dashboard** | Modern dark theme UI with glassmorphism effects |
| **Booking Management** | View, filter, and manage bookings from all OTAs |
| **Room Status Grid** | Visual room management with one-click status updates |
| **Guest Management** | Guest records with passport info and XNC status |
| **Passport OCR** | MRZ parsing from passport Machine Readable Zone |
| **Housekeeping** | Task assignment, room status, maintenance tracking |
| **XNC Export** | NA17 format reports for immigration portal |
| **Mobile Responsive** | Full mobile/tablet support with touch-friendly UI |

### 🧪 Mock/Demo Features (Requires API Credentials)

| Feature | Description | Required |
|---------|-------------|----------|
| **Channex Sync** | Booking sync from Airbnb/Booking/Agoda/Trip | Channex API Key |
| **TTLock Integration** | Smart lock passcode generation | TTLock Hardware + Dev Account |
| **Telegram Notifications** | Instant alerts for bookings and issues | Telegram Bot Token |
| **Auto-Response** | Automated guest message replies | Channex Messaging API |

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph External["External Services"]
        OTA["OTAs\n(Airbnb/Booking/Agoda)"]
        Channex["Channex API\n(Channel Manager)"]
        TTLock["TTLock API\n(Smart Lock)"]
        Telegram["Telegram Bot\n(Notifications)"]
        XNC["XNC Portal\n(Immigration)"]
    end

    subgraph Frontend["Frontend (Port 8003)"]
        UI["Admin Dashboard\n(HTML/CSS/JS)"]
    end

    subgraph Backend["Backend (Port 8002)"]
        FastAPI["FastAPI Application"]
        subgraph Services["Services Layer"]
            ChannexSvc["Channex Service"]
            TTLockSvc["TTLock Service"]
            TelegramSvc["Telegram Service"]
            XNCSvc["XNC Service"]
            PassportSvc["Passport OCR Service"]
        end
        subgraph API["API Layer"]
            CRUD["CRUD Endpoints"]
            Webhooks["Webhook Handlers"]
            Reports["Report Generator"]
            HK["Housekeeping API"]
        end
    end

    subgraph Database["Database (Port 5434)"]
        PostgreSQL["PostgreSQL/SQLite"]
    end

    OTA --> Channex
    Channex -->|Webhooks| Webhooks
    Channex <-->|API| ChannexSvc
    TTLock <-->|API| TTLockSvc
    Telegram <-->|API| TelegramSvc
    XNCSvc -->|Export| XNC

    UI <-->|REST API| FastAPI
    FastAPI --> API
    API --> Services
    Services --> PostgreSQL
```

---

## 📁 Project Structure (Accurate)

```
HOTEL/
├── 📄 .env.example                    # Environment variables template
├── 📄 .gitignore                      # Git ignore rules
├── 📄 CHANGELOG.md                    # Version history & feature status
├── 📄 README.md                       # This documentation
├── 📄 Dockerfile                      # Backend Docker image
├── 📄 docker-compose.production.yml   # Production Docker Compose
├── 📄 nginx_hotel.khoviet.com.conf    # Nginx site configuration
│
├── 📁 backend/
│   ├── 📄 alembic.ini                 # Alembic configuration
│   ├── 📄 requirements.txt            # Python dependencies
│   ├── 📄 init_db.py                  # Database seeding script
│   ├── 📄 standalone_demo.py          # Standalone demo script
│   ├── 📄 hotel_pms.db                # SQLite database (dev)
│   │
│   ├── 📁 alembic/                    # Database migrations
│   │   ├── 📄 env.py                  # Migration environment
│   │   ├── 📄 script.py.mako          # Migration template
│   │   └── 📁 versions/               # Migration files
│   │
│   └── 📁 app/                        # Main application
│       ├── 📄 __init__.py
│       ├── 📄 main.py                 # FastAPI app entry point
│       ├── 📄 config.py               # Settings from environment
│       ├── 📄 database.py             # SQLAlchemy setup
│       ├── 📄 demo.py                 # Demo data generator
│       │
│       ├── 📁 api/                    # API route handlers
│       │   ├── 📄 __init__.py         # Router exports
│       │   ├── 📄 health.py           # GET /health
│       │   ├── 📄 crud.py             # CRUD endpoints (13KB)
│       │   ├── 📄 bookings.py         # Booking operations
│       │   ├── 📄 rooms.py            # Room management
│       │   ├── 📄 passport.py         # Passport OCR (8.5KB)
│       │   ├── 📄 housekeeping.py     # Housekeeping API (13.5KB)
│       │   ├── 📄 reports.py          # XNC report generation
│       │   └── 📄 webhooks.py         # Channex webhooks (9KB)
│       │
│       ├── 📁 models/                 # SQLAlchemy ORM models
│       │   └── 📄 __init__.py         # All models (10.5KB)
│       │
│       ├── 📁 schemas/                # Pydantic schemas
│       │   └── 📄 __init__.py         # All schemas (6.8KB)
│       │
│       ├── 📁 services/               # Business logic
│       │   ├── 📄 __init__.py         # Service exports
│       │   ├── 📄 channex_service.py  # Channel Manager (9.4KB)
│       │   ├── 📄 ttlock_service.py   # Smart Lock API (11KB)
│       │   ├── 📄 xnc_service.py      # XNC NA17 export (13.5KB)
│       │   ├── 📄 telegram_service.py # Telegram stub (2KB)
│       │   ├── 📄 passport_ocr_service.py # MRZ parser (13.8KB)
│       │   └── 📄 mock_services.py    # Mock implementations (15KB)
│       │
│       └── 📁 tasks/                  # Celery tasks (optional)
│           └── 📄 __init__.py
│
├── 📁 frontend/
│   ├── 📄 index.html                  # Main HTML (20KB)
│   ├── 📄 app.js                      # JavaScript logic (65KB)
│   ├── 📄 styles.css                  # CSS styles (24KB)
│   ├── 📄 nginx.conf                  # Container Nginx config
│   └── 📄 Dockerfile                  # Frontend Docker image
│
├── 📁 docs/
│   ├── 📄 101-Mau A17.doc             # NA17 template reference
│   └── 📄 vps_rebuild_docker_backend.ps1
│
└── 📁 scripts/ (PowerShell deployment)
    ├── 📄 deploy_hotel_pms.ps1        # Main deployment script
    ├── 📄 deploy_and_test_hotel_pms.ps1
    ├── 📄 fix_deployment.ps1
    ├── 📄 fix_nginx_conflict.ps1
    ├── 📄 fix_nginx_routing.ps1
    ├── 📄 fix_ipv4_restart.ps1
    └── 📄 setup_vps_ssl.ps1
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    PROPERTY ||--o{ ROOM : contains
    ROOM ||--o{ BOOKING : has
    BOOKING ||--o{ GUEST : includes
    BOOKING ||--o{ ACCESS_CODE : generates
    ROOM ||--o{ HOUSEKEEPING_LOG : tracks
    ROOM ||--o{ MAINTENANCE_ISSUE : reports
    STAFF ||--o{ HOUSEKEEPING_LOG : performs
    STAFF ||--o{ MAINTENANCE_ISSUE : resolves

    PROPERTY {
        string id PK
        string name
        string address
        string district
        string city
        string channex_property_id UK
        string xnc_registration_code
        datetime created_at
        datetime updated_at
    }

    ROOM {
        string id PK
        string property_id FK
        string room_number
        string room_type
        string ttlock_lock_id
        string ttlock_gateway_id
        string status "available|occupied|cleaning|maintenance"
        datetime created_at
    }

    BOOKING {
        string id PK
        string room_id FK
        string channex_booking_id UK
        string channex_revision_id
        string ota_source "airbnb|booking|agoda|trip|direct"
        string ota_reservation_code
        date check_in
        date check_out
        int nights
        int guests_count
        string guest_name
        string guest_email
        string guest_phone
        string guest_nationality
        string status "pending|confirmed|checked_in|checked_out|cancelled"
        json guest_messages
        datetime created_at
        datetime updated_at
    }

    GUEST {
        string id PK
        string booking_id FK
        string full_name
        string gender "male|female"
        date date_of_birth
        string nationality
        string passport_number
        date passport_issue_date
        date passport_expiry_date
        string passport_issue_country
        string passport_image_path
        string mrz_line1
        string mrz_line2
        bool is_primary
        bool ocr_verified
        bool xnc_exported
        datetime xnc_exported_at
        datetime created_at
    }

    ACCESS_CODE {
        string id PK
        string booking_id FK
        bigint ttlock_passcode_id
        bigint ttlock_backup_passcode_id
        string passcode
        string backup_passcode
        datetime valid_from
        datetime valid_to
        bool sent_to_guest
        datetime sent_at
        string sent_via "channex|email|sms"
        int usage_count
        datetime created_at
    }

    STAFF {
        string id PK
        string email UK
        string password_hash
        string full_name
        string role "admin|owner|housekeeping|maintenance"
        string telegram_chat_id
        bool is_active
        datetime created_at
        datetime last_login
    }

    HOUSEKEEPING_LOG {
        string id PK
        string room_id FK
        string staff_id FK
        string status "dirty|cleaning|clean|inspected"
        string notes
        datetime created_at
    }

    MAINTENANCE_ISSUE {
        string id PK
        string room_id FK
        string reported_by_id FK
        string issue_type "missing_item|damage|repair_needed"
        string severity "low|medium|high|urgent"
        string description
        json images
        bool resolved
        datetime resolved_at
        string resolved_by_id
        string resolution_notes
        datetime notified_at
        datetime created_at
    }
```

---

## 🔄 Workflow Diagrams

### 1. Booking Flow (OTA → Check-out)

```mermaid
sequenceDiagram
    participant OTA as OTA (Airbnb/Booking)
    participant Channex as Channex API
    participant Backend as Hotel PMS Backend
    participant DB as Database
    participant TTLock as TTLock API
    participant Guest as Guest
    participant Staff as Staff

    OTA->>Channex: New Booking Created
    Channex->>Backend: Webhook: booking_created
    Backend->>DB: Save Booking + Guest
    Backend->>TTLock: Create Timed Passcode
    TTLock-->>Backend: Return Passcode
    Backend->>DB: Save AccessCode
    Backend->>Channex: Send Passcode Message
    Channex->>Guest: Deliver via OTA Chat

    Note over Guest,Staff: Guest Arrives

    Guest->>TTLock: Enter Passcode
    TTLock-->>Guest: Door Unlocks
    Staff->>Backend: Update Status: checked_in
    Backend->>DB: Update Room Status: occupied

    Note over Guest,Staff: During Stay

    Guest->>Channex: Send Message (Issue)
    Channex->>Backend: Webhook: message_received
    Backend->>Staff: Telegram Notification
    Staff->>Backend: Resolve Issue

    Note over Guest,Staff: Check-out Day

    Guest->>TTLock: Passcode Expires
    Staff->>Backend: Update Status: checked_out
    Backend->>DB: Update Room: cleaning
    Backend->>TTLock: Delete Passcode
    Backend->>Staff: Housekeeping Task Created
```

### 2. Housekeeping Workflow

```mermaid
flowchart TD
    A[Guest Checks Out] --> B[Room Status: Cleaning]
    B --> C[Task Created Automatically]
    C --> D{Assign Staff?}
    D -->|Manual| E[Admin Assigns Staff]
    D -->|Auto| F[Round-Robin Assignment]
    E --> G[Staff Receives Notification]
    F --> G
    G --> H[Staff Cleans Room]
    H --> I{Issues Found?}
    I -->|Yes| J[Report Maintenance Issue]
    J --> K[Create Maintenance Task]
    K --> L[Notify Maintenance Staff]
    I -->|No| M[Mark Room: Clean]
    L --> N[Maintenance Fixes Issue]
    N --> O[Resolve Issue]
    O --> M
    M --> P[Room Available for Booking]
```

### 3. Passport OCR & XNC Export Flow

```mermaid
flowchart LR
    subgraph Input["Input Methods"]
        A1[📷 Passport Image]
        A2[⌨️ Manual MRZ Entry]
    end

    subgraph OCR["OCR Processing"]
        B1[Tesseract OCR]
        B2[MRZ Parser]
    end

    subgraph Validation["Data Validation"]
        C1[Check Digit Validation]
        C2[Passport Format Check]
        C3[Confidence Score]
    end

    subgraph Storage["Database"]
        D1[(Guest Record)]
    end

    subgraph Export["XNC Export"]
        E1[Select Pending Guests]
        E2[Generate NA17 CSV]
        E3[Upload to XNC Portal]
    end

    A1 --> B1 --> B2
    A2 --> B2
    B2 --> C1
    C1 --> C2
    C2 --> C3
    C3 -->|Valid| D1
    D1 --> E1
    E1 --> E2
    E2 --> E3
```

### 4. Smart Lock Integration Flow

```mermaid
flowchart TD
    subgraph Booking["Booking Created"]
        A[New Booking] --> B[Calculate Check-in/out Times]
    end

    subgraph Passcode["Passcode Generation"]
        B --> C[Get Room's Lock ID]
        C --> D{TTLock Connected?}
        D -->|Yes| E[Call TTLock API]
        D -->|No| F[Mock: Generate Random Code]
        E --> G[Create Timed Passcode]
        F --> G
        G --> H[Create Backup Passcode]
    end

    subgraph Delivery["Delivery"]
        H --> I[Save to Database]
        I --> J[Send via Channex]
        J --> K[Guest Receives Code]
    end

    subgraph Usage["Guest Usage"]
        K --> L[Guest Enters Code]
        L --> M{Valid Time Window?}
        M -->|Yes| N[Door Opens]
        M -->|No| O[Access Denied]
    end

    subgraph Cleanup["Checkout"]
        P[Guest Checks Out] --> Q[Delete Passcode from Lock]
        Q --> R[Invalidate in Database]
    end
```

---

## 🔌 API Endpoints Reference

### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and version |
| GET | `/health` | Service health status |

### CRUD Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/crud/stats` | Dashboard statistics |
| GET | `/api/v1/crud/properties` | List properties |
| GET | `/api/v1/crud/rooms` | List rooms |
| PUT | `/api/v1/crud/rooms/{id}/status` | Update room status |
| GET | `/api/v1/crud/bookings` | List bookings (filterable) |
| GET | `/api/v1/crud/bookings/{id}` | Booking details |
| POST | `/api/v1/crud/bookings` | Create booking |
| PUT | `/api/v1/crud/bookings/{id}/status` | Update booking status |
| POST | `/api/v1/crud/bookings/{id}/generate-passcode` | Generate lock passcode |
| GET | `/api/v1/crud/guests` | List guests |
| GET | `/api/v1/crud/locks` | List smart locks |

### Passport OCR
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/passport/parse-mrz` | Parse MRZ text |
| POST | `/api/v1/passport/parse-image` | Parse passport image |
| POST | `/api/v1/passport/demo` | Demo with sample MRZ |

### Housekeeping
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/housekeeping/tasks` | List cleaning tasks |
| POST | `/api/v1/housekeeping/tasks` | Create task |
| PUT | `/api/v1/housekeeping/tasks/{id}` | Update task |
| GET | `/api/v1/housekeeping/issues` | List maintenance issues |
| POST | `/api/v1/housekeeping/issues` | Report issue |
| PUT | `/api/v1/housekeeping/issues/{id}` | Update/resolve issue |
| GET | `/api/v1/housekeeping/rooms/{id}/status` | Get room cleaning status |
| PUT | `/api/v1/housekeeping/rooms/{id}/status` | Update room status |
| GET | `/api/v1/housekeeping/staff` | List staff |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports/xnc/generate` | Generate XNC NA17 report |
| GET | `/api/v1/reports/xnc/pending` | Pending guests count |

### Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/webhooks/channex` | Channex booking webhook |
| POST | `/api/v1/webhooks/channex/message` | Channex message webhook |

---

## 🛠️ Setup Guide

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (production) or SQLite (development)
- Tesseract OCR (optional, for passport image scanning)

### Quick Start

```bash
# 1. Clone & Setup
cd d:\HOTEL
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env with your values

# 3. Initialize database
cd backend
python init_db.py

# 4. Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# 5. Access application
# Frontend: http://localhost:8003
# API Docs: http://localhost:8002/docs
```

### Docker Deployment

```bash
docker-compose -f docker-compose.production.yml up -d --build
```

---

## 📊 Feature Status Legend

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | Production | Works without additional setup |
| ⚠️ | Partial | Works but requires optional dependency |
| 🧪 | Mock | Demo mode, needs real API credentials |
| 📝 | Stub | Placeholder, needs implementation |
| 🔮 | Planned | On roadmap, not yet started |

---

## 📝 License

Private - All Rights Reserved

---

## 👥 Contact & Support

For issues and feature requests, please create an issue in the repository.
