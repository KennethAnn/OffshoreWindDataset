#%%
# make 3 NetCDF files from 2020 to 2035
import pandas as pd
import numpy as np
import netCDF4 as nc

#%%
dict_scn = {
    'Medium': '中速技术进步情景',
    'High': '高速技术进步情景',
    'Low': '低速技术进步情景'
}


# dict of all variables
dict_vars = {
    # '年份': {'name': 'time', 'type': np.int32, 'unit': 'year'},
    '省份': {'name': 'province', 'type': 'S20', 'unit': 'no'},
    # '经度': {'name': 'longitude', 'type': np.float32, 'unit': 'degrees_east'},
    # '维度': {'name': 'latitude', 'type': np.float32, 'unit': 'degrees_north'},
    '水深(m)': {'name': 'water depth', 'type': np.float32, 'unit': 'm'},
    '离岸距离(km)': {'name': 'offshore distance', 'type': np.float32, 'unit': 'km'},
    '单机容量（MW）': {'name': 'rated power', 'type': np.float32, 'unit': 'MW'},
    '叶片直径（m）': {'name': 'rotor diamater', 'type': np.float32, 'unit': 'm'},
    '轮毂高度（m）': {'name': 'hub height', 'type': np.float32, 'unit': 'm'},
    '单位机头重量（t/MW）': {'name': 'nacelle weight', 'type': np.float32, 'unit': 't/MW'},
    '开发成本': {'name': 'development cost', 'type': np.float32, 'unit': '$/kW'},
    '征海费用': {'name': 'marine use cost', 'type': np.float32, 'unit': '$/kW'},
    '整机成本': {'name': 'turbine cost', 'type': np.float32, 'unit': '$/kW'},
    '塔筒成本': {'name': 'tower cost', 'type': np.float32, 'unit': '$/kW'},
    '基础选择英文': {'name': 'foundation type', 'type': 'S20', 'unit': 'no'},
    '基础成本': {'name': 'foundation cost', 'type': np.float32, 'unit': '$/kW'},
    '系泊锚固成本': {'name': 'mooring&anchor cost', 'type': np.float32, 'unit': '$/kW'},
    '输电选择': {'name': 'transmission type', 'type': 'S20', 'unit': 'no'},
    '输电成本': {'name': 'transmission cost', 'type': np.float32, 'unit': '$/kW'},
    '安装成本': {'name': 'installation cost', 'type': np.float32, 'unit': '$/kW'},
    '年运维成本': {'name': 'annual O&M cost', 'type': np.float32, 'unit': '$/kW'},
    '容量因子': {'name': 'capacity factor', 'type': np.float32, 'unit': '%'},
    'LCOE': {'name': 'LCOE', 'type': np.float32, 'unit': '$/MWh'},
    'CAPEX': {'name': 'CAPEX', 'type': np.float32, 'unit': '$/MWh'},
    'OPEX': {'name': 'OPEX', 'type': np.float32, 'unit': '$/MWh'},
}

#%%
def get_installation_cost(row):
    if row.基础选择 == '单桩':
        return row.单桩安装成本
    elif row.基础选择 == '导管架':
        return row.导管架安装成本
    elif row.基础选择 == '漂浮式':
        return row.漂浮式安装成本
def get_foundation_cost(row):
    if row.基础选择 == '单桩':
        return row.单桩基础成本
    elif row.基础选择 == '导管架':
        return row.导管架基础成本
    elif row.基础选择 == '漂浮式':
        return row.漂浮式基础成本
def get_foundation_type(row):
    if row.基础选择 == '单桩':
        return 'monopile'
    elif row.基础选择 == '导管架':
        return 'jacket'
    elif row.基础选择 == '漂浮式':
        return 'floating'
def get_transmission_cost(row):
    if row.输电选择 == 'HVAC':
        return row.HVAC成本
    elif row.基础选择 == 'HVDC':
        return row.HVDC成本

#%%
scns = ['Medium', 'High', 'Low']
for scn in scns:
    # 制作中等技术进步情景的数据
    InvData = pd.read_excel('../data/cost/SI_key_parameters.xlsx', dict_scn[scn])
    r = 0.08 # discount rate
    T = 25 # lifetime
    
    CostData = InvData.copy(deep=True)
    CostData['LCOE'] = CostData.T.apply(lambda row: (row.单位投资额 + sum(row.年运维成本 * (1 + r) ** (-t) for t in range(1, T+1))) / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))
    CostData['CAPEX'] = CostData.T.apply(lambda row: row.单位投资额 / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))
    CostData['OPEX'] = CostData.T.apply(lambda row: sum(row.年运维成本 * (1 + r) ** (-t) for t in range(1, T+1)) / sum(row.容量因子 * (1 + r) ** (-t) for t in range(1, T+1)))

    CostData['基础成本'] = CostData.T.apply(lambda row: get_foundation_cost(row))
    CostData['安装成本'] = CostData.T.apply(lambda row: get_installation_cost(row))
    CostData['基础选择英文'] = CostData.T.apply(lambda row: get_foundation_type(row))
    CostData['输电成本'] = CostData.T.apply(lambda row: get_transmission_cost(row))

    unique_years = InvData['年份'].unique()
    unique_ID = InvData['ID'].unique()

    # 创建netCDF文件
    nc_file = nc.Dataset('../data/nc/CF_Inv_LCOE_%s.nc' %scn, 'w', format='NETCDF4')

    # 创建维度
    nc_file.createDimension('time', len(unique_years)) # 年份
    nc_file.createDimension('points', len(unique_ID))

    # 创建经纬度变量
    lon_var = nc_file.createVariable('longitude', np.float32, ('time', 'points'))
    lat_var = nc_file.createVariable('latitude', np.float32, ('time', 'points'))
    time_var = nc_file.createVariable('time', np.int32, ('time',))

    # 添加单位
    lon_var.units = 'degrees_east'
    lat_var.units = 'degrees_north'
    time_var.units = 'year'

    # 创建其它变量
    for var_id in dict_vars.keys():
        var_name = dict_vars[var_id]['name']
        var_type = dict_vars[var_id]['type']
        var_unit = dict_vars[var_id]['unit']
        var = nc_file.createVariable(var_name, var_type, ('time', 'points'))
        var.units = str(var_unit)
        print(var_name, var_type, var_unit)
    # 填充变量数据
    for i, year in enumerate(unique_years):
        yearly_data = CostData[CostData['年份'] == year]
        
        #填充经纬度和时间数据
        lon_var[i, :] = yearly_data['经度'].values
        lat_var[i, :] = yearly_data['维度'].values
        time_var[i] = year

        # 填充其它变量
        for var_id in dict_vars.keys():
            if var_id in ['开发成本', '征海费用', '整机成本', '塔筒成本', '基础成本', '系泊锚固成本', '输电成本', '安装成本', '年运维成本']:
                nc_file.variables[dict_vars[var_id]['name']][i, :] = yearly_data[var_id].values * 0.14
            elif var_id in ['LCOE', 'CAPEX', 'OPEX']:
                nc_file.variables[dict_vars[var_id]['name']][i, :] = yearly_data[var_id].values * 140
            elif var_id == '容量因子':
                nc_file.variables[dict_vars[var_id]['name']][i, :] = yearly_data[var_id].values / 8760 * 100
            else:
                nc_file.variables[dict_vars[var_id]['name']][i, :] = yearly_data[var_id].values
    nc_file.close()