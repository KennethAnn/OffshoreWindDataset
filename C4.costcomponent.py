#%%
import pandas as pd
import numpy as np
#%%
InvMid = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '中速技术进步情景')
InvHigh = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '高速技术进步情景')
InvLow = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '低速技术进步情景')
InvMid['scn'] = 'Mid'
InvHigh['scn'] = 'High'
InvLow['scn'] = 'Low'
InvData = pd.concat([InvMid, InvHigh, InvLow], axis=0)
CostData = InvData[['scn', 'ID', '年份', '单位投资额', '年运维成本', '容量因子']]
r = 0.08 # discount rate
T = 25 # lifetime
CostData['LCOE'] = CostData.T.apply(lambda row: (row.单位投资额 + sum(row.年运维成本 * (1 + r) ** (-t) for t in range(1, T+1))) / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))
CostData['CAPEX'] = CostData.T.apply(lambda row: row.单位投资额 / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))
CostData['OPEX'] = CostData.T.apply(lambda row: sum(row.年运维成本 * (1 + r) ** (-t) for t in range(1, T+1)) / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))
CostData.to_csv('../data/cost/CostData_LCOE.csv', index=False)
#%%
# data of point A，Pointid=1483
CostDataA = CostData.loc[(CostData.ID == 1483) & (CostData.年份.isin([2020, 2025, 2030, 2035])), ['scn', '年份', 'CAPEX', 'OPEX']]
# investment cost
InvDataA = InvData[(InvData.ID == 1483) & (InvData.年份.isin([2020, 2025, 2030, 2035]))]
CapexType = ['Dev', 'Marine use', 'Turbine', 'Tower', 'Foundation', 'Mooring&Anchor', 'Transmission', 'Installation']
CostType = CapexType + ['OPEX']
Dict_Capex = dict(zip(['开发成本', '征海费用',  '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本', 'OPEX'], CapexType))
InvDataA['基础成本'] = InvDataA.T.apply(lambda row: row.单桩基础成本 if row.基础选择 == '单桩' else row.导管架基础成本)
InvDataA['输电成本'] = InvDataA.T.apply(lambda row: row.HVAC成本 if row.输电选择 == 'HVAC' else row.HVDC成本)
InvDataA['安装成本'] = InvDataA.T.apply(lambda row: row.单桩安装成本 if row.基础选择 == '单桩' else row.导管架安装成本)
InvDataA = InvDataA[['scn', '年份', '开发成本', '征海费用',  '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本', '单位投资额']]
InvDataA.index = range(0, len(InvDataA.index))
CostDataA = CostDataA.merge(InvDataA, on=['scn', '年份'], how='left')
for type in ['开发成本', '征海费用',  '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本']:
    CostDataA[Dict_Capex[type]] = CostDataA[type] / CostDataA['单位投资额'] * CostDataA['CAPEX']
CostDataA['OPEX'] = CostDataA['OPEX']
CostDataA['Mooring&Anchor'] = 0
CostDataA['scns'] = CostDataA['scn'] + CostDataA['年份'].astype(str)
CostDataA = CostDataA[['scns'] + CostType]
CostDataA = CostDataA.replace('Mid2020', '2020').set_index('scns')
CostDataA = CostDataA.loc[(CostDataA.index != 'High2020') & (CostDataA.index != 'Low2020')]
CostDataA = CostDataA * 140 # $/MWh

#%%
# data of point B, Pointid=4224
CostDataB = CostData.loc[(CostData.ID == 4224) & (CostData.年份.isin([2020, 2025, 2030, 2035])), ['scn', '年份', 'CAPEX', 'OPEX']]
# investment cost
InvDataB = InvData[(InvData.ID == 4224) & (InvData.年份.isin([2020, 2025, 2030, 2035]))]
CapexType = ['Dev', 'Marine use', 'Turbine', 'Tower', 'Foundation', 'Mooring&Anchor', 'Transmission', 'Installation']
CostType = CapexType + ['OPEX']
Dict_Capex = dict(zip(['开发成本', '征海费用',  '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本', 'OPEX'], CapexType))
InvDataB['基础成本'] = InvDataB['漂浮式基础成本']
InvDataB['输电成本'] = InvDataB.T.apply(lambda row: row.HVAC成本 if row.输电选择 == 'HVAC' else row.HVDC成本)
InvDataB['安装成本'] = InvDataB['漂浮式安装成本']
InvDataB = InvDataB[['scn', '年份', '开发成本', '征海费用',  '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本', '单位投资额']]
InvDataB.index = range(0, len(InvDataB.index))
CostDataB = CostDataB.merge(InvDataB, on=['scn', '年份'], how='left')
for type in ['开发成本', '征海费用',  '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本']:
    CostDataB[Dict_Capex[type]] = CostDataB[type] / CostDataB['单位投资额'] * CostDataB['CAPEX']
CostDataB['OPEX'] = CostDataB['OPEX']
CostDataB['scns'] = CostDataB['scn'] + CostDataB['年份'].astype(str)
CostDataB = CostDataB[['scns'] + CostType]
CostDataB = CostDataB.replace('Mid2020', '2020').set_index('scns')
CostDataB = CostDataB.loc[(CostDataB.index != 'High2020') & (CostDataB.index != 'Low2020')]
CostDataB = CostDataB * 140 # $/MWh

#%%
import matplotlib.pyplot as plt
plt.rc('font',family='Arial',size=14)
dict_colors_for_capac = {
    'Dev': '#4C5561',
    'Marine use': '#f39a8f',
    'Turbine': '#9b8063',
    'Tower': '#6497a8',
    'Foundation':'#ae98b6',
    'Mooring&Anchor': '#6c9ac0',
    'Transmission': '#f2c69c',
    'Installation': '#9dc2de',
    'OPEX': '#98c39a',
}
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
axes = axes.T.flatten()
bottoms = []
for i, g in enumerate(CostDataA.columns):
    bottom = CostDataA.iloc[:,:i].sum(axis=1)
    axes[0].bar(CostDataA.index, CostDataA.iloc[:, i], bottom = bottom, color=dict_colors_for_capac[g], label=g, width=0.8)
axes[0].set_xticks(CostDataA.index)
axes[0].set_xticklabels(CostDataA.index, rotation=30)
axes[0].set_xlabel('Scenarios')
axes[0].set_ylabel('LCOE($/MWh)')
axes[0].set_ylim(0, 80)
bottoms = []
for i, g in enumerate(CostDataB.columns):
    bottom = CostDataB.iloc[:,:i].sum(axis=1)
    axes[1].bar(CostDataB.index, CostDataB.iloc[:, i], bottom = bottom, color=dict_colors_for_capac[g], label=g, width=0.8)
axes[1].set_xticks(CostDataB.index)
axes[1].set_xticklabels(CostDataB.index, rotation=30)
axes[1].set_ylim(0, 160)
axes[1].set_xlabel('Scenarios')
axes[1].legend(ncol=1, bbox_to_anchor=(1., 1), frameon=True, fancybox=False, edgecolor='black', columnspacing=0.8)
plt.tight_layout()
plt.savefig('../figures/lcoe_dyn.png', dpi=400, bbox_inches = 'tight',pad_inches = 0.2)