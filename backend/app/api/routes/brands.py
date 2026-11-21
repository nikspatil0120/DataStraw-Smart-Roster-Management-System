"""Brand routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Brand
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/brands", tags=["brands"])


@router.get("", response_model=dict)
async def list_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all brands with pagination."""
    total = db.query(Brand).count()
    brands = db.query(Brand).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[BrandResponse.model_validate(b) for b in brands],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    request: BrandCreate,
    db: Session = Depends(get_db),
):
    """Create a new brand."""
    # Check for duplicate brand code
    existing = db.query(Brand).filter(
        Brand.brand_code == request.brand_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand code already exists",
        )
    
    brand = Brand(**request.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    
    return BrandResponse.model_validate(brand)


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: UUID,
    db: Session = Depends(get_db),
):
    """Get brand by ID."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    
    return BrandResponse.model_validate(brand)


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: UUID,
    request: BrandUpdate,
    db: Session = Depends(get_db),
):
    """Update brand."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)
    
    db.commit()
    db.refresh(brand)
    
    return BrandResponse.model_validate(brand)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete brand."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    
    db.delete(brand)
    db.commit()
