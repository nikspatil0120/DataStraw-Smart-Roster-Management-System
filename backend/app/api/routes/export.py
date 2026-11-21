"""Export routes (CSV, Excel)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from io import StringIO, BytesIO
import csv
from datetime import datetime

router = APIRouter(prefix="/api/export", tags=["export"])

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from app.database import get_db
from app.models import Roster, RosterEntry, Employee, Brand, Process
from fastapi.responses import StreamingResponse


@router.get("/rosters/{roster_id}/csv")
async def export_roster_csv(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Export roster to CSV."""
    try:
        roster = db.query(Roster).filter(Roster.id == roster_id).first()
        if not roster:
            raise HTTPException(status_code=404, detail="Roster not found")
        
        entries = db.query(RosterEntry).filter(RosterEntry.roster_id == roster_id).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Date",
            "Employee",
            "Employee Code",
            "Pod",
            "Brand",
            "Process",
            "Status",
            "Shift Start",
            "Shift End",
            "Notes",
        ])
        
        # Data rows
        for entry in entries:
            employee = db.query(Employee).filter(Employee.id == entry.employee_id).first()
            brand = db.query(Brand).filter(Brand.id == entry.brand_id).first()
            process = db.query(Process).filter(Process.id == entry.process_id).first() if entry.process_id else None
            
            writer.writerow([
                entry.roster_date.isoformat(),
                employee.full_name if employee else "",
                employee.employee_code if employee else "",
                employee.pod.pod_name if employee and employee.pod else "",
                brand.brand_name if brand else "",
                process.process_name if process else "N/A",
                entry.assignment_status,
                entry.shift_start.isoformat() if entry.shift_start else "",
                entry.shift_end.isoformat() if entry.shift_end else "",
                entry.notes or "",
            ])
        
        # Return as downloadable file
        output.seek(0)
        filename = f"roster_{roster.month}_{roster.year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/rosters/{roster_id}/excel")
async def export_roster_excel(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Export roster to Excel."""
    if not EXCEL_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Excel export not available. Install openpyxl.",
        )
    
    try:
        roster = db.query(Roster).filter(Roster.id == roster_id).first()
        if not roster:
            raise HTTPException(status_code=404, detail="Roster not found")
        
        entries = db.query(RosterEntry).filter(RosterEntry.roster_id == roster_id).all()
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Roster"
        
        # Styling
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )
        
        # Headers
        headers = [
            "Date",
            "Employee",
            "Employee Code",
            "Pod",
            "Brand",
            "Process",
            "Status",
            "Shift Start",
            "Shift End",
            "Notes",
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
        
        # Data rows
        for row, entry in enumerate(entries, 2):
            employee = db.query(Employee).filter(Employee.id == entry.employee_id).first()
            brand = db.query(Brand).filter(Brand.id == entry.brand_id).first()
            process = db.query(Process).filter(Process.id == entry.process_id).first() if entry.process_id else None
            
            row_data = [
                entry.roster_date.isoformat(),
                employee.full_name if employee else "",
                employee.employee_code if employee else "",
                employee.pod.pod_name if employee and employee.pod else "",
                brand.brand_name if brand else "",
                process.process_name if process else "N/A",
                entry.assignment_status,
                entry.shift_start.isoformat() if entry.shift_start else "",
                entry.shift_end.isoformat() if entry.shift_end else "",
                entry.notes or "",
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row, column=col)
                cell.value = value
                cell.border = border
                cell.alignment = Alignment(horizontal="left", vertical="center")
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"roster_{roster.month}_{roster.year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
