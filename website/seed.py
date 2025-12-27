import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import Department, MaintenanceTeam, Technician, User, Equipment, MaintenanceRequest, WorkCenter

# --- DATA LISTS ---
DEPT_NAMES = ['Production', 'Logistics', 'Quality Control', 'Research & Development', 'Assembly Line']
TEAM_NAMES = ['Alpha (Mechanical)', 'Beta (Electrical)', 'Gamma (Hydraulics)', 'Delta (IT & Sensors)', 'Sigma (Robotics)']

NAMES_MALE = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Rohan", "Vikram", "Kabir", "Ravi"]
NAMES_FEMALE = ["Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Riya", "Anvi", "Pihu", "Myra", "Zara", "Kavya", "Sneha", "Priya", "Nisha", "Meera"]

EQUIP_TYPES = [
    ("CNC Machine", "CNC"), ("Conveyor Belt", "CV"), ("Hydraulic Press", "HP"), 
    ("Industrial Robot", "ROB"), ("Diesel Generator", "GEN"), ("Forklift", "FL"),
    ("Injection Molder", "IM"), ("Packaging Unit", "PKG"), ("Laser Cutter", "LC"), ("Air Compressor", "AC")
]

ISSUES = [
    "Oil leakage detected", "Overheating warning", "Abnormal vibration", "Belt snapped", 
    "Software calibration error", "Sensor malfunction", "Hydraulic pressure drop", 
    "Emergency stop stuck", "Bearing noise", "Motor burnout", "Coolant leak", "Misalignment detected"
]

def get_random_date():
    # Generate a random date within last 90 days for graphs
    days_back = random.randint(0, 90)
    return datetime.utcnow() - timedelta(days=days_back)

def run_seed():
    with app.app_context():
        print("🌱 Database Resetting & Seeding started...")
        
        # 1. CLEAN DATABASE
        db.drop_all()
        db.create_all()
        print("🧹 Old data cleared.")

        # 2. CREATE DEPARTMENTS
        depts = []
        for name in DEPT_NAMES:
            d = Department(name=name)
            depts.append(d)
        db.session.add_all(depts)
        db.session.commit()
        print(f"✅ {len(depts)} Departments Added.")

        # 3. CREATE TEAMS
        teams = []
        for name in TEAM_NAMES:
            t = MaintenanceTeam(name=name)
            teams.append(t)
        db.session.add_all(teams)
        db.session.commit()
        print(f"✅ {len(teams)} Teams Added.")

        # 4. CREATE WORK CENTERS (10 Entries)
        wc_data = [
            ("Main Assembly A", "WC-001", 150.0, 92, 85),
            ("CNC Machining B", "WC-002", 200.0, 88, 80),
            ("Packaging Zone", "WC-003", 75.0, 95, 90),
            ("Quality Lab 1", "WC-004", 120.0, 98, 95),
            ("Welding Station", "WC-005", 180.0, 85, 78),
            ("Paint Shop", "WC-006", 130.0, 90, 82),
            ("Elec. Assembly", "WC-007", 160.0, 94, 88),
            ("Finishing Line", "WC-008", 100.0, 91, 85),
            ("Raw Material Depot", "WC-009", 60.0, 96, 90),
            ("Robotic Cell X", "WC-010", 250.0, 82, 80)
        ]
        for name, code, cost, eff, target in wc_data:
            wc = WorkCenter(name=name, code=code, cost_per_hour=cost, capacity_efficiency=eff, oee_target=target)
            db.session.add(wc)
        db.session.commit()
        print("✅ 10 Work Centers Added.")

        # 5. CREATE USERS (Employees - 20 Entries)
        # Samarth (Admin/User) ko fix rakhenge login ke liye
        all_users = []
        admin = User(name='Samarth', email='samarth@gear.com', password_hash=generate_password_hash('123'), department_id=depts[0].id)
        all_users.append(admin)
        
        full_names = NAMES_MALE + NAMES_FEMALE
        random.shuffle(full_names)

        for i in range(19): # 19 more users
            name = full_names[i]
            u = User(
                name=f"{name} {random.choice(['Sharma', 'Verma', 'Patel', 'Singh', 'Gupta'])}",
                email=f"{name.lower()}{i}@gear.com",
                password_hash=generate_password_hash('123'),
                department_id=random.choice(depts).id
            )
            all_users.append(u)
        
        db.session.add_all(all_users)
        db.session.commit()
        print("✅ 20 Users Added (Login: samarth@gear.com / 123).")

        # 6. CREATE TECHNICIANS (15 Entries)
        # Mike (Tech) ko fix rakhenge login ke liye
        all_techs = []
        mike = Technician(name='Mike Ross', email='mike@gear.com', password_hash=generate_password_hash('123'), team_id=teams[0].id)
        all_techs.append(mike)

        tech_names = NAMES_MALE[5:] + NAMES_FEMALE[5:] # Use remaining names
        random.shuffle(tech_names)

        for i in range(14):
            name = tech_names[i]
            t = Technician(
                name=f"{name} {random.choice(['Yadav', 'Khan', 'Das', 'Nair', 'Reddy'])}",
                email=f"tech{i}@gear.com",
                password_hash=generate_password_hash('123'),
                team_id=random.choice(teams).id
            )
            all_techs.append(t)

        db.session.add_all(all_techs)
        db.session.commit()
        print("✅ 15 Technicians Added (Login: mike@gear.com / 123).")

        # 7. CREATE EQUIPMENT (25 Entries)
        all_equipment = []
        for i in range(1, 26):
            eq_type, prefix = random.choice(EQUIP_TYPES)
            eq = Equipment(
                name=f"{eq_type} #{random.randint(100, 999)}",
                serial_number=f"{prefix}-2025-{i:03d}",
                location=f"Floor {random.randint(1,3)}, Zone {random.choice(['A','B','C','D'])}",
                department_id=random.choice(depts).id,
                team_id=random.choice(teams).id
            )
            all_equipment.append(eq)
        
        db.session.add_all(all_equipment)
        db.session.commit()
        print("✅ 25 Equipment Added.")

        # 8. CREATE MAINTENANCE REQUESTS (40 Entries)
        requests = []
        statuses = ['new', 'in_progress', 'repaired', 'scrap']
        
        # Thoda logic: Scrap kam honge, Repaired jyada (graph ke liye)
        weighted_statuses = ['new']*8 + ['in_progress']*10 + ['repaired']*20 + ['scrap']*2

        for i in range(40):
            status = random.choice(weighted_statuses)
            eq = random.choice(all_equipment)
            creator = random.choice(all_users)
            
            req = MaintenanceRequest(
                description=random.choice(ISSUES),
                status=status,
                equipment_id=eq.id,
                team_id=eq.team_id,
                created_by=creator.id,
                created_at=get_random_date() # Random date in last 3 months
            )

            # Assign technician only if NOT 'new'
            if status != 'new':
                # Pick a tech from the correct team
                possible_techs = [t for t in all_techs if t.team_id == eq.team_id]
                if possible_techs:
                    req.technician_id = random.choice(possible_techs).id
                
                # Add duration if repaired
                if status == 'repaired':
                    req.duration_hours = round(random.uniform(1.0, 48.0), 1)
            
            requests.append(req)

        db.session.add_all(requests)
        db.session.commit()
        print("✅ 40 Maintenance Requests Added (with graph history).")

        print("\n🎉 MEGA SEED COMPLETE! Database full bhara hua hai.")
        print("👉 User Login: samarth@gear.com / 123")

if __name__ == '__main__':
    run_seed()