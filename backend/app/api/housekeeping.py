"""
Housekeeping & Maintenance API Routes
CRUD operations for housekeeping tasks and maintenance issues.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Room, Staff, HousekeepingLog, MaintenanceIssue

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/housekeeping", tags=["Housekeeping"])


# ============================================
# Pydantic Schemas
# ============================================

class HousekeepingTaskCreate(BaseModel):
    """Create a new housekeeping task."""
    room_id: str
    task_type: str  # checkout_clean, turndown, deep_clean, refresh
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    priority: str = "normal"  # low, normal, high
    notes: Optional[str] = None


class HousekeepingTaskResponse(BaseModel):
    """Housekeeping task response."""
    id: str
    room_id: str
    room_number: Optional[str] = None
    task_type: str
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    priority: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaintenanceIssueCreate(BaseModel):
    """Create a maintenance issue."""
    room_id: str
    issue_type: str = "repair_needed"
    severity: str = "medium"  # low, medium, high, urgent
    description: str
    reporter: Optional[str] = None


class MaintenanceIssueResponse(BaseModel):
    """Maintenance issue response."""
    id: str
    room_id: str
    room_number: Optional[str] = None
    issue_type: str
    severity: str
    description: str
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True


class RoomCleaningStatus(BaseModel):
    """Room cleaning status for grid display."""
    id: str
    room_number: str
    room_name: Optional[str] = None
    status: str
    has_pending_task: bool = False
    has_open_issue: bool = False


class StaffResponse(BaseModel):
    """Staff member response."""
    id: str
    name: str
    role: str
    available: bool = True


# ============================================
# Housekeeping Tasks API
# ============================================

@router.get("/tasks", response_model=List[HousekeepingTaskResponse])
async def get_housekeeping_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    room_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all housekeeping tasks."""
    query = db.query(HousekeepingLog)
    
    if status:
        query = query.filter(HousekeepingLog.status == status)
    if room_id:
        query = query.filter(HousekeepingLog.room_id == room_id)
    
    tasks = query.order_by(HousekeepingLog.created_at.desc()).all()
    
    result = []
    for task in tasks:
        room = db.query(Room).filter(Room.id == task.room_id).first()
        staff = None
        if task.staff_id:
            staff = db.query(Staff).filter(Staff.id == task.staff_id).first()
        
        result.append(HousekeepingTaskResponse(
            id=task.id,
            room_id=task.room_id,
            room_number=room.room_number if room else None,
            task_type=task.status,  # Using status as task_type for now
            assignee_id=task.staff_id,
            assignee_name=staff.full_name if staff else None,
            priority="normal",
            status=task.status,
            notes=task.notes,
            created_at=task.created_at
        ))
    
    return result


@router.post("/tasks", response_model=HousekeepingTaskResponse)
async def create_housekeeping_task(
    task: HousekeepingTaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new housekeeping task."""
    # Verify room exists
    room = db.query(Room).filter(Room.id == task.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Create task
    new_task = HousekeepingLog(
        room_id=task.room_id,
        staff_id=task.assignee_id,
        status=task.task_type,  # pending, cleaning, etc.
        notes=f"Priority: {task.priority}. {task.notes or ''}"
    )
    
    db.add(new_task)
    
    # Update room status to cleaning
    room.status = "cleaning"
    
    db.commit()
    db.refresh(new_task)
    
    logger.info(f"Created housekeeping task {new_task.id} for room {room.room_number}")
    
    return HousekeepingTaskResponse(
        id=new_task.id,
        room_id=new_task.room_id,
        room_number=room.room_number,
        task_type=task.task_type,
        assignee_id=task.assignee_id,
        assignee_name=task.assignee_name,
        priority=task.priority,
        status="pending",
        notes=task.notes,
        created_at=new_task.created_at
    )


@router.put("/tasks/{task_id}/complete")
async def complete_housekeeping_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Mark a housekeeping task as complete."""
    task = db.query(HousekeepingLog).filter(HousekeepingLog.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "completed"
    
    # Update room status to available
    room = db.query(Room).filter(Room.id == task.room_id).first()
    if room:
        room.status = "available"
    
    db.commit()
    
    logger.info(f"Completed housekeeping task {task_id}")
    
    return {"success": True, "message": "Task marked as complete"}


@router.delete("/tasks/{task_id}")
async def delete_housekeeping_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Delete a housekeeping task."""
    task = db.query(HousekeepingLog).filter(HousekeepingLog.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"success": True, "message": "Task deleted"}


# ============================================
# Maintenance Issues API
# ============================================

@router.get("/issues", response_model=List[MaintenanceIssueResponse])
async def get_maintenance_issues(
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    severity: Optional[str] = None,
    room_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all maintenance issues."""
    query = db.query(MaintenanceIssue)
    
    if resolved is not None:
        query = query.filter(MaintenanceIssue.resolved == resolved)
    if severity:
        query = query.filter(MaintenanceIssue.severity == severity)
    if room_id:
        query = query.filter(MaintenanceIssue.room_id == room_id)
    
    issues = query.order_by(MaintenanceIssue.created_at.desc()).all()
    
    result = []
    for issue in issues:
        room = db.query(Room).filter(Room.id == issue.room_id).first()
        result.append(MaintenanceIssueResponse(
            id=issue.id,
            room_id=issue.room_id,
            room_number=room.room_number if room else None,
            issue_type=issue.issue_type,
            severity=issue.severity,
            description=issue.description,
            resolved=issue.resolved,
            created_at=issue.created_at,
            resolved_at=issue.resolved_at,
            resolution_notes=issue.resolution_notes
        ))
    
    return result


@router.post("/issues", response_model=MaintenanceIssueResponse)
async def create_maintenance_issue(
    issue: MaintenanceIssueCreate,
    db: Session = Depends(get_db)
):
    """Report a new maintenance issue."""
    # Verify room exists
    room = db.query(Room).filter(Room.id == issue.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Create issue
    new_issue = MaintenanceIssue(
        room_id=issue.room_id,
        issue_type=issue.issue_type,
        severity=issue.severity,
        description=issue.description
    )
    
    db.add(new_issue)
    
    # If high severity, update room status
    if issue.severity in ["high", "urgent"]:
        room.status = "maintenance"
    
    db.commit()
    db.refresh(new_issue)
    
    logger.info(f"Created maintenance issue {new_issue.id} for room {room.room_number}")
    
    return MaintenanceIssueResponse(
        id=new_issue.id,
        room_id=new_issue.room_id,
        room_number=room.room_number,
        issue_type=new_issue.issue_type,
        severity=new_issue.severity,
        description=new_issue.description,
        resolved=new_issue.resolved,
        created_at=new_issue.created_at
    )


@router.put("/issues/{issue_id}/resolve")
async def resolve_maintenance_issue(
    issue_id: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Resolve a maintenance issue."""
    issue = db.query(MaintenanceIssue).filter(MaintenanceIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue.resolved = True
    issue.resolved_at = datetime.utcnow()
    issue.resolution_notes = resolution_notes
    
    # Update room status if it was in maintenance
    room = db.query(Room).filter(Room.id == issue.room_id).first()
    if room and room.status == "maintenance":
        # Check for other open issues
        other_issues = db.query(MaintenanceIssue).filter(
            MaintenanceIssue.room_id == issue.room_id,
            MaintenanceIssue.resolved == False,
            MaintenanceIssue.id != issue_id
        ).count()
        
        if other_issues == 0:
            room.status = "available"
    
    db.commit()
    
    logger.info(f"Resolved maintenance issue {issue_id}")
    
    return {"success": True, "message": "Issue resolved"}


@router.delete("/issues/{issue_id}")
async def delete_maintenance_issue(
    issue_id: str,
    db: Session = Depends(get_db)
):
    """Delete a maintenance issue."""
    issue = db.query(MaintenanceIssue).filter(MaintenanceIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db.delete(issue)
    db.commit()
    
    return {"success": True, "message": "Issue deleted"}


# ============================================
# Room Status API
# ============================================

@router.get("/rooms", response_model=List[RoomCleaningStatus])
async def get_rooms_cleaning_status(
    db: Session = Depends(get_db)
):
    """Get all rooms with their cleaning status."""
    rooms = db.query(Room).all()
    
    result = []
    for room in rooms:
        # Check for pending tasks
        pending_tasks = db.query(HousekeepingLog).filter(
            HousekeepingLog.room_id == room.id,
            HousekeepingLog.status != "completed"
        ).count()
        
        # Check for open issues
        open_issues = db.query(MaintenanceIssue).filter(
            MaintenanceIssue.room_id == room.id,
            MaintenanceIssue.resolved == False
        ).count()
        
        result.append(RoomCleaningStatus(
            id=room.id,
            room_number=room.room_number,
            room_name=room.room_type,
            status=room.status,
            has_pending_task=pending_tasks > 0,
            has_open_issue=open_issues > 0
        ))
    
    return result


@router.put("/rooms/{room_id}/status")
async def update_room_cleaning_status(
    room_id: str,
    status: str = Query(..., description="New status: available, cleaning, maintenance"),
    db: Session = Depends(get_db)
):
    """Update room cleaning status."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room.status = status
    db.commit()
    
    logger.info(f"Updated room {room.room_number} status to {status}")
    
    return {"success": True, "room_number": room.room_number, "status": status}


# ============================================
# Staff API
# ============================================

@router.get("/staff", response_model=List[StaffResponse])
async def get_housekeeping_staff(
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)
):
    """Get staff members for task assignment."""
    query = db.query(Staff).filter(Staff.is_active == True)
    
    if role:
        query = query.filter(Staff.role == role)
    else:
        query = query.filter(Staff.role.in_(["housekeeping", "maintenance"]))
    
    staff = query.all()
    
    return [
        StaffResponse(
            id=s.id,
            name=s.full_name or s.email,
            role=s.role,
            available=s.is_active
        )
        for s in staff
    ]
