"""Process routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Process
from app.schemas.process import ProcessCreate, ProcessUpdate, ProcessResponse
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/processes", tags=["processes"])


@router.get("", response_model=dict)
async def list_processes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all processes with pagination."""
    total = db.query(Process).count()
    processes = db.query(Process).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[ProcessResponse.model_validate(p) for p in processes],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_process(
    request: ProcessCreate,
    db: Session = Depends(get_db),
):
    """Create a new process."""
    # Check for duplicate process code
    existing = db.query(Process).filter(
        Process.process_code == request.process_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process code already exists",
        )
    
    process = Process(**request.model_dump())
    db.add(process)
    db.commit()
    db.refresh(process)
    
    return ProcessResponse.model_validate(process)


@router.get("/{process_id}", response_model=ProcessResponse)
async def get_process(
    process_id: UUID,
    db: Session = Depends(get_db),
):
    """Get process by ID."""
    process = db.query(Process).filter(Process.id == process_id).first()
    
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found",
        )
    
    return ProcessResponse.model_validate(process)


@router.put("/{process_id}", response_model=ProcessResponse)
async def update_process(
    process_id: UUID,
    request: ProcessUpdate,
    db: Session = Depends(get_db),
):
    """Update process."""
    process = db.query(Process).filter(Process.id == process_id).first()
    
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found",
        )
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(process, field, value)
    
    db.commit()
    db.refresh(process)
    
    return ProcessResponse.model_validate(process)


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process(
    process_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete process."""
    process = db.query(Process).filter(Process.id == process_id).first()
    
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found",
        )
    
    db.delete(process)
    db.commit()
