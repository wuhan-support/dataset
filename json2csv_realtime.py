import json
import time
import os
import datetime
import pandas as pd

def timechange(timestamp):
    timestamp=timestamp.split('.')[0]+timestamp.split('.')[1]
    timestamp=int(timestamp[0:13])
    # 转换成localtime
    time_local = time.localtime(timestamp / 1000)
    # 转换成新的时间格式(精确到秒)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def save_csv_area(filename):
    f = open("jsons/%s"%filename,'r',encoding='utf-8')
    for line in f.readlines():
        dic=json.loads(line)
        Area = dic[ 'data' ]['listByArea']
        city=[]
        for i in Area:
            for j in i['cities']:
                dict = {}
                dict[ 'provinceName' ] = i[ 'provinceName' ]
                dict[ 'provinceAbbreviation' ] = i[ 'provinceShortName' ]
                dict[ 'city']= j['cityName']
                dict[ 'confirmed']=j['confirmed']
                dict[ 'suspected']=j['suspected']
                dict[ 'cured']=j['cured']
                dict[ 'dead']=j['dead']
                city.append(dict)

        pd.DataFrame(city).to_csv('csvs/real_time.csv',index=0)

if __name__ == '__main__':
    list=[]
    for i in os.listdir('jsons/'):
        if i.split('.')[ 0]!='latest':
            if i.split('.')[ 1 ]!='json':
                timestamp = float(i.split('.')[ 0 ]+'.'+i.split('.')[ 1 ])
                list.append(timestamp)
    a=max(list)
    realtime_name=str(a)+'.json'
    save_csv_area(realtime_name)
    