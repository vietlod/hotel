"""
Hotel PMS - TTLock Service
Integration with TTLock Cloud API for smart lock control.
"""
import httpx
import hashlib
import time
from typing import Optional, List
from datetime import datetime
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class TTLockService:
    """
    TTLock Cloud API Integration Service.
    
    Handles passcode generation, lock control, and gateway management.
    API Docs: https://euopen.ttlock.com/doc/api/
    """
    
    def __init__(self):
        self.base_url = settings.ttlock_api_endpoint
        self.client_id = settings.ttlock_client_id
        self.client_secret = settings.ttlock_client_secret
        self.username = settings.ttlock_username
        self.password_md5 = settings.ttlock_password_md5
        
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._refresh_token: Optional[str] = None
    
    # ============== Authentication ==============
    
    async def _get_access_token(self) -> str:
        """Get or refresh OAuth2 access token."""
        # Check if current token is still valid
        if self._access_token and self._token_expires_at:
            if time.time() < self._token_expires_at - 300:  # 5 min buffer
                return self._access_token
        
        # Get new token
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                data={
                    "clientId": self.client_id,
                    "clientSecret": self.client_secret,
                    "username": self.username,
                    "password": self.password_md5
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"TTLock auth error: {data.get('errmsg', 'Unknown error')}")
            
            self._access_token = data["access_token"]
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            self._refresh_token = data.get("refresh_token")
            
            return self._access_token
    
    async def _request(
        self, 
        endpoint: str, 
        data: dict,
        method: str = "POST"
    ) -> dict:
        """Make authenticated request to TTLock API."""
        token = await self._get_access_token()
        
        # Add common parameters
        data["clientId"] = self.client_id
        data["accessToken"] = token
        data["date"] = int(time.time() * 1000)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                result = response.json()
                
                if "errcode" in result and result["errcode"] != 0:
                    logger.error(f"TTLock API error: {result}")
                    raise Exception(f"TTLock error {result['errcode']}: {result.get('errmsg', 'Unknown')}")
                
                return result
                
            except httpx.RequestError as e:
                logger.error(f"TTLock request error: {str(e)}")
                raise
    
    # ============== Lock Management ==============
    
    async def get_locks(self, page_no: int = 1, page_size: int = 100) -> List[dict]:
        """Get list of all locks for the account."""
        result = await self._request("/lock/list", {
            "pageNo": page_no,
            "pageSize": page_size
        })
        return result.get("list", [])
    
    async def get_lock_detail(self, lock_id: int) -> dict:
        """Get detailed info about a specific lock."""
        return await self._request("/lock/detail", {"lockId": lock_id})
    
    async def get_lock_state(self, lock_id: int) -> dict:
        """
        Get current lock state (locked/unlocked).
        
        Requires gateway for remote query.
        """
        return await self._request("/lock/queryOpenState", {"lockId": lock_id})
    
    # ============== Passcode Management ==============
    
    async def create_passcode(
        self,
        lock_id: int,
        passcode_name: str,
        passcode_type: int = 2,  # 2 = Timed passcode
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        passcode: Optional[str] = None
    ) -> dict:
        """
        Create a new passcode for a lock.
        
        Passcode Types:
        - 1: Permanent
        - 2: Timed (recommended for bookings)
        - 3: One-time
        - 4: Erase (clears all passcodes)
        - 5: Cyclic - weekly
        - 6: Cyclic - daily
        
        Args:
            lock_id: TTLock lock ID
            passcode_name: Display name (e.g., "Guest: John Doe")
            passcode_type: Type of passcode
            start_date: When passcode becomes valid
            end_date: When passcode expires
            passcode: Specific passcode value (optional, auto-generated if not provided)
        
        Returns:
            Dict with keyboardPwdId and keyboardPwd (the actual code)
        """
        data = {
            "lockId": lock_id,
            "keyboardPwdName": passcode_name,
            "keyboardPwdType": passcode_type
        }
        
        if passcode_type == 2:  # Timed passcode
            if not start_date or not end_date:
                raise ValueError("start_date and end_date required for timed passcode")
            data["startDate"] = int(start_date.timestamp() * 1000)
            data["endDate"] = int(end_date.timestamp() * 1000)
        
        if passcode:
            data["keyboardPwd"] = passcode
            
        result = await self._request("/keyboardPwd/add", data)
        
        return {
            "passcode_id": result.get("keyboardPwdId"),
            "passcode": result.get("keyboardPwd"),
            "valid_from": start_date,
            "valid_to": end_date
        }
    
    async def create_booking_passcode(
        self,
        lock_id: int,
        guest_name: str,
        check_in: datetime,
        check_out: datetime
    ) -> dict:
        """
        Create a timed passcode for a booking.
        
        Convenience method that creates passcode valid from check-in to check-out.
        Also creates a backup passcode.
        
        Args:
            lock_id: TTLock lock ID  
            guest_name: Guest name for reference
            check_in: Check-in datetime
            check_out: Check-out datetime
        
        Returns:
            Dict with primary and backup passcodes
        """
        # Create primary passcode
        primary = await self.create_passcode(
            lock_id=lock_id,
            passcode_name=f"Guest: {guest_name}",
            passcode_type=2,
            start_date=check_in,
            end_date=check_out
        )
        
        # Create backup passcode (valid same period)
        backup = await self.create_passcode(
            lock_id=lock_id,
            passcode_name=f"Backup: {guest_name}",
            passcode_type=2,
            start_date=check_in,
            end_date=check_out
        )
        
        return {
            "passcode": primary["passcode"],
            "passcode_id": primary["passcode_id"],
            "backup_passcode": backup["passcode"],
            "backup_passcode_id": backup["passcode_id"],
            "valid_from": check_in,
            "valid_to": check_out
        }
    
    async def delete_passcode(self, lock_id: int, passcode_id: int) -> bool:
        """Delete a passcode."""
        try:
            await self._request("/keyboardPwd/delete", {
                "lockId": lock_id,
                "keyboardPwdId": passcode_id
            })
            return True
        except Exception as e:
            logger.error(f"Failed to delete passcode {passcode_id}: {e}")
            return False
    
    async def get_passcodes(self, lock_id: int) -> List[dict]:
        """Get all passcodes for a lock."""
        result = await self._request("/lock/listKeyboardPwd", {
            "lockId": lock_id,
            "pageNo": 1,
            "pageSize": 100
        })
        return result.get("list", [])
    
    # ============== Lock Control ==============
    
    async def unlock(self, lock_id: int) -> bool:
        """
        Remotely unlock a lock.
        
        Requires gateway connection.
        """
        try:
            await self._request("/lock/unlock", {"lockId": lock_id})
            return True
        except Exception as e:
            logger.error(f"Failed to unlock {lock_id}: {e}")
            return False
    
    async def lock(self, lock_id: int) -> bool:
        """
        Remotely lock a lock.
        
        Requires gateway connection.
        """
        try:
            await self._request("/lock/lock", {"lockId": lock_id})
            return True
        except Exception as e:
            logger.error(f"Failed to lock {lock_id}: {e}")
            return False
    
    # ============== Gateway Management ==============
    
    async def get_gateways(self) -> List[dict]:
        """Get list of gateways."""
        result = await self._request("/gateway/list", {
            "pageNo": 1,
            "pageSize": 100
        })
        return result.get("list", [])
    
    async def get_gateway_locks(self, gateway_id: int) -> List[dict]:
        """Get locks connected to a gateway."""
        result = await self._request("/gateway/listLock", {
            "gatewayId": gateway_id
        })
        return result.get("list", [])
    
    # ============== Health Check ==============
    
    async def health_check(self) -> str:
        """Check TTLock API connectivity."""
        try:
            await self._get_access_token()
            return "connected"
        except Exception as e:
            logger.warning(f"TTLock health check failed: {e}")
            return "disconnected"


# Singleton instance
ttlock_service = TTLockService()


# ============== Utility Functions ==============

def md5_password(password: str) -> str:
    """
    Convert password to MD5 hash (required by TTLock API).
    
    Usage:
        md5_hash = md5_password("your_password")
        # Store this in TTLOCK_PASSWORD_MD5 env variable
    """
    return hashlib.md5(password.encode('utf-8')).hexdigest()
