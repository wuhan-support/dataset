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

    time=timechange(filename)
    for line in f.readlines():
        dic=json.loads(line)
        try:
            Area = dic[ 'data' ]['areaList']
        except:
            Area = dic[ 'data' ][ 'listByArea']
        city=[]
        for i in Area:
            for j in i['cities']:
                dict = {}
                dict[ 'provinceName' ] = i[ 'provinceName' ]
                dict[ 'provinceAbbreviation' ] = i[ 'provinceShortName' ]
                dict[ 'city']= j['cityName']
                try:
                    dict[ 'confirmed' ] = j[ 'confirmed' ]
                    dict[ 'suspected' ] = j[ 'suspected' ]
                    dict[ 'cured']=j['cured']
                    dict[ 'dead']=j['dead']

                except:
                    dict[ 'confirmed']=j['confirmedCount']
                    dict[ 'suspected']=j['suspectedCount']
                    dict[ 'cured']=j['curedCount']
                    dict[ 'dead']=j['deadCount']
                city.append(dict)

        pd.DataFrame(city).to_csv('history/city_%s.csv'%time,index=0)

if __name__ == '__main__':
    list=[]
    for i in os.listdir('history/'):
        a=i.split('_')[ 1 ]
        list.append(a.split('.')[0])
    for i in os.listdir('jsons/'):
        if i.split('.')[0]!='latest':
            j=timechange(i)
            if j in list:
                pass
            else:
                save_csv_area(i)