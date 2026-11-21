"""Seed database with realistic sample data."""
import os
import sys
from datetime import date, timedelta
from uuid import uuid4
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import (
    Pod,
    Employee,
    Brand,
    Process,
    Assignment,
    SchedulingRule,
    Holiday,
    Leave,
    Availability,
    User,
)
from app.models.employee import EmployeeRole, EmploymentStatus
from app.models.leave import LeaveType, LeaveStatus
from app.utils.security import hash_password

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed_pods():
    """Create 5 operational pods."""
    pod_names = [
        "Pod Alpha",
        "Pod Beta",
        "Pod Gamma",
        "Pod Delta",
        "Pod Epsilon",
    ]

    pods = []
    for name in pod_names:
        pod = Pod(
            pod_name=name,
            description=f"Operational pod: {name}",
            status="active",
        )
        db.add(pod)
        pods.append(pod)

    db.flush()
    return pods


def seed_employees(pods):
    """Create 30 employees distributed across 5 pods."""
    employee_data = [
        # Pod Alpha (6 employees)
        ("EMP001", "Rajesh Kumar", "rajesh@datastraw.local", "SUNDAY"),
        ("EMP002", "Priya Singh", "priya@datastraw.local", "MONDAY"),
        ("EMP003", "Amit Patel", "amit@datastraw.local", "SUNDAY"),
        ("EMP004", "Neha Sharma", "neha@datastraw.local", "TUESDAY"),
        ("EMP005", "Vikram Reddy", "vikram@datastraw.local", "SUNDAY"),
        ("EMP006", "Anjali Gupta", "anjali@datastraw.local", "WEDNESDAY"),
        # Pod Beta (6 employees)
        ("EMP007", "Ravi Iyer", "ravi@datastraw.local", "SUNDAY"),
        ("EMP008", "Divya Nair", "divya@datastraw.local", "MONDAY"),
        ("EMP009", "Sanjay Das", "sanjay@datastraw.local", "SUNDAY"),
        ("EMP010", "Meera Bhat", "meera@datastraw.local", "THURSDAY"),
        ("EMP011", "Arjun Rao", "arjun@datastraw.local", "SUNDAY"),
        ("EMP012", "Shreya Kulkarni", "shreya@datastraw.local", "FRIDAY"),
        # Pod Gamma (6 employees)
        ("EMP013", "Kunal Verma", "kunal@datastraw.local", "SUNDAY"),
        ("EMP014", "Anika Desai", "anika@datastraw.local", "SATURDAY"),
        ("EMP015", "Nikhil Joshi", "nikhil@datastraw.local", "SUNDAY"),
        ("EMP016", "Pooja Mishra", "pooja@datastraw.local", "MONDAY"),
        ("EMP017", "Rohit Singh", "rohit@datastraw.local", "SUNDAY"),
        ("EMP018", "Sneha Roy", "sneha@datastraw.local", "TUESDAY"),
        # Pod Delta (6 employees)
        ("EMP019", "Abhishek Tiwari", "abhishek@datastraw.local", "SUNDAY"),
        ("EMP020", "Isha Malhotra", "isha@datastraw.local", "WEDNESDAY"),
        ("EMP021", "Varun Negi", "varun@datastraw.local", "SUNDAY"),
        ("EMP022", "Kavya Rao", "kavya@datastraw.local", "THURSDAY"),
        ("EMP023", "Aditya Sharma", "aditya@datastraw.local", "SUNDAY"),
        ("EMP024", "Tanvi Chopra", "tanvi@datastraw.local", "SATURDAY"),
        # Pod Epsilon (6 employees)
        ("EMP025", "Harsh Patel", "harsh@datastraw.local", "SUNDAY"),
        ("EMP026", "Ritika Singh", "ritika@datastraw.local", "FRIDAY"),
        ("EMP027", "Manish Kumar", "manish@datastraw.local", "SUNDAY"),
        ("EMP028", "Sonali Nair", "sonali@datastraw.local", "MONDAY"),
        ("EMP029", "Deepak Verma", "deepak@datastraw.local", "SUNDAY"),
        ("EMP030", "Yasmine Khan", "yasmine@datastraw.local", "WEDNESDAY"),
    ]

    employees = []
    for i, (code, name, email, weekly_off) in enumerate(employee_data):
        pod = pods[i // 6]  # 6 employees per pod
        is_pod_lead = (i % 6) == 0  # First employee in each pod is pod lead

        employee = Employee(
            employee_code=code,
            full_name=name,
            email=email,
            phone=f"+91-{random.randint(9000000000, 9999999999)}",
            pod_id=pod.id,
            role=EmployeeRole.POD_LEAD.value if is_pod_lead else EmployeeRole.EXECUTIVE.value,
            employment_status=EmploymentStatus.ACTIVE.value,
            joining_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
            max_assignments_per_day=2,
            preferred_weekly_off=weekly_off,
        )
        db.add(employee)
        employees.append(employee)

        # Update pod lead
        if is_pod_lead:
            pod.pod_lead_id = employee.id

    db.flush()
    return employees


def seed_processes():
    """Create 4+ operational processes."""
    process_data = [
        ("CS", "Customer Support", "Handle customer inquiries and support tickets"),
        ("ACC", "Abandoned Cart Conversion", "Convert abandoned shopping carts"),
        ("RET", "Retention", "Customer retention and engagement"),
        ("NDR", "NDR Management", "Non-delivery report handling"),
        ("BIZ", "Business Development", "New business and partnership opportunities"),
    ]

    processes = []
    for code, name, description in process_data:
        process = Process(
            process_code=code,
            process_name=name,
            description=description,
            status="active",
        )
        db.add(process)
        processes.append(process)

    db.flush()
    return processes


def seed_brands(processes):
    """Create 25 brands with realistic distribution."""
    brand_data = [
        # Single-resource brands (20 brands, 80%)
        "UrbanKart", "QuickShop", "FreshCart", "StyleHub", "TechDeal",
        "BeautyBox", "FitnessPro", "HomeNest", "FoodieFam", "TravelMate",
        "EdTechPlus", "HealthCare+", "GadgetZone", "FashionPulse", "EcoLife",
        "PetPals", "BookwormBay", "GamesGalaxy", "CoffeeClub", "GreenGrow",
        # Multi-resource brands (5 brands, 20%)
        "MegaMart", "OmniStore", "SuperBuy", "PremiumPlus", "EliteChoice",
    ]

    brands = []
    for i, name in enumerate(brand_data):
        brand = Brand(
            brand_name=name,
            brand_code=name.upper()[:4],
            description=f"D2C Brand: {name}",
            status="active",
        )
        db.add(brand)
        brands.append(brand)

    db.flush()
    return brands


def seed_assignments(employees, brands, processes):
    """Create assignments following 80/20 distribution."""
    assignments = []

    # Single-resource brands: first 20 brands
    for i in range(20):
        employee = employees[i % 30]
        brand = brands[i]

        # This employee handles all processes for this brand
        for process in processes:
            assignment = Assignment(
                employee_id=employee.id,
                brand_id=brand.id,
                process_id=process.id,
                assigned_from=date.today(),
                priority=1,
                max_daily_capacity=1,
                status="active",
            )
            db.add(assignment)
            assignments.append(assignment)

    # Multi-resource brands: last 5 brands
    for i in range(20, 25):
        brand = brands[i]

        # Assign 2-3 employees
        num_employees = random.randint(2, 3)
        selected_employees = random.sample(employees, num_employees)

        for emp in selected_employees:
            # Assign to different processes
            num_processes = random.randint(1, len(processes))
            selected_processes = random.sample(processes, num_processes)

            for process in selected_processes:
                assignment = Assignment(
                    employee_id=emp.id,
                    brand_id=brand.id,
                    process_id=process.id,
                    assigned_from=date.today(),
                    priority=random.randint(1, 3),
                    max_daily_capacity=1,
                    status="active",
                )
                db.add(assignment)
                assignments.append(assignment)

    db.flush()
    return assignments


def seed_scheduling_rules(brands, processes):
    """Create scheduling rules for brands and processes."""
    # Get current month
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)

    for i, brand in enumerate(brands[:20]):
        # Single-resource brands
        if i % 3 == 0:
            operating_type = "every_day"
            sunday_working = True
            public_holiday_working = False
        elif i % 3 == 1:
            operating_type = "except_public_holidays"
            sunday_working = True
            public_holiday_working = False
        else:
            operating_type = "except_sundays_and_public_holidays"
            sunday_working = False
            public_holiday_working = False

        for process in processes:
            rule = SchedulingRule(
                brand_id=brand.id,
                process_id=process.id,
                operating_type=operating_type,
                sunday_working=sunday_working,
                public_holiday_working=public_holiday_working,
                minimum_staff=1,
                maximum_staff=2,
                priority=1,
                effective_from=month_start,
                effective_until=month_end,
                status="active",
            )
            db.add(rule)

    # Multi-resource brands
    for i, brand in enumerate(brands[20:], start=20):
        operating_type = "every_day" if i % 2 == 0 else "except_sundays_and_public_holidays"

        for process in processes:
            rule = SchedulingRule(
                brand_id=brand.id,
                process_id=process.id,
                operating_type=operating_type,
                sunday_working=(i % 2 == 0),
                public_holiday_working=False,
                minimum_staff=2,
                maximum_staff=3,
                priority=1,
                effective_from=month_start,
                effective_until=month_end,
                status="active",
            )
            db.add(rule)

    db.flush()


def seed_holidays():
    """Create public holidays for India 2024."""
    holidays_data = [
        ("Republic Day", date(2024, 1, 26), "company"),
        ("Holi", date(2024, 3, 25), "company"),
        ("Good Friday", date(2024, 3, 29), "company"),
        ("Eid ul-Fitr", date(2024, 4, 11), "company"),
        ("May Day", date(2024, 5, 1), "company"),
        ("Independence Day", date(2024, 8, 15), "company"),
        ("Janmashtami", date(2024, 8, 26), "company"),
        ("Ganesh Chaturthi", date(2024, 9, 7), "company"),
        ("Dussehra", date(2024, 10, 12), "company"),
        ("Diwali", date(2024, 11, 1), "company"),
        ("Christmas", date(2024, 12, 25), "company"),
    ]

    for name, hdate, scope in holidays_data:
        holiday = Holiday(
            holiday_name=name,
            holiday_date=hdate,
            description=f"Public holiday: {name}",
            applicable_scope=scope,
            status="active",
        )
        db.add(holiday)

    db.flush()


def seed_leaves(employees):
    """Create some approved and pending leaves."""
    start_date = date.today()

    # Create 5-10 leaves for random employees
    for _ in range(random.randint(5, 10)):
        employee = random.choice(employees)
        leave_start = start_date + timedelta(days=random.randint(1, 30))
        leave_end = leave_start + timedelta(days=random.randint(1, 5))

        leave = Leave(
            employee_id=employee.id,
            start_date=leave_start,
            end_date=leave_end,
            leave_type=random.choice([LeaveType.PLANNED.value, LeaveType.SICK.value]),
            status=random.choice([LeaveStatus.APPROVED.value, LeaveStatus.PENDING.value]),
            reason="Personal leave" if random.random() > 0.5 else "Sick leave",
        )
        db.add(leave)

    db.flush()


def seed_availability(employees):
    """Mark some employees as unavailable on specific dates."""
    today = date.today()

    # Mark 10-15 employee-date combinations as unavailable
    for _ in range(random.randint(10, 15)):
        employee = random.choice(employees)
        unavail_date = today + timedelta(days=random.randint(1, 30))

        availability = Availability(
            employee_id=employee.id,
            date=unavail_date,
            availability_status="unavailable",
            reason="Personal commitment",
        )
        db.add(availability)

    db.flush()


def main():
    """Run all seeding functions."""
    print("🌱 Seeding database...")

    # Clear existing data
    print("Clearing existing data...")
    db.query(Assignment).delete()
    db.query(SchedulingRule).delete()
    db.query(Holiday).delete()
    db.query(Leave).delete()
    db.query(Availability).delete()
    db.query(Employee).delete()
    db.query(Brand).delete()
    db.query(Process).delete()
    db.query(Pod).delete()
    db.commit()

    print("Creating pods...")
    pods = seed_pods()

    print("Creating employees...")
    employees = seed_employees(pods)

    print("Creating processes...")
    processes = seed_processes()

    print("Creating brands...")
    brands = seed_brands(processes)

    print("Creating assignments...")
    assignments = seed_assignments(employees, brands, processes)

    print("Creating scheduling rules...")
    seed_scheduling_rules(brands, processes)

    print("Creating holidays...")
    seed_holidays()

    print("Creating leaves...")
    seed_leaves(employees)

    print("Creating availability records...")
    seed_availability(employees)

    db.commit()

    print("✅ Database seeded successfully!")
    print(f"   - {len(pods)} pods")
    print(f"   - {len(employees)} employees")
    print(f"   - {len(processes)} processes")
    print(f"   - {len(brands)} brands")
    print(f"   - {len(assignments)} assignments")

    db.close()


if __name__ == "__main__":
    main()
