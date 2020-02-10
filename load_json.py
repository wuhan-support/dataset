# -*- coding: UTF-8 -*-

import json
import random
import time
import requests
from log_support import LogSupport
import os

# 初始化日志
ls = LogSupport()
def load_response():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4037.2 Safari/537.36',
            'Connection': 'keep - alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-AU;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Host': 'service-f9fjwngp-1252021671.bj.apigw.tencentcs.com'
        }
        api = 'https://service-f9fjwngp-1252021671.bj.apigw.tencentcs.com/release/pneumonia'
        response = json.loads(requests.get(api, headers=headers).text)
        if not response['data']['listByArea']:
            raise Exception(response)
        ls.logging.info('json loaded at time {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        return response
    except Exception as e:
        ls.logging.error('json load failed, waiting for around 15 seconds')
        ls.logging.exception(e)
        time.sleep(15 + 5 * random.random())
        return load_response()


def load_json(file_name='./epidemic_history/latest.json'):
    with open(file_name, 'r+') as f:
        return json.load(f)


def write_json(file_name, js):
    with open(file_name, 'w+') as f:
        json.dump(js, f, sort_keys=True, indent=2)


def update():
    response = load_json()
    i = 0
    while True:
        latest_response = load_response()
        if latest_response['data']['listByArea'] != response['data']['listByArea']:
            write_json('epidemic_history/{}.json'.format(int(time.time())), latest_response)
            write_json('epidemic_history/latest.json', latest_response)
            ls.logging.info('json updated at time {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            response = latest_response
            i += 1
            if i % 10 == 0:
                git_upload()
                i = 0
            continue

def git_upload():
    os.system('git add epidemic_history/')
    os.system('git commit -m "update jsosn"')
    os.system('git push')
    ls.logging.info('jsons uploaded at time {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))


if __name__ == "__main__":
    update()
