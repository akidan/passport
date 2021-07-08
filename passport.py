# -*- coding: utf-8
import os, requests, json, time, datetime, smtplib, pymysql.cursors, random, hashlib
from time import sleep
from email.mime.text import MIMEText

json_str = os.popen("cat ~/.secrets/key.json").read()
const_param = json.loads(json_str)['passport']
mysql_param = json.loads(json_str)['mysql']
mail_param  = json.loads(json_str)['mail']

def main():
    global const_param
    pcxSessionId       = const_param['pcxSessionId']
    pcxSessionIdNagoya = const_param['pcxSessionIdNagoya']
    htdocs             = const_param['htdocs']

    headers = {'Cookie': 'pcxSessionId='+pcxSessionId+';'}
    headers_nagoya = {'Cookie': 'pcxSessionId='+pcxSessionIdNagoya+';'}
    #daoguan
    data_dg = {'addressName' : ''}
    #youji
    data_yj = {'addressName' : 'e1be0a00f05e40e6badd079ea4db9a87'}
    #teshu
    data_ts = {'addressName' : '0c50854c36c04e309bcdf607a1739bb2'}

    fp_hp = htdocs+'.html'

    reservation_types = ['daoguan','youji','teshu','nagoya']
    reservation_names = ['东京到馆办理', '不见面办理（邮寄）', '东京到馆绿色通道特殊办理（16岁以下，60岁以上）', '名古屋到馆办理']

    try:
        responses = []
        responses.append(requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers, data = data_dg))
        responses.append(requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers, data = data_yj))
        responses.append(requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers, data = data_ts))
        responses.append(requests.post('https://ppt.mfa.gov.cn/appo/service/reservation/data/getReservationDateBean.json',headers=headers_nagoya, data = data_dg))
    except OSError:
        return 0

    with open(fp_hp, 'w', encoding='UTF-8') as f_hp:
        f_hp.write('<h2>更新护照预约空位查询</h2>')
        f_hp.write('网页更新时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')

        for i in range(len(reservation_types)):
            process_response(i, f_hp, htdocs+'_'+reservation_types[i], responses[i], reservation_types[i], reservation_names[i])

def process_response(i, f_hp, fp_self, response, reservation_type, reservation_name):
    if response.status_code < 400:
        array = get_time_list(response.json(),fp_self+'_log.html',fp_self+'_log_tmp.html',fp_self+'_history.html',fp_self+'_history_origin.html',reservation_type)
        if array[0] == False:
            f_hp.write('\n'+reservation_name+' 当前状态: 无空位\n')
            with open(fp_self+'_log.html', 'r', encoding='UTF-8') as f_log:
                f_hp.write(f_log.read()+'\n')
        else:
            f_hp.write('<font color="red">\n'+reservation_name+' 当前状态: 有空位</font>\n')
            f_hp.write('<a href=https://ppt.mfa.gov.cn/appo/index.html>点此快速预约</a>\n')
            send_mail(i+1, reservation_name)
        for l in array[1]:
            f_hp.write(l)

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
                    lasttime += '<a href="../passport/'+reservation_type+'">上次放号时间</a>: '+time.strftime("%Y-%m-%d %H:%M", time.localtime())
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

def append_to_head(fp, t1, t2, now):
    with open(fp, 'r+', encoding='UTF-8') as f:
        text = f.read()
        f.seek(0, 0)
        f.write(t1[:-1]+'-'+now[-9:]+' '+t2+'\n'+text)

def send_mail(mail_type, reservation_name):
    #subscribe_types = [[1,3,5,7,9,11,13,15],
    #                   [2,3,6,7,10,11,14,15],
    #                   [4,5,6,7,12,13,14,15],
    #                   [8,9,10,11,12,13,14,15]]
    global const_param, mail_param
    mail_types = 4
    subscribe_type = []
    i = 0
    while i < pow(2,mail_types)-1:
        i = i + pow(2,mail_type-1)
        for j in range(pow(2,mail_type-1)):
            subscribe_type.append(i)
            i = i + 1

    mail_dict = {}
    mail_list = select_mail_from_user(mail_type, subscribe_type)
    for mail in mail_list:
        to_email = mail['email']

        code_str = mail['email'] + str(int(round(time.time() * 1000)))
        random_index = random.randrange(len(code_str))
        mail_code_origin = code_str[0:random_index]+'#'+str(mail['user_id'])+'#'+code_str[random_index:len(code_str)]
        mail_code = encode_decimal(int(hashlib.md5(mail_code_origin.encode()).hexdigest(),16))

        mail_dict['user_id'] = mail['user_id']
        mail_dict['email'] = mail['email']
        mail_dict['mail_code'] = mail_code

        message = "<table><tr><td style=\"border-collapse: collapse; font-size: 18px; font-weight: bold; line-height: 20px; padding-top: 50px; padding-bottom: 50px;\">" + reservation_name + " 放号</td></tr><tr><td style=\"border-collapse: collapse; font-size: 18px; line-height: 24px; padding-bottom: 10px;\">点此快速预约：<a href=\"https://ppt.mfa.gov.cn/appo/index.html\">https://ppt.mfa.gov.cn/appo/index.html</a></td></tr><tr><td align=\"left\" style=\"font-family: Arial, Helvetica, sans-serif; font-size: 10px; color: rgb(102, 102, 102);\" class=\"\">请勿回复本电子邮件。我们无法回复您发送到本邮件地址的任何邮件。如有疑问，<a href=\"https://www.akidan.com/passport/\">请访问这里</a>获取更多信息。<a href=\"https://www.akidan.com/passport/subscribe?code="+mail_code+"\">退订</a></td></tr></table>"
        msg = MIMEText(message, "html")
        msg["Subject"] = "出现更新护照预约的空位！"
        msg["To"] = mail['email']
        msg["From"] = const_param['mailSender']

        server = smtplib.SMTP(mail_param['domain'], int(mail_param['port']))
        server.set_debuglevel(True)
        server.starttls()
        server.login(const_param['mailSender'], const_param['mailPassword'])
        server.send_message(msg)
        server.quit()
    #if len(mail_dict) > 0:
        insert_into_mail(mail_type, mail_dict)

def encode_decimal(num):
    global const_param
    chars = const_param['mailCodeEncryptor']
    base = len(chars)
    string = ""
    while True:
        string = chars[num % base] + string
        num = num // base
        if num == 0:
            break
    return string

def select_mail_from_user(mail_type, subscribe_type):
    global const_param
    db = db_connect()
    cursor = db.cursor()
    if mail_type == 2:
        check_date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        check_date = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
    sql = (const_param['selectSql'] % (str(mail_type),check_date,str(tuple(subscribe_type))))
    cursor.execute(sql)
    db.close()
    if cursor != None:
        mail_list = cursor
    cursor.close()
    return mail_list

def insert_into_mail(mail_type, mail_dict):
    global const_param
    db = db_connect()
    cursor = db.cursor()
    sql = (const_param['insertSql'] %(str(mail_dict['user_id']), str(mail_type), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), mail_dict['mail_code']))
    cursor.execute(sql)
    db.commit()
    db.close()
    cursor.close()

def db_connect():
    global const_param, mysql_param
    db = pymysql.connect(host = mysql_param['host'],
                         port = int(mysql_param['port']),
                         db = const_param['db'],
                         user = mysql_param['user'],
                         password = mysql_param['password'],
                         cursorclass = pymysql.cursors.DictCursor)
    return db

if __name__ == "__main__":
    while (True):
        main()
        sleep(10)
