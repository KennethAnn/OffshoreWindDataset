#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rc('font',family='Arial',size=14)
#%%
# Capacity Potential
capacity_pot = pd.read_excel('../data/params/validation_data.xlsx', 'CapacityPotential')
capacity_pot.Dataset.corr(capacity_pot['Wang et al., 2022'])

#%%
#  Capacity Factor, compared to global wind atlas
cf_data = pd.read_excel('../data/params/capacity_factor_datasets_atlas.xls')

#%%
# 图3：与现有研究的预测相比较
InvMid = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '中速技术进步情景')
InvData = InvMid.copy(deep=True).rename(columns={'年份': 'year'})
InvData['LCOE'] *= 140
InvData = InvData[InvData.year.isin([2020, 2025, 2030, 2035])]
InvFixed = InvData.loc[InvData.基础选择 != '漂浮式', ['year', 'LCOE']]
InvFixed['Mod'] = 'Dataset'
InvFloating = InvData.loc[InvData.基础选择 == '漂浮式', ['year', 'LCOE']]
InvFloating['Mod'] = 'Dataset'
InvFixed

proj_fixed = pd.read_excel('../data/params/validation_data.xlsx', 'ProjectionCost', skiprows=1)
proj_fixed = proj_fixed[proj_fixed.type == 'b. Fixed-Bottom Offshore']
proj_fixed = proj_fixed.pivot_table(index='year', columns='region', values = ['median', 'p25', 'p75'])
proj_fixed.loc[2020, :] = np.nan
proj_fixed.loc[2030, :] = np.nan
proj_fixed = proj_fixed.sort_index()
proj_fixed = proj_fixed.interpolate(method='linear')
proj_fixed = proj_fixed.loc[[2020, 2025, 2030, 2035]].reset_index()
proj_fixed = proj_fixed.melt(id_vars='year', value_name='LCOE', var_name='Mod')
proj_fixed['Mod'] = 'Wiser et al., 2021'

proj_floating = pd.read_excel('../data/params/validation_data.xlsx', 'ProjectionCost', skiprows=1)
proj_floating = proj_floating[proj_floating.type == 'c. Floating Offshore']
proj_floating = proj_floating.pivot_table(index='year', columns='region', values = ['median', 'p25', 'p75'])
proj_floating.loc[2030, :] = np.nan
proj_floating = proj_floating.sort_index()
proj_floating = proj_floating.interpolate(method='linear')
proj_floating = proj_floating.loc[[2025, 2030, 2035]].reset_index()
proj_floating = proj_floating.melt(id_vars='year', value_name='LCOE', var_name='Mod')
proj_floating['Mod'] = 'Wiser et al., 2021'
proj_floating
fixedData = pd.concat([InvFixed, proj_fixed], axis=0)
floatingData = pd.concat([InvFloating, proj_floating], axis=0)
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes = axes.flatten()
axes[0].scatter(capacity_pot.Dataset.values, capacity_pot['Wang et al., 2022'].values, s=60, marker='s', color='#ff7f0e')
axes[0].plot(range(0, 800), range(0, 800), linewidth=4, color='#1f77b4', linestyle='--')
axes[0].set_xlabel('Datasets(GW)')
axes[0].set_ylabel('Wang et al., 2022(GW)')
axes[0].set_title('a)', loc='left', y=1, fontsize=16)
axes[1].scatter(cf_data.CapacityFactor_2020_tif.values, cf_data.wind_potential_Band_1.values * 100, s=60, marker='s', color='#ff7f0e')
axes[1].plot(range(25, 75), range(25, 75), linewidth=4, color='#1f77b4', linestyle='--')
axes[1].set_xlabel('Datasets(%)')
axes[1].set_ylabel('WindAtlas(%)')
axes[1].set_title('b)', loc='left', y=1, fontsize=16)
sns.boxplot(fixedData, x='year', y='LCOE', hue='Mod', ax=axes[2],palette = ['#ff7f0e', '#1f77b4'],fill=False)
axes[2].set_title('c)', loc='left', y=1, fontsize=16)
axes[2].legend(frameon=False)
sns.boxplot(floatingData, x='year', y='LCOE', hue='Mod', ax=axes[3], palette = ['#ff7f0e', '#1f77b4'],fill=False)
axes[3].set_title('d)', loc='left', y=1, fontsize=16)
axes[3].legend(frameon=False)
plt.savefig('../figures/literature_validation.png', dpi=400, bbox_inches = 'tight',pad_inches = 0.2)
