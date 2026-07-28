import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_curve, auc, accuracy_score,
                             precision_score, recall_score, f1_score)


# 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

if not os.path.exists("task2_output"):
    os.mkdir("task2_output")


#1.生成模拟客户数据
np.random.seed(42)
n_samples = 1000

data = pd.DataFrame({
    '年龄': np.random.randint(18, 65, n_samples),
    '月消费金额': np.random.exponential(200,n_samples),
    '使用时长_月': np.random.randint(1, 60, n_samples),
    '投诉次数': np.random.poisson(0.5, n_samples),
    '是否流失': np.zeros(n_samples, dtype = int)
})

score = (
    -0.02 * data['年龄']                           # 年龄越大,流失概率越低(忠诚度更高)
    + 0.005 * data['月消费金额']                    # 消费高但使用时间短更易流失
    - 0.05 * data['使用时长_月']                    # 使用越久,流失概率越低
    + 0.8 * data['投诉次数']                        # 投诉越多,流失概率越高
    - 1.0                                           # 偏置项,控制总体流失率
)
prob = 1 / (1 + np.exp(-score))
data['是否流失'] = (np.random.random(n_samples) < prob).astype(int)

print(f"数据总量: {len(data)}")
print(f"流失比例: {data['是否流失'].mean():.1%}")
print(data.head(8))

#2.数据预处理
# 添加类别特征: 消费等级
bins = [0, 100, 300, float('inf')]
labels = ['低消费', '中消费', '高消费']
data['消费等级'] = pd.cut(data['月消费金额'], bins=bins, labels=labels)

# 查看各类别流失率
print("各消费等级流失率:")
print(data.groupby('消费等级', observed=False)['是否流失'].agg(['count', 'mean']))

# 对类别特征进行编码
data_encoded = pd.get_dummies(data, columns=['消费等级'], drop_first=True)

# 分离特征和标签
feature_cols = ['年龄', '月消费金额', '使用时长_月', '投诉次数',
                '消费等级_中消费', '消费等级_高消费']
X = data_encoded[feature_cols]
y = data_encoded['是否流失']

#标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)
print(f"训练集: {len(X_train)}  测试集: {len(X_test)}")
print(f"训练集流失率: {y_train.mean():.1%}  测试集流失率: {y_test.mean():.1%}")


#3.使用逻辑回归，SVM，随机森林训练模型
models = {
    '逻辑回归': LogisticRegression(max_iter=1000, random_state=42),
    'SVM': SVC(kernel='rbf', probability=True, random_state=42),
    '随机森林': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
}

results = {}

for name, model in models.items():
    
    print(f"======================{name}=========================")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # 五折交叉验证
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='f1')
    print(f"准确率: {acc:.4f}  精确率: {prec:.4f}  召回率: {rec:.4f}  F1: {f1:.4f}")
    print(f"5折交叉验证F1: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    print(f"\n分类报告:\n{classification_report(y_test, y_pred, target_names=['未流失', '流失'])}")

    results[name] = {
        'y_pred': y_pred,
        'y_prob': y_prob,
        'acc': acc, 'prec': prec, 'rec': rec, 'f1': f1,
        'cv_mean': cv_scores.mean(),
    }


#4.输出分类报告，混淆矩阵，ROC曲线
# --- 4.1 混淆矩阵对比 ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (name, res) in zip(axes, results.items()):
    cm = confusion_matrix(y_test, res['y_pred'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['未流失', '流失'],
                yticklabels=['未流失', '流失'])
    ax.set_title(f'{name} - 混淆矩阵', fontsize=13)
    ax.set_xlabel('预测标签')
    ax.set_ylabel('真实标签')
plt.suptitle('三模型混淆矩阵对比', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('task2_output/01_混淆矩阵对比.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: 01_混淆矩阵对比.png")

# --- 4.2 ROC曲线对比 ---
plt.figure(figsize=(9, 7))
colors = {'逻辑回归': '#2E86AB', 'SVM': '#F24236', '随机森林': '#F5A623'}
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, lw=2.5, color=colors[name],
             label=f'{name} (AUC={roc_auc:.4f})')
plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='随机猜测 (AUC=0.5)', alpha=0.5)
plt.xlabel('假正率 (FPR)', fontsize=12)
plt.ylabel('真正率 (TPR / Recall)', fontsize=12)
plt.title('三模型 ROC 曲线对比', fontsize=14)
plt.legend(loc='lower right', fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('task2_output/02_ROC曲线对比.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: 02_ROC曲线对比.png")

# --- 4.3 指标柱状图对比 ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 子图1: 准确率/精确率/召回率/F1
metrics = ['acc', 'prec', 'rec', 'f1']
metric_labels = ['准确率', '精确率', '召回率', 'F1-Score']
x_pos = np.arange(len(metrics))
width = 0.25
for i, (name, res) in enumerate(results.items()):
    values = [res[m] for m in metrics]
    axes[0].bar(x_pos + i * width, values, width, label=name, alpha=0.85)
axes[0].set_xticks(x_pos + width)
axes[0].set_xticklabels(metric_labels)
axes[0].set_ylim(0, 1)
axes[0].set_ylabel('分数')
axes[0].set_title('各模型指标对比', fontsize=13)
axes[0].legend(fontsize=9)
axes[0].grid(axis='y', alpha=0.3)

# 子图2: 交叉验证F1
names = list(results.keys())
cv_means = [results[n]['cv_mean'] for n in names]
bars = axes[1].bar(names, cv_means, color=[colors[n] for n in names], alpha=0.85)
axes[1].set_ylim(0, 1)
axes[1].set_ylabel('F1-Score')
axes[1].set_title('5折交叉验证 F1 对比', fontsize=13)
for bar, val in zip(bars, cv_means):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.4f}', ha='center', fontsize=11)
axes[1].grid(axis='y', alpha=0.3)

plt.suptitle('模型性能全面对比', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('task2_output/03_指标对比.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: 03_指标对比.png")

# --- 4.4 随机森林特征重要性 ---
rf_model = models['随机森林']
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
colors_bar = plt.cm.Blues(np.linspace(0.4, 0.9, len(feature_cols)))
plt.barh(range(len(feature_cols)), importances[indices], color=colors_bar)
plt.yticks(range(len(feature_cols)), [feature_cols[i] for i in indices])
plt.xlabel('重要性', fontsize=12)
plt.title('随机森林 - 特征重要性排名', fontsize=14)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('task2_output/04_特征重要性.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: 04_特征重要性.png")


#效果对比
print("==========================5. 模型对比分析==========================")

print(f"  模型         准确率     精确率     召回率     F1-Score   CV-F1      ")
for name, res in results.items():
    print(f"  {name:　<8s}  {res['acc']:.4f}    {res['prec']:.4f}    "
          f"{res['rec']:.4f}    {res['f1']:.4f}    {res['cv_mean']:.4f}    ")

# 找出最佳模型
best_f1 = max(results.items(), key=lambda x: x[1]['f1'])
best_auc_name = max(results.items(), key=lambda x: auc(*roc_curve(y_test, x[1]['y_prob'])[:2]))
print(f"\n最佳 F1-Score: {best_f1[0]} ({best_f1[1]['f1']:.4f})")
print(f"最佳 AUC:      {best_auc_name[0]} ({auc(*roc_curve(y_test, best_auc_name[1]['y_prob'])[:2]):.4f})")

print(f"""
分析结论:
-----------------------------------------------------
1. 在这个模拟的客户流失数据上,逻辑回归表现良好。因为数据是
   通过 sigmoid 函数生成的,与逻辑回归的模型假设天然匹配。

2. 随机森林通过集成多个决策树,能捕捉非线性特征组合,通常
   在真实数据上泛化能力更强,且能输出特征重要性。

3. SVM(RBF核)适合非线性边界,但数据量较大时训练较慢。

4. 特征重要性分析表明:'投诉次数'和'使用时长'是预测客户
   流失最关键的因素——投诉多、使用时间短的客户流失风险高。

5. 在真实业务中应优先关注召回率(Recall),宁可多预警几个
   潜在流失客户,也不能漏掉真正要流失的客户。
----------------------------------------------------
""")

print("\n所有图表已保存至 task2_output/ 文件夹")