---
description: How to enable real API integrations (Channex, TTLock, Telegram)
---

# Enable Production Integrations

This workflow guides you through converting mock services to real API integrations.

---

## 1. Channex Integration (Channel Manager)

### Prerequisites
- Channex account (staging or production)
- Property configured in Channex dashboard
- API key from Settings → API

### Steps

1. **Get API Credentials**
   - Login to https://staging.channex.io (or production)
   - Go to Settings → API
   - Copy your API Key

2. **Configure Environment**
   ```bash
   # Update .env file
   CHANNEX_API_KEY=your_real_api_key
   CHANNEX_PROPERTY_ID=your_property_uuid
   CHANNEX_WEBHOOK_SECRET=your_webhook_secret
   ```

3. **Configure Webhook in Channex**
   - Go to Settings → Webhooks
   - Add new webhook:
     - URL: `https://hotel.khoviet.com/api/v1/webhooks/channex`
     - Events: `booking_created`, `booking_modified`, `booking_cancelled`
   - Save and note the secret for CHANNEX_WEBHOOK_SECRET

4. **Restart Backend**
   ```bash
   # Local
   # Stop uvicorn (Ctrl+C) and restart
   
   # VPS
   docker-compose -f docker-compose.production.yml restart backend
   ```

5. **Test Integration**
   ```bash
   # Check health shows "connected"
   curl https://hotel.khoviet.com/health
   # channex should show "connected" not "mock"
   
   # Test booking sync
   curl https://hotel.khoviet.com/api/v1/bookings/sync
   ```

---

## 2. TTLock Integration (Smart Lock)

### Prerequisites
- TTLock smart locks installed
- TTLock G2 Gateway configured and online
- TTLock Open Platform developer account

### Steps

1. **Register Developer Account**
   - Go to https://euopen.ttlock.com
   - Register for Open Platform access
   - Create an application

2. **Get OAuth Credentials**
   - In TTLock developer portal, go to Application → Settings
   - Note: Client ID, Client Secret
   - Your TTLock account email and password

3. **Generate Password MD5**
   ```python
   # Run in Python console
   from app.services.ttlock_service import md5_password
   print(md5_password("your_ttlock_password"))
   ```

4. **Configure Environment**
   ```bash
   TTLOCK_CLIENT_ID=your_client_id
   TTLOCK_CLIENT_SECRET=your_client_secret
   TTLOCK_USERNAME=your_email@example.com
   TTLOCK_PASSWORD_MD5=md5_hash_from_step_3
   ```

5. **Map Locks to Rooms**
   - Get lock IDs from TTLock API or app
   - Update room records in database:
   ```sql
   UPDATE rooms SET ttlock_lock_id = '10001' WHERE room_number = '101';
   ```

6. **Restart and Test**
   ```bash
   # Restart backend
   docker-compose -f docker-compose.production.yml restart backend
   
   # Check health
   curl https://hotel.khoviet.com/health
   # ttlock should show "connected"
   
   # Test passcode generation
   curl -X POST https://hotel.khoviet.com/api/v1/crud/bookings/[id]/generate-passcode
   ```

---

## 3. Telegram Bot Integration

### Prerequisites
- Telegram account
- Group/channel for notifications

### Steps

1. **Create Bot**
   - Open Telegram, find @BotFather
   - Send: `/newbot`
   - Follow prompts to name your bot
   - Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`)

2. **Create Notification Group**
   - Create a new Telegram group
   - Add your bot to the group
   - Make bot admin (for sending messages)

3. **Get Chat ID**
   - Add @getidsbot to your group temporarily
   - It will show the group chat ID (negative number like `-12345678`)
   - Remove @getidsbot after getting ID

4. **Configure Environment**
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
   TELEGRAM_CHAT_ID=-12345678
   ```

5. **Implement Real Service**
   
   Replace the stub in `telegram_service.py`:
   ```python
   from telegram import Bot
   from telegram.error import TelegramError
   
   class TelegramService:
       def __init__(self):
           self.bot = Bot(token=settings.telegram_bot_token)
           self.chat_id = settings.telegram_chat_id
           
       async def send_message(self, text: str):
           try:
               await self.bot.send_message(
                   chat_id=self.chat_id,
                   text=text,
                   parse_mode='HTML'
               )
               return True
           except TelegramError as e:
               logger.error(f"Telegram error: {e}")
               return False
   ```

6. **Install Dependency**
   ```bash
   pip install python-telegram-bot
   # Add to requirements.txt
   ```

7. **Test**
   ```bash
   # Restart backend
   # Create a test booking to trigger notification
   ```

---

## Verification Checklist

After enabling each integration:

```
□ .env file updated with real credentials
□ Backend restarted
□ /health shows "connected" for the service
□ Test API call works
□ No errors in logs
□ Credentials NOT committed to git (check .gitignore)
```

---

## Troubleshooting

### Channex: "unauthorized" error
- Verify API key is correct
- Check API key hasn't expired
- Ensure you're using staging key for staging URL

### TTLock: "client not found" error
- Verify Client ID and Secret
- Check application is approved in TTLock Open Platform
- Ensure using correct API endpoint (EU vs US)

### Telegram: "chat not found" error
- Verify chat ID is correct (including negative sign for groups)
- Ensure bot is added to the group
- Check bot has permission to send messages

---

*Workflow for enabling production integrations*
