#%%
# make hourly output data files of 2020
import pandas as pd
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
#%%
file_path  = '' # using VMF model to project the outputs
cf_mid = pd.read_csv(file_path)
hours = pd.read_csv('')[['Timestamp']] # using VMF model, windspeed.csv
#%%
#Timestamp, change to +8 UTC
columns2020 = [i for i in cf_mid.columns if i.split('.')[1] == '2020']
cf_mid2020 = cf_mid[columns2020]
cf_mid2020 = pd.concat([hours, cf_mid2020], axis=1).set_index('Timestamp')
cf_mid2020_8 = cf_mid2020.iloc[-8:, :]
cf_mid2020_lag = cf_mid2020.shift(8)
cf_mid2020_lag.iloc[0:8] = cf_mid2020_8.iloc[-8:]
cf_mid2020_lag = cf_mid2020_lag.reset_index().melt(id_vars='Timestamp',var_name='ID', value_name='CF')
cf_mid2020_lag['pointid'] = cf_mid2020_lag.ID.apply(lambda x: int(x.split('.')[0][1:]))
cf_mid2020_lag

#%%
points = pd.read_csv('../data/points/points.csv')
points = points[['pointid', 'lon', 'lat']]
points = points.merge(cf_mid2020_lag, on='pointid', how='right')
points['Timestamp'] = pd.to_datetime(points['Timestamp'])
points

#%%

nc_file = nc.Dataset('../data/hourly/Hourly_outputs_2020.nc', 'w', format='NETCDF4')
unique_time = points.Timestamp.unique()
unique_ID = points.pointid.unique()
# 创建维度
nc_file.createDimension('time', len(unique_time)) # 年份
nc_file.createDimension('points', len(unique_ID))
# 创建经纬度变量
lon_var = nc_file.createVariable('longitude', np.float32, ('time', 'points'))
lat_var = nc_file.createVariable('latitude', np.float32, ('time', 'points'))
time_var = nc_file.createVariable('time', np.float64, ('time',))
cf_var = nc_file.createVariable('capacity factor', np.float32, ('time', 'points'))

# 添加单位
lon_var.units = 'degrees_east'
lat_var.units = 'degrees_north'
time_var.units = 'hours since 2020-01-01 00:00:00 +08:00'
cf_var.units = '%'
start_time = pd.Timestamp('2020-01-01 00:00:00')
# 填充变量数据
for i, t in enumerate(unique_time):
    print(t)
    t_data = points[points['Timestamp'] == t]
    #填充经纬度和时间数据
    lon_var[i, :] = t_data['lon'].values
    lat_var[i, :] = t_data['lat'].values
    time_var[i] = (t - start_time).total_seconds() / 3600 
    cf_var[i, :] = t_data['CF'].values * 100
nc_file.close()