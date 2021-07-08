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
    pcxSessionId = json_dict['passport']['pcxSessionId']
    pcxSessionIdNagoya = json_dict['passport']['pcxSessionIdNagoya']
    htdocs = json_dict['passport']['htdocs']

    headers = {'Cookie': 'pcxSessionId='+pcxSessionId+';'}
    headers_nagoya = {'Cookie': 'pcxSessionId='+pcxSessionIdNagoya+';'}
    #daoguan
    data_dg = {'addressName' : ''}
    #youji
    data_yj = {'addressName' : 'e1be0a00f05e40e6badd079ea4db9a87'}
    #teshu
    data_ts = {'addressName' : '0c50854c36c04e309bcdf607a1739bb2'}

    fp_hp = htdocs+'.html'

    fp_dg_log     = htdocs+'_daoguan_log.html'
    fp_dg_log_tmp = htdocs+'_daoguan_log_tmp.html'
    fp_dg_his     = htdocs+'_daoguan_history.html'
    fp_dg_his_ori = htdocs+'_daoguan_history_origin.html'

    fp_yj_log     = htdocs+'_youji_log.html'
    fp_yj_log_tmp = htdocs+'_youji_log_tmp.html'
    fp_yj_his     = htdocs+'_youji_history.html'
    fp_yj_his_ori = htdocs+'_youji_history_origin.html'

    fp_ts_log     = htdocs+'_teshu_log.html'
    fp_ts_log_tmp = htdocs+'_teshu_log_tmp.html'
    fp_ts_his     = htdocs+'_teshu_history.html'
    fp_ts_his_ori = htdocs+'_teshu_history_origin.html'

    fp_ngy_log     = htdocs+'_nagoya_log.html'
    fp_ngy_log_tmp = htdocs+'_nagoya_log_tmp.html'
    fp_ngy_his     = htdocs+'_nagoya_history.html'
    fp_ngy_his_ori = htdocs+'_nagoya_history_origin.html'

    try:
        response_ngy =requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers_nagoya, data = data_dg)
        response_dg = requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers, data = data_dg)
        response_yj = requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers, data = data_yj)
        response_ts = requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers, data = data_ts)
    except OSError:
        return 0

    with open(fp_hp, 'w', encoding='UTF-8') as f_hp:
        f_hp.write('<h2>更新护照预约空位查询</h2>')
        f_hp.write('网页更新时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')

        if response_dg.status_code < 400:
            array = get_time_list(response_dg.json(),fp_dg_log,fp_dg_log_tmp,fp_dg_his,fp_dg_his_ori,"daoguan")
            if array[0] == False:
                f_hp.write('\n东京到馆办理 当前状态: 无空位\n')
                with open(fp_dg_log, 'r', encoding='UTF-8') as f_dg_log:
                    f_hp.write(f_dg_log.read()+'\n')
            else:
                f_hp.write('<font color="red">\n东京到馆办理 当前状态: 有空位</font>\n')
                f_hp.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n')
            for l in array[1]:
                f_hp.write(l)

        if response_yj.status_code < 400:
            array = get_time_list(response_yj.json(),fp_yj_log,fp_yj_log_tmp,fp_yj_his,fp_yj_his_ori,"youji")
            if array[0] == False:
                f_hp.write('\n不见面办理（邮寄） 当前状态: 无空位\n')
                with open(fp_yj_log, 'r', encoding='UTF-8') as f_yj_log:
                    f_hp.write(f_yj_log.read()+'\n')
            else:
                f_hp.write('<font color="red">\n不见面办理（邮寄） 当前状态: 有空位</font>\n')
                f_hp.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n')
            for l in array[1]:
                f_hp.write(l)

        if response_ts.status_code < 400:
            array = get_time_list(response_ts.json(),fp_ts_log,fp_ts_log_tmp,fp_ts_his,fp_ts_his_ori,"teshu")
            if array[0] == False:
                f_hp.write('\n东京到馆绿色通道特殊办理（16岁以下，60岁以上） 当前状态: 无空位\n')
                with open(fp_ts_log, 'r', encoding='UTF-8') as f_ts_log:
                    f_hp.write(f_ts_log.read()+'\n')
            else:
                f_hp.write('<font color="red">\n东京到馆绿色通道特殊办理（16岁以下，60岁以上） 当前状态: 有空位</font>\n')
                f_hp.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n')
            for l in array[1]:
                f_hp.write(l)

        if response_ngy.status_code < 400:
            array = get_time_list(response_ngy.json(),fp_ngy_log,fp_ngy_log_tmp,fp_ngy_his,fp_ngy_his_ori,"nagoya")
            if array[0] == False:
                f_hp.write('\n名古屋到馆办理 当前状态: 无空位\n')
                with open(fp_ngy_log, 'r', encoding='UTF-8') as f_ngy_log:
                    f_hp.write(f_ngy_log.read()+'\n')
            else:
                f_hp.write('<font color="red">\n名古屋到馆办理 当前状态: 有空位</font>\n')
                f_hp.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n')
            for l in array[1]:
                f_hp.write(l)

def append_to_head(fp, t1, t2, now):
    with open(fp, 'r+', encoding='UTF-8') as f:
        text = f.read()
        f.seek(0, 0)
        f.write(t1[:-1]+'-'+now[-9:]+' '+t2+'\n'+text)

def get_time_list(response_json,fp_log,fp_log_tmp,fp_his,fp_his_ori,reservation_type):
    all_count = 0
    result = False
    timelist = list()
    lasttime = ""
    # fp_xx_log_tmp format
    # Line1: [2021-03-22 06:22:09] 
    # Line2: 放出1个空位 | 4月16日 10:00-11:00 1个
    now_line1 = ""
    now_line2 = ""
    past_line1 = ""
    past_line2 = ""
    if "data" in response_json.keys():
        schedule = response_json['data']
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
                    lasttime += '<a href=log/'+reservation_type+'>上次放号时间</a>: '+time.strftime("%Y-%m-%d %H:%M", time.localtime())
                result = True

    now_line1 = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+']'
    now_line2 = '放出'+str(all_count)+'个空位'+now_line2
        
    with open(fp_log_tmp, 'r', encoding='UTF-8') as f_log_tmp:
        past_line1 = f_log_tmp.readline().strip('\n')
        past_line2 = f_log_tmp.readline().strip('\n')

    #past  now
    # 0     0    Keep
    # N     N    Keep
    # 0     N    Write f_xx_log_tmp
    # N1    N2   Write f_xx_log_tmp,f_xx_his,f_xx_his_ori
    # N     0    Write f_xx_log_tmp,f_xx_his,f_xx_his_ori
    if past_line2 != now_line2:
        with open(fp_log_tmp, 'w', encoding='UTF-8') as f_log_tmp:
            f_log_tmp.write(now_line1+'\n'+now_line2)
        if past_line2 != '放出0个空位':
            append_to_head(fp_his,     past_line1, past_line2, now_line1)
            append_to_head(fp_his_ori, past_line1, past_line2, now_line1)
            
    if lasttime != "":
        with open(fp_log, 'w', encoding='UTF-8') as f_log:
            f_log.write(lasttime)

    timelist.sort()
    return [result, timelist]

if __name__ == "__main__":
    while (True):
        main()
        sleep(10)
