#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rc('font',family='Arial',size=14)

#%%
InvMid = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '中速技术进步情景')

#%%
turbineCosts = pd.read_excel('../data/cost/SI_key_parameters.xlsx', 'A1. 中国2019-2024海上风电项目')
turbineCosts['year'] = turbineCosts['季度'].apply(lambda x: int(x[:4]))
turbineCosts = turbineCosts[['year', '是否含塔筒', '金额（元/kW）']]
turbineCosts['$/kW'] = turbineCosts['金额（元/kW）'] * 0.14

#%%
turbineCostsMod = InvMid[['年份', '整机成本', '塔筒成本']].drop_duplicates()
turbineCostsMod['无塔筒'] = turbineCostsMod['整机成本'] * 0.14
turbineCostsMod['有塔筒'] = (turbineCostsMod['整机成本'] + turbineCostsMod['塔筒成本']) * 0.14

#%%
# monopile and jacket cost
foundationCosts = pd.read_excel('../data/cost/SI_key_parameters.xlsx', 'A2.2 固定式桩基成本实证分析').loc[0:21, ['类型', '单机容量 (MW)', '桩基用量(t)']]
foundationCosts['Costs'] = foundationCosts['桩基用量(t)'] / foundationCosts['单机容量 (MW)'] * 8.8 * 0.14

#%%
foundationCostsMod = InvMid.loc[(InvMid.年份.isin([2020, 2021, 2022])) & (InvMid.基础选择 != '漂浮式'), ['年份', '导管架基础成本', '单桩基础成本', '基础选择']].drop_duplicates()
foundationCostsMod[['导管架基础成本', '单桩基础成本']] *= 0.14
foundationCostsMod

#%%
# floating offshore wind cost
floatingCostsMod = InvMid.loc[(InvMid.年份.isin([2021, 2022, 2023, 2025, 2027])) & (InvMid.基础选择 == '漂浮式'), ['年份', '单位投资额']].drop_duplicates()
floatingCostsMod['$/kW'] = floatingCostsMod['单位投资额'] * 0.14

#%%
floatingCosts = pd.read_excel('../data/cost/SI_key_parameters.xlsx', 'A3 中国海上风电成本现状').loc[0:4, ['投产年份', '单位kW投资（万元/kW）']]
floatingCosts['$/kW'] = floatingCosts['单位kW投资（万元/kW）'] * 0.14 * 10000
#%%
# turbine (excl. tower)
turbineCostsNo = turbineCosts[turbineCosts.是否含塔筒 != 'With']
turbineCostsNo.year += 1
fig = plt.figure(figsize=(14, 10))
axes = []
from matplotlib.gridspec import GridSpec
gs = GridSpec(2, 12)
axes.append(fig.add_subplot(gs[0, 0:6]))
axes.append(fig.add_subplot(gs[0, 6:12]))
axes.append(fig.add_subplot(gs[1, 0:3]))
axes.append(fig.add_subplot(gs[1, 3:6]))
axes.append(fig.add_subplot(gs[1, 6:12]))

sns.boxplot(turbineCostsNo, x='year', y='$/kW', ax=axes[0], fill=False, color='#1f77b4')
axes[0].plot([0, 1, 2, 3, 4], turbineCostsMod.无塔筒.values[:5], marker='s', c='#ff7f0e', zorder=10, label = 'Datasets')
axes[0].plot([0, 1, 2, 3, 4], -1 * turbineCostsMod.无塔筒.values[[0, 1, 2, 3, 5]], marker='s', c='#1f77b4', zorder=10, label = 'Projects')
axes[0].set_ylabel('$/kW')
axes[0].set_title('a)', loc='left', y=1, fontsize=16)
axes[0].set_ylim(300, 1200)
axes[0].legend(frameon=False)
# turbine (incl. tower)
turbineCostsNo = turbineCosts[turbineCosts.是否含塔筒 == 'With']
turbineCostsNo.year += 1
sns.boxplot(turbineCostsNo, x='year', y='$/kW', ax=axes[1], fill=False, color='#1f77b4')
axes[1].plot(turbineCostsMod.年份.values[1:6] - 2021, turbineCostsMod.有塔筒.values[1:6], marker='s', c='#ff7f0e', zorder=10, label = 'Datasets')
axes[1].set_title('b)', loc='left', y=1, fontsize=16)
axes[1].set_ylim(300, 1200)

monopileCosts_proj = foundationCosts.loc[0:12, ['Costs']]
monopileCosts_proj['type'] = 'Projects'
monopileCosts_data = foundationCostsMod[['单桩基础成本']].rename(columns={'单桩基础成本': 'Costs'})
monopileCosts_data['type'] = 'Datasets'
monopileCosts = pd.concat([monopileCosts_data, monopileCosts_proj], axis=0)
monopileCosts = pd.DataFrame(monopileCosts)
sns.boxplot(monopileCosts, x='type', y='Costs', ax=axes[2], fill=False, palette = ['#ff7f0e', '#1f77b4'], width=0.5)
axes[2].set_ylim(150, 700)
axes[2].set_ylabel('$/kW')
axes[2].set_title('c)', loc='left', y=1, fontsize=16)

monopileCosts_proj = foundationCosts.loc[13:21, ['Costs']]
monopileCosts_proj['type'] = 'Projects'
monopileCosts_data = foundationCostsMod[['导管架基础成本']].rename(columns={'导管架基础成本': 'Costs'})
monopileCosts_data['type'] = 'Datasets'
monopileCosts = pd.concat([monopileCosts_data, monopileCosts_proj], axis=0)
monopileCosts
monopileCosts = pd.DataFrame(monopileCosts)
sns.boxplot(monopileCosts, x='type', y='Costs', ax=axes[3], fill=False, palette = ['#ff7f0e', '#1f77b4'], width=0.5)
axes[3].set_ylim(150, 700)
axes[3].set_ylabel('$/kW')
axes[3].set_title('d)', loc='left', y=1, fontsize=16)
sns.boxplot(floatingCostsMod, x='年份', y='$/kW', ax=axes[4], fill=False, color='#ff7f0e')
axes[4].plot([0, 1, 2, 3, 4], floatingCosts['$/kW'].values, marker='s', c='#1f77b4', zorder=10, label = 'Projects')
axes[4].set_xlabel('year')
plt.tight_layout()
axes[4].set_title('e)', loc='left', y=1, fontsize=16)
plt.savefig('../figures/tech_validation.png', dpi=400, bbox_inches = 'tight',pad_inches = 0.2)
