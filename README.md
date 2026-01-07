# Hotel PMS - Property Management System

Hệ thống quản lý khách sạn/căn hộ dịch vụ tích hợp Channel Manager, Smart Lock và báo cáo XNC.

## 🚀 Features (MVP)

- ✅ **Booking Sync**: Đồng bộ booking từ Airbnb/Booking/Agoda/Trip qua Channex
- ✅ **Auto Passcode**: Tự động tạo và gửi mã cửa cho khách qua TTLock
- ✅ **XNC Report**: Xuất báo cáo lưu trú người nước ngoài theo format chuẩn

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── channex_service.py
│   │   ├── ttlock_service.py
│   │   ├── xnc_service.py
│   │   └── telegram_service.py
│   ├── api/                 # API routes
│   └── tasks/               # Celery async tasks
├── tests/
├── alembic/                 # Database migrations
└── requirements.txt
```

## 🛠️ Setup

### 1. Clone & Install

```bash
cd d:\HOTEL
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Environment Variables

```bash
copy .env.example .env
# Edit .env with your actual credentials
```

### 3. Database Setup

```bash
# Start PostgreSQL (or use SQLite for development)
cd backend
alembic upgrade head
```

### 4. Run Development Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run Celery Worker (for async tasks)

```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

## 📖 API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Required Accounts

| Service | URL | Purpose |
|---------|-----|---------|
| Channex | https://staging.channex.io | Channel Manager |
| TTLock | https://euopen.ttlock.com | Smart Lock API |
| Telegram | @BotFather | Notifications |
| XNC Portal | https://hochiminh.xuatnhapcanh.gov.vn | Immigration Report |

## 📝 License

Private - All Rights Reserved
