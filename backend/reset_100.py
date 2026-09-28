import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from app.models.birthday import Birthday
import random

db = SessionLocal()
db.query(Birthday).delete()
db.commit()

surnames = ['张','王','李','刘','陈','杨','黄','赵','周','吴','徐','孙','马','朱','胡','郭','林','何','高','梁']
given = ['伟','芳','娜','秀','敏','静','丽','强','磊','军','洋','勇','艳','杰','涛','明','超','宇','晨','欣','怡','梦','琪','琳','浩','子涵','梓萱','浩然','思远','雨桐','思雨','一诺','沐阳','诗涵']
cats = ['朋友','家人','同事','客户','同学','other']
rems = ['送礼物','请吃饭','发红包','打电话问候','寄快递','']

for i in range(100):
    sn = random.choice(surnames)
    gn = random.choice(given)
    name = sn + gn + (str(i+1) if random.random() < 0.2 else '')
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    yr = random.randint(1970, 2010)
    is_lunar = random.random() < 0.5
    db.add(Birthday(
        name=name,
        solar_date=f'{yr}-{m:02d}-{d:02d}',
        lunar_date=f'{yr}-{m:02d}-{d:02d}' if is_lunar else None,
        is_lunar=is_lunar,
        category=random.choice(cats),
        remark=random.choice(rems),
        is_enabled=random.random() < 0.9,
    ))

db.commit()
total = db.query(Birthday).count()
print('done:', total)
db.close()
