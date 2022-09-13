import requests, json,psycopg2
API_KEY = "lGCfuIAWocXFJlONHzJBKVc1GM51cIzzTAZcAhUS"
from DB import query

def proxy_cleaner():
    rows = query("SELECT ip,port,proxy.user,password,buy_date,owner FROM proxy")
    for row in rows:
        print(row[4])
def buy_proxy(owner):
    PARAMS = {'type': 'dedicated',
              'ip_version': 4,
              'country': 'ru',
              'quantity': 1,
              'period': 30}
    x = requests.post('https://panel.proxyline.net/api/new-order/?api_key=' + API_KEY, json=PARAMS).text
    #x = '''[{"id":6853744,"ip":"45.149.129.130","internal_ip":null,"port_http":56626,"port_socks5":52188,"user":"11kQzRnT","username":"11kQzRnT","password":"KDT5UaKG","order_id":1444585,"type":"1","ip_version":4,"country":"ru","date":"2022-08-14 08:57:57.632228+00:00","date_end":"2022-09-13T11:57:57.632228+03:00","tags":[],"access_ips":[]}]'''
    res = json.loads(x)[0]
    query("INSERT INTO proxy VALUES ('"+res['ip']+"','"+str(res['port_http'])+"','"+res['user']+"','"+res['password']+"','"+owner+"',now()::timestamp)")
    return res

def set_proxy(username,owner):
    proxy = None
    #сначало проверим есть ли у нашего чувака свободный прокси
    rows = query("SELECT proxy_ip,COUNT(proxy_ip) FROM accounts WHERE owner='"+owner+"' and proxy_ip!='empty' GROUP BY proxy_ip'")
    for row in rows:
        # если есть то отдаем ему айпи
        if row[1]<3:
            proxy = row[0]
            r = query("SELECT ip,port,proxy.user,password from proxy WHERE ip='"+proxy+"'")[0]
            query("UPDATE accounts SET proxy_ip='"+r[0]+"',proxy_port='"+r[1]+"',proxy_user='"+r[2]+"',proxy_password='"+r[3]+"' WHERE phone='"+username+"' and owner = '"+owner+"'")
            break
    #ищем свободный прокси
    rows = query("SELECT ip,port,proxy.user,proxy.password from proxy WHERE owner=''")
    for r in rows:
        query("UPDATE accounts SET proxy_ip='" + r[0] + "',proxy_port='" + r[1] + "',proxy_user='" + r[2] + "',proxy_password='" + r[3] + "' WHERE phone='" + username + "' and owner = '" + owner + "'")
        break
    else:
        r = buy_proxy(owner)
        query("UPDATE accounts SET proxy_ip='" + r['ip'] + "',proxy_port='" + str(r['port_http']) + "',proxy_user='" + r['user'] + "',proxy_password='" + r['password'] + "' WHERE phone='" + username + "' and owner = '" + owner + "'")
def get_proxy(owner):
    rows = query("SELECT proxy_ip,COUNT(proxy_ip) FROM accounts WHERE owner='" + owner + "' and proxy_ip!='empty' GROUP BY proxy_ip")
    for row in rows:
        # если есть то отдаем ему айпи
        if row[1] < 3:
            proxy = row[0]
            r = query("SELECT ip,port,proxy.user,proxy.password from proxy WHERE ip='" + proxy + "'")[0]
            return r
    rows = query("SELECT ip,port,proxy.user,proxy.password from proxy WHERE owner=''")
    for r in rows:
        query("UPDATE proxy SET owner='"+owner+"' WHERE ip='"+r[0]+"'")
        return r
    # если свободного прокси нету то покупаем новый
    r = buy_proxy(owner)
    return [r['ip'],str(r['port_http']),r['user'],r['password']]

