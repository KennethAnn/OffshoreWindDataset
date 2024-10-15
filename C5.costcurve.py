#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rc('font',family='Arial',size=14)

#%%
CostData = pd.read_csv('../data/cost/CostData_LCOE.csv')
points = pd.read_csv('../data/points/points.csv')
points = points[['pointid', 'Province']].rename(columns={'pointid': 'ID'})
CostData = CostData.merge(points, on='ID', how='left')
prov_coalcost = pd.read_csv('../data/params/prov_coalcost.csv')
CostData = CostData.merge(prov_coalcost, on = 'Province', how='left')
CostData['LCOE'] *= 140
CostData['CoalCost'] *= 140
CostData['potential'] = 0.6 # GW
CostData['potential_gen'] = 0.6 * CostData['容量因子'] / 1000 # TWh
CostData
#%%
CostDataAgg = CostData.groupby(['scn', '年份', 'Province'])['potential_gen'].sum().reset_index()
CostDataAgg = CostDataAgg.pivot_table(values='potential_gen', index=['scn', '年份'], columns='Province')
#%%
# plot by provinces
fig, axes = plt.subplots(2, 5, figsize=(20, 10))
axes = axes.T.flatten()
bottoms = []
dict_colors = {
    1: '#d84018',
    2: '#9c58ce',
    3: '#0085e1',
    4: '#6497a8',
    5: '#ae98b6',
    6: '#6c9ac0',
    7: '#f2c69c',
    8: '#9dc2de',
}
provinces = ['Fujian','Guangdong','Guangxi','Hainan','Hebei','Jiangsu','Liaoning','Shandong','Shanghai','Zhejiang']
titles = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)', 'j)']
i_prov = 0
for prov in provinces:
    CostData_prov = CostData[CostData.Province == prov]
    # cost curve by generation
    # 2020
    CostScn = CostData_prov.loc[(CostData_prov.年份==2020) & (CostData_prov.scn =='Mid'), ['ID', 'Province', 'LCOE', 'CoalCost', 'potential_gen']]
    CostScn = CostScn.sort_values('LCOE')
    CostScn['cum_potential_gen'] = CostScn.potential_gen.cumsum()
    axes[i_prov].plot(CostScn.cum_potential_gen.values, CostScn.LCOE.values, linewidth=3, color=dict_colors[1], label = '2020')
    # Mid 2025
    CostScn = CostData_prov.loc[(CostData_prov.年份==2025) & (CostData_prov.scn =='Mid'), ['ID', 'Province', 'LCOE', 'CoalCost', 'potential_gen']]
    CostScn = CostScn.sort_values('LCOE')
    CostScn['cum_potential_gen'] = CostScn.potential_gen.cumsum()
    axes[i_prov].plot(CostScn.cum_potential_gen.values, CostScn.LCOE.values, linewidth=3, color=dict_colors[2], label='Mid 2025')
    # Mid 2035
    CostScn = CostData_prov.loc[(CostData_prov.年份==2035) & (CostData_prov.scn =='Mid'), ['ID', 'Province', 'LCOE', 'CoalCost', 'potential_gen']]
    CostScn = CostScn.sort_values('LCOE')
    CostScn['cum_potential_gen'] = CostScn.potential_gen.cumsum()
    axes[i_prov].plot(CostScn.cum_potential_gen.values, CostScn.LCOE.values, linewidth=3, color=dict_colors[3], label='Mid 2035')
    axes[i_prov].plot(CostScn.cum_potential_gen.values, CostScn.CoalCost.values, linewidth=3, color='black', linestyle = '--', label='Coal Power')
    axes[i_prov].set_ylim(0, 100)
    axes[i_prov].set_xlabel('TWh')
    axes[i_prov].set_ylabel('$/MWh')
    axes[i_prov].set_title(titles[i_prov] + ' ' + prov, loc='left', y=1, fontsize=14)
    i_prov += 1
axes[i_prov-1].legend(frameon=False)
plt.tight_layout()
plt.savefig('../figures/costcurve_prov.png', dpi=400, bbox_inches = 'tight',pad_inches = 0.2)