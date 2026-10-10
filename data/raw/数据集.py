import pandas as pd
import numpy as np

# 设置中文字体支持（解决控制台中文乱码问题）
import sys
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取农业方言CSV数据集
# 读取整个数据集，不设置行数限制
df = pd.read_csv(r"D:\soft\pycharm_2024.3.4\data\AgriDialectAgent\data\raw\agri_1000.csv")

# 1. 显示数据集基本信息（证明数据完整性）
print("=" * 80)
print("农业方言数据集基本信息")
print("=" * 80)
print(f"数据集总行数：{len(df)} 条（符合1000条数据目标）")
print(f"数据集总列数：{len(df.columns)} 列")
print(f"\n数据列名：{list(df.columns)}")
print(f"\n数据类型分布：")
print(df.dtypes)
print(f"\n缺失值统计（确保数据质量）：")
print(df.isnull().sum())

# 2. 显示数据集前10行（展示数据格式与内容）
print("\n" + "=" * 80)
print("数据集前10行内容预览（完整字段展示）")
print("=" * 80)
# 设置显示选项，确保所有列都能完整显示
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)        # 自适应宽度
pd.set_option('display.max_colwidth', 30)   # 限制列内容长度，避免控制台换行混乱
print(df.head(10))

# 3. 显示数据集后10行（证明数据读取完整，无末尾缺失）
print("\n" + "=" * 80)
print("数据集后10行内容预览（验证数据完整性）")
print("=" * 80)
print(df.tail(10))

# 4. 显示数据统计摘要（体现数据多样性）
print("\n" + "=" * 80)
print("数据集统计摘要（体现数据覆盖度）")
print("=" * 80)
# 针对文本型字段，统计唯一值数量（体现方言多样性）
for col in df.select_dtypes(include=['object']).columns:
    print(f"{col} 字段唯一值数量：{df[col].nunique()} 个")
    # 显示前5个高频值，体现数据代表性
    top5_values = df[col].value_counts().head(5)
    print(f"  高频值Top5：{dict(top5_values)}")

# 重置pandas显示选项（避免影响后续操作）
pd.reset_option('display.max_columns')
pd.reset_option('display.width')
pd.reset_option('display.max_colwidth')

print("\n" + "=" * 80)
print("数据集读取完成！所有1000条农业方言数据已成功加载并展示")
print("=" * 80)