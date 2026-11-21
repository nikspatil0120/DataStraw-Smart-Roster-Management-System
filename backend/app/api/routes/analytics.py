"""Analytics routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models import (
    Employee, Brand, Process, Roster, RosterEntry, Conflict,
    Assignment, Leave, Pod
)
from app.models.roster import AssignmentStatus
from app.models.leave import LeaveStatus

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics."""
    # Count totals
    total_employees = db.query(Employee).count()
    total_brands = db.query(Brand).count()
    total_processes = db.query(Process).count()
    total_pods = db.query(Pod).count()
    total_rosters = db.query(Roster).count()
    
    # Active employees
    active_employees = db.query(Employee).filter(
        Employee.employment_status == "active"
    ).count()
    
    # Published rosters
    published_rosters = db.query(Roster).filter(
        Roster.status == "published"
    ).count()
    
    # Pending leaves
    pending_leaves = db.query(Leave).filter(
        Leave.status == LeaveStatus.PENDING.value
    ).count()
    
    # Total conflicts in recent rosters
    recent_rosters = db.query(Roster).order_by(Roster.created_at.desc()).limit(10).all()
    recent_roster_ids = [r.id for r in recent_rosters]
    total_conflicts = 0
    critical_conflicts = 0
    
    if recent_roster_ids:
        total_conflicts = db.query(Conflict).filter(
            Conflict.roster_id.in_(recent_roster_ids)
        ).count()
        critical_conflicts = db.query(Conflict).filter(
            Conflict.roster_id.in_(recent_roster_ids),
            Conflict.severity == "critical",
        ).count()
    
    return {
        "success": True,
        "metrics": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "total_brands": total_brands,
            "total_processes": total_processes,
            "total_pods": total_pods,
            "total_rosters": total_rosters,
            "published_rosters": published_rosters,
            "pending_leaves": pending_leaves,
            "total_conflicts": total_conflicts,
            "critical_conflicts": critical_conflicts,
        },
    }


@router.get("/coverage")
async def get_coverage_analytics(
    roster_id: UUID = Query(None),
    db: Session = Depends(get_db),
):
    """Get coverage analytics."""
    query = db.query(RosterEntry)
    
    if roster_id:
        query = query.filter(RosterEntry.roster_id == roster_id)
    
    total = query.count()
    working = query.filter(RosterEntry.assignment_status == AssignmentStatus.WORKING.value).count()
    on_leave = query.filter(RosterEntry.assignment_status == AssignmentStatus.LEAVE.value).count()
    weekly_off = query.filter(RosterEntry.assignment_status == AssignmentStatus.WEEKLY_OFF.value).count()
    unavailable = query.filter(RosterEntry.assignment_status == AssignmentStatus.UNAVAILABLE.value).count()
    
    coverage_percentage = (working / max(total, 1)) * 100
    
    return {
        "success": True,
        "coverage": {
            "total_entries": total,
            "working": working,
            "on_leave": on_leave,
            "weekly_off": weekly_off,
            "unavailable": unavailable,
            "coverage_percentage": round(coverage_percentage, 2),
        },
    }


@router.get("/workload")
async def get_workload_analytics(db: Session = Depends(get_db)):
    """Get employee workload distribution."""
    # Get working assignments per employee in last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    
    workload_data = db.query(
        Employee.id,
        Employee.full_name,
        func.count(RosterEntry.id).label("assignments")
    ).join(
        RosterEntry, RosterEntry.employee_id == Employee.id
    ).filter(
        RosterEntry.roster_date >= thirty_days_ago,
        RosterEntry.assignment_status == AssignmentStatus.WORKING.value,
    ).group_by(
        Employee.id, Employee.full_name
    ).order_by(
        func.count(RosterEntry.id).desc()
    ).all()
    
    # Format for charts
    employees = [
        {
            "name": emp[1],
            "assignments": emp[2],
        }
        for emp in workload_data
    ]
    
    # Calculate average
    avg_workload = sum(e["assignments"] for e in employees) / max(len(employees), 1) if employees else 0
    
    return {
        "success": True,
        "workload": {
            "employees": employees[:20],  # Top 20
            "average_assignments": round(avg_workload, 2),
            "period_days": 30,
        },
    }


@router.get("/conflicts")
async def get_conflict_analytics(db: Session = Depends(get_db)):
    """Get conflict analytics."""
    # Conflicts by severity
    by_severity = db.query(
        Conflict.severity,
        func.count(Conflict.id).label("count")
    ).group_by(Conflict.severity).all()
    
    severity_breakdown = {
        item[0]: item[1] for item in by_severity
    }
    
    # Conflicts by type
    by_type = db.query(
        Conflict.conflict_type,
        func.count(Conflict.id).label("count")
    ).group_by(Conflict.conflict_type).all()
    
    type_breakdown = [
        {"type": item[0], "count": item[1]}
        for item in by_type
    ]
    
    # Resolution rate
    total_conflicts = db.query(Conflict).count()
    resolved_conflicts = db.query(Conflict).filter(Conflict.resolved == 1).count()
    resolution_rate = (resolved_conflicts / max(total_conflicts, 1)) * 100
    
    return {
        "success": True,
        "conflicts": {
            "by_severity": severity_breakdown,
            "by_type": type_breakdown,
            "total_conflicts": total_conflicts,
            "resolved_conflicts": resolved_conflicts,
            "resolution_rate": round(resolution_rate, 2),
        },
    }


@router.get("/assignments")
async def get_assignment_analytics(db: Session = Depends(get_db)):
    """Get assignment analytics."""
    # Brand distribution
    brand_assignments = db.query(
        Brand.brand_name,
        func.count(Assignment.id).label("count")
    ).join(
        Assignment, Assignment.brand_id == Brand.id
    ).group_by(Brand.brand_name).order_by(
        func.count(Assignment.id).desc()
    ).all()
    
    brand_data = [
        {"name": item[0], "assignments": item[1]}
        for item in brand_assignments
    ]
    
    # Process distribution
    process_assignments = db.query(
        Process.process_name,
        func.count(Assignment.id).label("count")
    ).join(
        Assignment, Assignment.process_id == Process.id
    ).group_by(Process.process_name).all()
    
    process_data = [
        {"name": item[0], "assignments": item[1]}
        for item in process_assignments
    ]
    
    # Single vs multi-resource brands
    single_resource = db.query(Brand).filter(
        ~Brand.id.in_(
            db.query(Assignment.brand_id).group_by(
                Assignment.brand_id
            ).having(func.count(Assignment.employee_id.distinct()) > 1)
        )
    ).count()
    
    multi_resource = db.query(Brand).filter(
        Brand.id.in_(
            db.query(Assignment.brand_id).group_by(
                Assignment.brand_id
            ).having(func.count(Assignment.employee_id.distinct()) > 1)
        )
    ).count()
    
    return {
        "success": True,
        "assignments": {
            "brands": brand_data,
            "processes": process_data,
            "single_resource_brands": single_resource,
            "multi_resource_brands": multi_resource,
            "distribution": [
                {"name": "Single-Resource", "value": single_resource},
                {"name": "Multi-Resource", "value": multi_resource},
            ],
        },
    }


@router.get("/pods")
async def get_pod_analytics(db: Session = Depends(get_db)):
    """Get pod-wise analytics."""
    pods = db.query(Pod).all()
    
    pod_data = []
    for pod in pods:
        employee_count = db.query(Employee).filter(Employee.pod_id == pod.id).count()
        
        # Get assignments for this pod
        assignments = db.query(Assignment).join(
            Employee, Employee.id == Assignment.employee_id
        ).filter(Employee.pod_id == pod.id).count()
        
        pod_data.append({
            "pod_name": pod.pod_name,
            "employees": employee_count,
            "assignments": assignments,
            "pod_lead": pod.pod_lead.full_name if pod.pod_lead else "Unassigned",
        })
    
    return {
        "success": True,
        "pods": pod_data,
    }
