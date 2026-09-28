import sys
sys.path.insert(0, r'D:\project\yearn\backend')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT id, name, solar_date FROM birthdays WHERE id=501")).fetchone()
print('before:', result)
db.execute(text("UPDATE birthdays SET solar_date='1995-06-15', lunar_date=NULL, is_lunar=0, is_leap_month=0 WHERE id=501"))
db.commit()
result2 = db.execute(text("SELECT id, name, solar_date FROM birthdays WHERE id=501")).fetchone()
print('after:', result2)
db.close()
