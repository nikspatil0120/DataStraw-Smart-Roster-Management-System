"""Assignment routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


@router.get("", response_model=dict)
async def list_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    employee_id: UUID = Query(None),
    brand_id: UUID = Query(None),
    db: Session = Depends(get_db),
):
    """List assignments with optional filters."""
    query = db.query(Assignment)
    
    if employee_id:
        query = query.filter(Assignment.employee_id == employee_id)
    if brand_id:
        query = query.filter(Assignment.brand_id == brand_id)
    
    total = query.count()
    assignments = query.offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[AssignmentResponse.model_validate(a) for a in assignments],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    request: AssignmentCreate,
    db: Session = Depends(get_db),
):
    """Create a new assignment."""
    assignment = Assignment(**request.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return AssignmentResponse.model_validate(assignment)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
):
    """Get assignment by ID."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    return AssignmentResponse.model_validate(assignment)


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: UUID,
    request: AssignmentUpdate,
    db: Session = Depends(get_db),
):
    """Update assignment."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    
    return AssignmentResponse.model_validate(assignment)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete assignment."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    db.delete(assignment)
    db.commit()
