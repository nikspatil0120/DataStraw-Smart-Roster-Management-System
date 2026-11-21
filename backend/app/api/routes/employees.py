"""Employee routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)
from app.utils.response import success_response, paginated_response

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=dict)
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all employees with pagination."""
    total = db.query(Employee).count()
    employees = db.query(Employee).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[EmployeeResponse.model_validate(e) for e in employees],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    request: EmployeeCreate,
    db: Session = Depends(get_db),
):
    """Create a new employee."""
    # Check for duplicate employee code
    existing = db.query(Employee).filter(
        Employee.employee_code == request.employee_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee code already exists",
        )
    
    employee = Employee(**request.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    return EmployeeResponse.model_validate(employee)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
):
    """Get employee by ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    
    return EmployeeResponse.model_validate(employee)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    request: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    """Update employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    return EmployeeResponse.model_validate(employee)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    
    db.delete(employee)
    db.commit()
