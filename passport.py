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
    fp3 = htdocs+'_history.html'
    try:
        response = requests.post(
            'https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',
            headers=headers,
            data = data )
    except OSError:
        return 0
    
    schedule = response.json()['data']
    timelist = list()
    result = False
    lasttime = ""
    history_prev = ""
    history_post = ""
    history  = ""
    all_count = 0
    for s in schedule:
        day_per_count = 0
        for t in s['periodOfTimeList']:
            hour_per_count = t['peopleNumber']-t['userNumber']
            if hour_per_count > 0:
                day_per_count += hour_per_count
                history_post += ' | '+s['date'][6:].replace('-0', '月').replace('-', '月')+'日 '+t['startTime']+'-'+t['endTime']+' '+str(t['peopleNumber']-t['userNumber'])+'个'

        if day_per_count == 0:
            timelist.append(s['date'] +' 可预约数: '+str(day_per_count)+'\n')
        else:
            all_count += day_per_count
            timelist.append(s['date']+' <font color="red">可预约数: '+str(day_per_count)+'</font>\n')
            if result == False:
                lasttime += '上次放号时间: '+time.strftime("%Y-%m-%d %H:%M", time.localtime())+'\n'
            result = True
            #lasttime = lasttime+'于 '+s['date'] +' 时间段放出 '+str(day_per_count)+' 个空位'+'\n'

    if all_count > 0:
        history_prev = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'] 放出'
        history = history_prev+str(all_count)+'个空位'+history_post
        f3 = open(fp3, 'r+', encoding='UTF-8')
        oldhistory = f3.read()        
        f3.seek(0, 0)
        f3.write(history+'\n'+oldhistory)
        f3.close()

    if lasttime != "":
        f2 = open(fp2, 'w', encoding='UTF-8')
        f2.write(lasttime)
        f2.close()

    timelist.sort()
    f1 = open(fp1, 'w', encoding='UTF-8')
    f1.write('<h2>更新护照预约空位查询</h2>')
    if result == False:
        f1.write('当前状态: 无空位\n')
        f1.write('网页更新时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
        f2 = open(fp2, 'r', encoding='UTF-8')
        f1.write(f2.read()+'\n')
    else:
        f1.write('<font color="red">当前状态: 有空位</font>\n')
        f1.write('网页更新时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
        f1.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n\n')
    for l in timelist:
        f1.write(l)
    f1.close()

if __name__ == "__main__":
    while (True):
        main()
        sleep(10)
