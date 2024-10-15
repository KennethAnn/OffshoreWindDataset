#%%
# collect TIFFs data
import pandas as pd
import numpy as np

#%%
# Average capacity factor data
CF_Mid_Average = pd.read_csv('../data/power_output/CF_Mid_Average.csv')
CF_Mid_Average['pointid'] = CF_Mid_Average.id.apply(lambda x: int(x.split('.')[0][1:]))
CF_Mid_Average['year'] = CF_Mid_Average.id.apply(lambda x: int(x.split('.')[1]))
CF_Mid_Average = CF_Mid_Average[['pointid', 'year', 'CF_Mid']]
CF_Low_Average = pd.read_csv('../data/power_output/CF_Low_Average.csv')
CF_Low_Average['pointid'] = CF_Low_Average.id.apply(lambda x: int(x.split('.')[0][1:]))
CF_Low_Average['year'] = CF_Low_Average.id.apply(lambda x: int(x.split('.')[1]))
CF_Low_Average = CF_Low_Average[['pointid', 'year', 'CF_Low']]
CF_High_Average = pd.read_csv('../data/power_output/CF_High_Average.csv')
CF_High_Average['pointid'] = CF_High_Average.id.apply(lambda x: int(x.split('.')[0][1:]))
CF_High_Average['year'] = CF_High_Average.id.apply(lambda x: int(x.split('.')[1]))
CF_High_Average = CF_High_Average[['pointid', 'year', 'CF_High']]
CF_Average = CF_Low_Average.merge(CF_Mid_Average, on=['pointid', 'year'], how='left')
CF_Average = CF_Average.merge(CF_High_Average, on=['pointid', 'year'], how='left')
CF_Average = CF_Average[CF_Average.year.isin([2020, 2025, 2030, 2035])]
CF_Average_pvt = CF_Average.pivot_table(index='pointid', columns='year')
names_tp = CF_Average_pvt.columns
CF_Average_pvt.columns = [i[0] + str(i[1]) for i in names_tp]
CF_Average_pvt = CF_Average_pvt[['CF_Mid2020', 'CF_Mid2025', 'CF_Mid2030', 'CF_Mid2035', 'CF_High2035', 'CF_Low2035']].rename(columns={'CF_Mid2020': 'CF2020'})

#%%
# investment costs
InvMid = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '中速技术进步情景')
InvHigh = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '高速技术进步情景')
InvLow = pd.read_excel('../data/cost/SI_key_parameters.xlsx', '低速技术进步情景')

Data_Inv = pd.DataFrame()
for yr in [2020, 2025, 2030, 2035]:
    Inv_yr = InvMid.loc[InvMid.年份 == yr, ['ID', '经度', '维度', '单位投资额', '基础选择']].rename(columns={'单位投资额': 'Inv_Mid' + str(yr), '基础选择': 'BaseMid' + str(yr)})
    if Data_Inv.empty:
        Data_Inv = Inv_yr
    else:
        Data_Inv = Data_Inv.merge(Inv_yr, on=['ID', '经度', '维度'], how='left')
for yr in [2020, 2025, 2030, 2035]:
    Inv_yr = InvHigh.loc[InvHigh.年份 == yr, ['ID', '经度', '维度', '单位投资额', '基础选择']].rename(columns={'单位投资额': 'Inv_High' + str(yr), '基础选择': 'BaseHigh' + str(yr)})
    if Data_Inv.empty: 
        Data_Inv = Inv_yr
    else:
        Data_Inv = Data_Inv.merge(Inv_yr, on=['ID', '经度', '维度'], how='left')
for yr in [2020, 2025, 2030, 2035]:
    Inv_yr = InvLow.loc[InvLow.年份 == yr, ['ID', '经度', '维度', '单位投资额', '基础选择']].rename(columns={'单位投资额': 'Inv_Low' + str(yr), '基础选择': 'BaseLow' + str(yr)})
    if Data_Inv.empty:
        Data_Inv = Inv_yr
    else:
        Data_Inv = Data_Inv.merge(Inv_yr, on=['ID', '经度', '维度'], how='left')
Data_Inv_pvt = Data_Inv[['ID', 'Inv_Mid2020', 'Inv_Mid2025', 'Inv_Mid2030', 'Inv_Mid2035', 'Inv_High2035', 'Inv_Low2035']].rename(columns={'Inv_Mid2020': 'Inv2020'}).set_index('ID') * 0.14

#%%
r = 0.08 # discount rate
T = 25 # lifetime
InvMid['scn'] = 'LCOE_Mid'
InvHigh['scn'] = 'LCOE_High'
InvLow['scn'] = 'LCOE_Low'
InvData = pd.concat([InvMid, InvHigh, InvLow], axis=0)
CostData = InvData.loc[InvData['年份'].isin([2020, 2025, 2030, 2035]), ['scn', 'ID', '年份', '单位投资额', '年运维成本', '容量因子']]
CostData['LCOE'] = CostData.T.apply(lambda row: (row.单位投资额 + sum(row.年运维成本 * (1 + r) ** (-t) for t in range(1, T+1))) / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))
CostData = CostData[['ID', 'scn', '年份', 'LCOE']]
CostData_pvt = CostData.pivot_table(index='ID', columns=['scn', '年份'], values='LCOE')
names_tp = CostData_pvt.columns
CostData_pvt.columns = [i[0] + str(i[1]) for i in names_tp]
CostData_pvt = CostData_pvt[['LCOE_Mid2020', 'LCOE_Mid2025', 'LCOE_Mid2030', 'LCOE_Mid2035', 'LCOE_High2035', 'LCOE_Low2035']].rename(columns={'LCOE_Mid2020': 'LCOE2020'}) * 0.14
CostData_pvt

#%%
tiffs_data = pd.concat([CF_Average_pvt, Data_Inv_pvt, CostData_pvt], axis=1).reset_index().rename(columns={'index': 'pointid'})
points = pd.read_csv('../cost/points_capital_costs.csv')
points = points[['pointid', 'lon', 'lat']]
points = points.merge(tiffs_data, on='pointid', how='left')
points.to_csv('./tiffs_data/tiffs_data.csv')