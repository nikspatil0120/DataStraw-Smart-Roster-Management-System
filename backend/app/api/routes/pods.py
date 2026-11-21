"""Pod routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Pod
from app.schemas.pod import PodCreate, PodUpdate, PodResponse
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/pods", tags=["pods"])


@router.get("", response_model=dict)
async def list_pods(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all pods with pagination."""
    total = db.query(Pod).count()
    pods = db.query(Pod).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[PodResponse.model_validate(p) for p in pods],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", response_model=PodResponse, status_code=status.HTTP_201_CREATED)
async def create_pod(
    request: PodCreate,
    db: Session = Depends(get_db),
):
    """Create a new pod."""
    # Check for duplicate pod name
    existing = db.query(Pod).filter(Pod.pod_name == request.pod_name).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pod name already exists",
        )
    
    pod = Pod(**request.model_dump())
    db.add(pod)
    db.commit()
    db.refresh(pod)
    
    return PodResponse.model_validate(pod)


@router.get("/{pod_id}", response_model=PodResponse)
async def get_pod(
    pod_id: UUID,
    db: Session = Depends(get_db),
):
    """Get pod by ID."""
    pod = db.query(Pod).filter(Pod.id == pod_id).first()
    
    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pod not found",
        )
    
    return PodResponse.model_validate(pod)


@router.put("/{pod_id}", response_model=PodResponse)
async def update_pod(
    pod_id: UUID,
    request: PodUpdate,
    db: Session = Depends(get_db),
):
    """Update pod."""
    pod = db.query(Pod).filter(Pod.id == pod_id).first()
    
    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pod not found",
        )
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(pod, field, value)
    
    db.commit()
    db.refresh(pod)
    
    return PodResponse.model_validate(pod)


@router.delete("/{pod_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pod(
    pod_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete pod."""
    pod = db.query(Pod).filter(Pod.id == pod_id).first()
    
    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pod not found",
        )
    
    db.delete(pod)
    db.commit()
