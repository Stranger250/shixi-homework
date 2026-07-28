import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (mean_squared_error, mean_absolute_error,
                             r2_score)


# 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

if not os.path.exists("task3_output"):
    os.mkdir("task3_output")


#1.加载数据并进行探索性分析
housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = pd.Series(housing.target, name='房价中位数')

# 特征名称中英文映射
feature_names_cn = {
    'MedInc':    '收入中位数',
    'HouseAge':  '房龄',
    'AveRooms':  '平均房间数',
    'AveBedrms': '平均卧室数',
    'Population':'人口数',
    'AveOccup':  '平均居住人数',
    'Latitude':  '纬度',
    'Longitude': '经度',
}

print(f"数据集大小: {X.shape}")
print(f"特征数量: {X.shape[1]}")
print(f"\n数据描述统计:")
print(X.describe().round(2))
print(f"\n目标变量(房价中位数, 单位: $100k):")
print(f"  均值: {y.mean():.3f}  标准差: {y.std():.3f}")
print(f"  最小值: {y.min():.3f}  最大值: {y.max():.3f}")
print(f"\n缺失值数量:\n{X.isnull().sum()}")

# --- 1.1 房价分布直方图 ---
plt.figure(figsize=(8, 5))
plt.hist(y, bins=50, edgecolor='black', alpha=0.75, color='#2E86AB')
plt.axvline(y.mean(), color='red', linestyle='--', linewidth=2,
            label=f'均值: {y.mean():.3f}')
plt.axvline(y.median(), color='orange', linestyle='--', linewidth=2,
            label=f'中位数: {y.median():.3f}')
plt.xlabel('房价中位数 ($100k)', fontsize=12)
plt.ylabel('频次', fontsize=12)
plt.title('加州房价分布直方图', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig('task3_output/01_房价分布.png', dpi=300, bbox_inches='tight')
plt.close()

# --- 1.2 相关性热力图 ---
plt.figure(figsize=(10, 8))
corr_matrix = X.copy()
corr_matrix['房价'] = y
corr = corr_matrix.corr()
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1,
            square=True, linewidths=0.5, fmt='.2f', mask=mask)
plt.title('特征与房价相关性热力图', fontsize=14)
plt.tight_layout()
plt.savefig('task3_output/02_相关性热力图.png', dpi=300, bbox_inches='tight')
plt.close()
print("\n已保存: 01_房价分布.png, 02_相关性热力图.png")

# --- 1.3 最强特征与房价的散点图 ---
top_features = corr['房价'].abs().sort_values(ascending=False).index[1:5]  # 排除房价自身
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()
for i, feat in enumerate(top_features):
    if feat in housing.feature_names:
        axes[i].scatter(X[feat], y, alpha=0.3, s=3, color='#2E86AB')
        axes[i].set_xlabel(feature_names_cn.get(feat, feat), fontsize=11)
        axes[i].set_ylabel('房价中位数', fontsize=11)
        axes[i].set_title(f'{feature_names_cn.get(feat, feat)} vs 房价', fontsize=12)
plt.suptitle('Top4 特征与房价散点图', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig('task3_output/03_特征散点图.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: 03_特征散点图.png")


#2.进行特征工程(标准化、特征选择)
# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"训练集: {X_train.shape}  测试集: {X_test.shape}")

#标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("特征标准化完成")

# 基于相关性的特征选择（保留 |r| > 0.1 的特征）
feature_corr = corr['房价'].drop('房价').abs().sort_values(ascending=False)
selected_features = feature_corr[feature_corr > 0.1].index.tolist()
print(f"\n相关性 > 0.1 的特征 ({len(selected_features)}个):")
for f in selected_features:
    print(f"  {feature_names_cn.get(f, f):　<8s}  r = {corr.loc[f, '房价']:+.3f}")


#3.使用线性回归、决策树、随机森林分别训练模型
models = {
    '线性回归': LinearRegression(),
    '决策树': DecisionTreeRegressor(max_depth=8, random_state=42),
    '随机森林': RandomForestRegressor(n_estimators=100, max_depth=10,
                                      random_state=42, n_jobs=-1),
}

results = {}

for name, model in models.items():

    print(f"======================{name}=========================")

    # 线性回归用标准化数据,树模型用原始数据
    if name == '线性回归':
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # 交叉验证
    if name == '线性回归':
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    else:
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')

    print(f"MSE:  {mse:.4f}    RMSE: {rmse:.4f}    MAE:  {mae:.4f}")
    print(f"R2:   {r2:.4f}")
    print(f"5折交叉验证 R2: {cv_scores.mean():.4f} (+/-{cv_scores.std():.4f})")

    results[name] = {
        'y_pred': y_pred,
        'mse': mse, 'rmse': rmse, 'mae': mae, 'r2': r2,
        'cv_mean': cv_scores.mean(),
    }


#4.比较三种模型的性能(MSE、R2)
# --- 4.1 MSE 和 R2 柱状图 ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
names = list(results.keys())
colors = ['#2E86AB', '#F24236', '#F5A623']

mse_values = [results[n]['mse'] for n in names]
bars1 = axes[0].bar(names, mse_values, color=colors, alpha=0.85, edgecolor='black')
axes[0].set_ylabel('MSE', fontsize=12)
axes[0].set_title('模型 MSE 对比 (越低越好)', fontsize=13)
for bar, val in zip(bars1, mse_values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                f'{val:.4f}', ha='center', fontsize=11)
axes[0].grid(axis='y', alpha=0.3)

r2_values = [results[n]['r2'] for n in names]
bars2 = axes[1].bar(names, r2_values, color=colors, alpha=0.85, edgecolor='black')
axes[1].set_ylabel('R2', fontsize=12)
axes[1].set_title('模型 R2 对比 (越高越好)', fontsize=13)
axes[1].set_ylim(0, 1)
for bar, val in zip(bars2, r2_values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.4f}', ha='center', fontsize=11)
axes[1].grid(axis='y', alpha=0.3)

plt.suptitle('三模型性能对比', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('task3_output/04_模型性能对比.png', dpi=300, bbox_inches='tight')
plt.close()

# --- 4.2 预测值 vs 真实值散点图 ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
for ax, (name, res) in zip(axes, results.items()):
    ax.scatter(y_test, res['y_pred'], alpha=0.3, s=5, color=colors[list(results.keys()).index(name)])
    ax.plot([0, 5], [0, 5], 'r--', linewidth=1.5, label='理想预测线')
    ax.set_xlabel('真实房价 ($100k)', fontsize=11)
    ax.set_ylabel('预测房价 ($100k)', fontsize=11)
    ax.set_title(f'{name}  (R2={res["r2"]:.4f})', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
plt.suptitle('预测值 vs 真实值', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('task3_output/05_预测vs真实.png', dpi=300, bbox_inches='tight')
plt.close()

print("已保存: 04_模型性能对比.png, 05_预测vs真实.png")


#5.输出特征重要性排序
# 随机森林特征重要性
rf_model = models['随机森林']
rf_importances = rf_model.feature_importances_
rf_indices = np.argsort(rf_importances)[::-1]

# 线性回归系数（标准化后的系数可反映重要性）
lr_model = models['线性回归']
lr_coef_abs = np.abs(lr_model.coef_)

# 两图并排
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

colors_rf = plt.cm.Blues(np.linspace(0.4, 0.9, len(housing.feature_names)))
axes[0].barh(range(X.shape[1]), rf_importances[rf_indices], color=colors_rf)
axes[0].set_yticks(range(X.shape[1]))
axes[0].set_yticklabels([feature_names_cn[housing.feature_names[i]]
                          for i in rf_indices])
axes[0].set_xlabel('重要性', fontsize=12)
axes[0].set_title('随机森林 - 特征重要性', fontsize=13)
axes[0].invert_yaxis()

coef_indices = np.argsort(lr_coef_abs)[::-1]
colors_lr = plt.cm.Oranges(np.linspace(0.4, 0.9, len(housing.feature_names)))
axes[1].barh(range(X.shape[1]), lr_coef_abs[coef_indices], color=colors_lr)
axes[1].set_yticks(range(X.shape[1]))
axes[1].set_yticklabels([feature_names_cn[housing.feature_names[i]]
                          for i in coef_indices])
axes[1].set_xlabel('|系数| (标准化后)', fontsize=12)
axes[1].set_title('线性回归 - 特征重要性 (|系数|)', fontsize=13)
axes[1].invert_yaxis()

plt.suptitle('特征重要性排序', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('task3_output/06_特征重要性.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: 06_特征重要性.png")

# --- 文本输出特征重要性 ---
print(f"\n随机森林特征重要性排名:")
for i in rf_indices:
    print(f"  {housing.feature_names[i]:　<12s}  {feature_names_cn[housing.feature_names[i]]:　<8s} = {rf_importances[i]:.4f}")

print(f"\n线性回归 |系数| 排名:")
for i in coef_indices:
    print(f"  {housing.feature_names[i]:　<12s}  {feature_names_cn[housing.feature_names[i]]:　<8s} = {lr_coef_abs[i]:.4f}")


#效果对比
print("==========================6. 模型对比分析==========================")

print(f"  模型          MSE        RMSE       MAE        R2         CV-R2      ")
for name, res in results.items():
    print(f"  {name:　<8s}  {res['mse']:.4f}    {res['rmse']:.4f}    "
          f"{res['mae']:.4f}    {res['r2']:.4f}    {res['cv_mean']:.4f}    ")

best = max(results.items(), key=lambda x: x[1]['r2'])
print(f"\n最优模型: {best[0]} (R2={best[1]['r2']:.4f})")

print(f"""
分析结论:
-----------------------------------------------------
1. 随机森林表现最佳,R2 最高、MSE 最低。说明房价数据中
   存在非线性关系,集成学习能更好地捕获这些复杂模式。

2. 线性回归虽然简单,但 R2 也接近 0.6,说明房价与特征
   之间存在较明显的线性趋势。可解释性强是其优势。

3. 决策树容易过拟合(max_depth控制后可缓解),单一决策树
   的泛化能力弱于随机森林。

4. 最重要的预测特征:'收入中位数(MedInc)'远超其他特征,
   符合直觉——收入水平是决定房价的最关键因素。

5. 地理位置(经度、纬度)也是重要特征,反映了加州不同地区
   的房价差异(沿海地区房价更高)。

6. 房龄呈负相关:房子越旧价格越低,但影响程度较小。
-----------------------------------------------------
""")

print("\n所有图表已保存至 task3_output/ 文件夹")
