"""
生成500条测试数据
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, engine, Base
from app.models.birthday import Birthday
import random
from datetime import date, timedelta

# 确保表存在
Base.metadata.create_all(bind=engine)

# 常见姓名
surnames = ['张', '王', '李', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '林', '何', '高', '梁',
            '郑', '罗', '宋', '谢', '唐', '韩', '曹', '许', '邓', '萧']

given_names = ['伟', '芳', '娜', '秀', '敏', '静', '丽', '强', '磊', '军',
                '洋', '勇', '艳', '杰', '涛', '明', '超', '秀', '霞', '平',
                '刚', '桂', '英', '华', '建', '云', '海', '雪', '梅', '小',
                '宇', '晨', '欣', '怡', '梦', '琪', '琳', '浩', '子涵', '梓萱',
                '浩然', '思远', '雨桐', '思雨', '子轩', '子墨', '一诺', '梓涵', '沐阳', '诗涵']

categories = ['朋友', '家人', '同事', '客户', '同学', '其他']
remarks = ['送礼物', '请吃饭', '发红包', '打电话问候', '寄快递', '']
genders = ['male', 'female', 'unspecified']
gender_weights = [0.45, 0.45, 0.10]  # 男女各45%，未知10%

db = SessionLocal()

# 统计已有数量
existing = db.query(Birthday).count()
print(f"当前已有 {existing} 条记录")

if existing >= 500:
    print("已有500条以上，跳过生成")
    db.close()
    exit()

# 生成数据
target = 500
to_add = target - existing
today = date.today()

added = 0
for i in range(to_add):
    surname = random.choice(surnames)
    given = random.choice(given_names)
    name = surname + given + (str(i + 1) if random.random() < 0.2 else '')

    # 生成随机日期（分布在全年）
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(1970, 2010)

    # 50% 概率为农历
    is_lunar = random.random() < 0.5

    # 农历日期格式（用lunardate自动算，这里用公历模拟）
    solar_date = f"{year}-{month:02d}-{day:02d}"
    lunar_date = f"{year}-{month:02d}-{day:02d}" if is_lunar else None

    category = random.choice(categories)
    remark = random.choice(remarks)

    birthday = Birthday(
        name=name,
        solar_date=solar_date,
        lunar_date=lunar_date,
        is_lunar=is_lunar,
        category=category,
        remark=remark,
        is_enabled=random.random() < 0.9,
        gender=random.choices(genders, weights=gender_weights)[0],
    )
    db.add(birthday)
    added += 1

    if (i + 1) % 100 == 0:
        db.commit()
        print(f"已添加 {i + 1} 条...")

db.commit()
db.close()

print(f"✅ 完成！共添加 {added} 条测试数据，总计 {existing + added} 条")
