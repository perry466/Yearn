import sys
sys.path.insert(0, r'D:\project\yearn\backend')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 看几条 is_lunar=1 的记录
print("=== 农历记录 solar_date 样本 ===")
rows = db.execute(text("SELECT name, solar_date, lunar_date, is_lunar FROM birthdays WHERE is_lunar=1 LIMIT 5")).fetchall()
for r in rows:
    print(r)

print("\n=== 公历记录 solar_date 样本 ===")
rows2 = db.execute(text("SELECT name, solar_date FROM birthdays WHERE is_lunar=0 LIMIT 5")).fetchall()
for r in rows2:
    print(r)

# 手动添加的数据：找最新的几条
print("\n=== 最新的5条记录 ===")
rows3 = db.execute(text("SELECT id, name, solar_date, lunar_date, is_lunar, gender FROM birthdays ORDER BY id DESC LIMIT 5")).fetchall()
for r in rows3:
    print(r)

db.close()
