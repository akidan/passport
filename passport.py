# -*- coding: utf-8
import os
import urllib.request
import requests
import json
import time
from time import sleep

def main():
    json_str = os.popen("cat ~/.secrets/key.json").read()
    json_dict = json.loads(json_str)
    jSessionId = json_dict['passport']['JSESSIONID']
    pcxSessionId = json_dict['passport']['pcxSessionId']
    htdocs = json_dict['passport']['htdocs']

    headers = {
        'Cookie': 'JSESSIONID='+jSessionId+'; pcxSessionId='+pcxSessionId+';'
    }

    data = {
        'addressName' : ''
    }

    fp1 = htdocs+'.html'
    fp2 = htdocs+'_log.html'
    fp3 = htdocs+'_log_tmp.html'
    fp4 = htdocs+'_history.html'
    fp5 = htdocs+'_history_origin.html'
    try:
        response = requests.post(
            'https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',
            headers=headers,
            data = data )
    except OSError:
        return 0

    if response.status_code >= 400:
        return 0

    schedule = response.json()['data']
    timelist = list()
    result = False
    lasttime = ""
    #fp3 format
    #Line1: [2021-03-22 06:22:09] 
    #Line2: 放出1个空位 | 4月16日 10:00-11:00 1个
    now_line1 = ""
    now_line2 = ""
    past_line1 = ""
    past_line2 = ""
    all_count = 0
    for s in schedule:
        day_per_count = 0
        for t in s['periodOfTimeList']:
            hour_per_count = t['peopleNumber']-t['userNumber']
            if hour_per_count > 0:
                day_per_count += hour_per_count
                now_line2 += ' | '+s['date'][6:].replace('-0', '月').replace('-', '月')+'日 '+t['startTime']+'-'+t['endTime']+' '+str(t['peopleNumber']-t['userNumber'])+'个'

        if day_per_count == 0:
            timelist.append(s['date'] +' 可预约数: '+str(day_per_count)+'\n')
        else:
            all_count += day_per_count
            timelist.append(s['date']+' <font color="red">可预约数: '+str(day_per_count)+'</font>\n')
            if result == False:
                lasttime += '<a href=log>上次放号时间</a>: '+time.strftime("%Y-%m-%d %H:%M", time.localtime())+'\n'
            result = True
            #lasttime = lasttime+'于 '+s['date'] +' 时间段放出 '+str(day_per_count)+' 个空位'+'\n'

    now_line1 = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+']'
    now_line2 = '放出'+str(all_count)+'个空位'+now_line2
        
    with open(fp3, 'r', encoding='UTF-8') as f3:
        past_line1 = f3.readline().strip('\n')
        past_line2 = f3.readline().strip('\n')

    #past  now
    # 0     0    Keep
    # N     N    Keep
    # 0     N    Write f3
    # N1    N2   Write f3,f4,f5
    # N     0    Write f3,f4,f5
    if past_line2 != now_line2:
        with open(fp3, 'w', encoding='UTF-8') as f3:
            f3.write(now_line1+'\n'+now_line2)
        if past_line2 != '放出0个空位':
            append_to_head(fp4, past_line1, past_line2, now_line1)
            append_to_head(fp5, past_line1, past_line2, now_line1)
            
    if lasttime != "":
        with open(fp2, 'w', encoding='UTF-8') as f2:
            f2.write(lasttime)

    timelist.sort()
    with open(fp1, 'w', encoding='UTF-8') as f1:
        f1.write('<h2>更新护照预约空位查询</h2>')
        if result == False:
            f1.write('当前状态: 无空位\n')
            f1.write('网页更新时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
            with open(fp2, 'r', encoding='UTF-8') as f2:
                f1.write(f2.read()+'\n')
        else:
            f1.write('<font color="red">当前状态: 有空位</font>\n')
            f1.write('网页更新时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
            f1.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n\n')
        for l in timelist:
            f1.write(l)

def append_to_head(fp, t1, t2, now):
    with open(fp, 'r+', encoding='UTF-8') as f:
        text = f.read()
        f.seek(0, 0)
        f.write(t1[:-1]+'-'+now[-9:]+' '+t2+'\n'+text)
            
if __name__ == "__main__":
    while (True):
        main()
        sleep(10)
