from app import app, db
from models import Department, MaintenanceTeam, Technician, User, Equipment, MaintenanceRequest
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def run_seed():
    with app.app_context():
        print("🌱 Database seeding shuru ho raha hai...")
        
        # 1. Purana Data Saaf karo (Optional: Agar fresh start chahiye)
        db.drop_all()
        db.create_all()
        print("🧹 Purana data saaf kiya aur naye tables banaye.")

        # 2. DEPARTMENTS Create karo
        dept_prod = Department(name='Production')
        dept_logistics = Department(name='Logistics')
        dept_quality = Department(name='Quality Control')
        db.session.add_all([dept_prod, dept_logistics, dept_quality])
        db.session.commit()
        print("✅ Departments ban gaye.")

        # 3. MAINTENANCE TEAMS Create karo
        team_alpha = MaintenanceTeam(name='Alpha Team (Mechanical)')
        team_beta = MaintenanceTeam(name='Beta Team (Electrical)')
        db.session.add_all([team_alpha, team_beta])
        db.session.commit()
        print("✅ Teams ban gayi.")

        # 4. TECHNICIANS Create karo (Login: mike@gear.com / 123)
        tech1 = Technician(
            name='Mike Ross', 
            email='mike@gear.com', 
            password_hash=generate_password_hash('123'),
            team_id=team_alpha.id
        )
        tech2 = Technician(
            name='Harvey Specter', 
            email='harvey@gear.com', 
            password_hash=generate_password_hash('123'),
            team_id=team_beta.id
        )
        db.session.add_all([tech1, tech2])
        db.session.commit()
        print("✅ Technicians add ho gaye.")

        # 5. EMPLOYEES (USERS) Create karo (Login: samarth@gear.com / 123)
        user1 = User(
            name='Samarth', 
            email='samarth@gear.com', 
            password_hash=generate_password_hash('123'),
            department_id=dept_prod.id
        )
        user2 = User(
            name='Riya Sharma', 
            email='riya@gear.com', 
            password_hash=generate_password_hash('123'),
            department_id=dept_quality.id
        )
        db.session.add_all([user1, user2])
        db.session.commit()
        print("✅ Users (Employees) add ho gaye.")

        # 6. EQUIPMENT (MACHINES) Create karo
        eq1 = Equipment(
            name='CNC Machine #3', 
            serial_number='CNC-2025-01', 
            location='Floor 1, Zone A',
            department_id=dept_prod.id,
            team_id=team_alpha.id # Mechanical Team
        )
        eq2 = Equipment(
            name='Conveyor Belt B', 
            serial_number='CV-2025-99', 
            location='Floor 2, Zone C',
            department_id=dept_logistics.id,
            team_id=team_alpha.id
        )
        eq3 = Equipment(
            name='Main Generator', 
            serial_number='GEN-5000', 
            location='Power Room',
            department_id=dept_prod.id,
            team_id=team_beta.id # Electrical Team
        )
        db.session.add_all([eq1, eq2, eq3])
        db.session.commit()
        print("✅ Machines (Equipment) add ho gayi.")

        # 7. KUCH FAKE REQUESTS (Taaki Dashboard Khali na dikhe)
        req1 = MaintenanceRequest(
            description='Oil leakage in main valve',
            status='new', # New Request column me dikhega
            equipment_id=eq1.id,
            team_id=eq1.team_id,
            created_by=user1.id,
            created_at=datetime.utcnow()
        )
        
        req2 = MaintenanceRequest(
            description='Motor overheating error',
            status='in_progress', # In Progress column me dikhega
            equipment_id=eq3.id,
            team_id=eq3.team_id,
            technician_id=tech2.id, # Harvey assigned hai
            created_by=user1.id,
            created_at=datetime.utcnow() - timedelta(hours=2)
        )

        req3 = MaintenanceRequest(
            description='Belt Alignment Fixed',
            status='repaired', # Repaired column me dikhega
            equipment_id=eq2.id,
            team_id=eq2.team_id,
            technician_id=tech1.id,
            created_by=user2.id,
            created_at=datetime.utcnow() - timedelta(days=1)
        )

        db.session.add_all([req1, req2, req3])
        db.session.commit()
        print("✅ Fake Requests add ho gaye.")
        
        print("\n🎉 SAB DONE! Ab app run karo.")
        print("👉 User Login: samarth@gear.com / 123")
        print("👉 Technician Login: mike@gear.com / 123")

if __name__ == '__main__':
    run_seed()