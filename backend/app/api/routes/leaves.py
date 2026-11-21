"""Leave routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Leave
from app.schemas.leave import LeaveCreate, LeaveUpdate, LeaveResponse
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/leaves", tags=["leaves"])


@router.get("", response_model=dict)
async def list_leaves(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    employee_id: UUID = Query(None),
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """List leaves with optional filters."""
    query = db.query(Leave)
    
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)
    if status_filter:
        query = query.filter(Leave.status == status_filter)
    
    total = query.count()
    leaves = query.offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[LeaveResponse.model_validate(l) for l in leaves],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
async def create_leave(
    request: LeaveCreate,
    db: Session = Depends(get_db),
):
    """Create a new leave request."""
    leave = Leave(**request.model_dump(), status="pending")
    db.add(leave)
    db.commit()
    db.refresh(leave)
    
    return LeaveResponse.model_validate(leave)


@router.get("/{leave_id}", response_model=LeaveResponse)
async def get_leave(
    leave_id: UUID,
    db: Session = Depends(get_db),
):
    """Get leave by ID."""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )
    
    return LeaveResponse.model_validate(leave)


@router.put("/{leave_id}", response_model=LeaveResponse)
async def update_leave(
    leave_id: UUID,
    request: LeaveUpdate,
    db: Session = Depends(get_db),
):
    """Update leave."""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(leave, field, value)
    
    db.commit()
    db.refresh(leave)
    
    return LeaveResponse.model_validate(leave)


@router.post("/{leave_id}/approve", response_model=LeaveResponse)
async def approve_leave(
    leave_id: UUID,
    db: Session = Depends(get_db),
):
    """Approve a leave request."""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )
    
    leave.status = "approved"
    db.commit()
    db.refresh(leave)
    
    return LeaveResponse.model_validate(leave)


@router.post("/{leave_id}/reject", response_model=LeaveResponse)
async def reject_leave(
    leave_id: UUID,
    db: Session = Depends(get_db),
):
    """Reject a leave request."""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )
    
    leave.status = "rejected"
    db.commit()
    db.refresh(leave)
    
    return LeaveResponse.model_validate(leave)


@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_leave(
    leave_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete leave."""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )
    
    db.delete(leave)
    db.commit()
