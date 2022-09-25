from _thread import start_new_thread
from itertools import groupby
from openpyxl import Workbook, load_workbook
import telethon,os,time,socket,asyncio,subprocess
from telethon import events
from telethon.sync import TelegramClient
from requests import get
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel
from datetime import datetime
from PROXY import get_proxy
from SocketStreamReader import SocketStreamReader
from ACCOUNT import ACCOUNT,TELEGRAM_ACCOUNT
from threading import Thread
import smtplib
import ssl
from email.message import EmailMessage
import string
import random
from DB import query
import socks

LIGHT_cost = 4900
LIGHT_limit = 10
STANDART_cost = 5900
STANDART_limit = 25
PRO_cost = 6900
PRO_limit = 50



## characters to generate password from
characters = list(string.ascii_letters.lower() + string.digits)
digits = list(string.digits)
def gen_new_password():
    random.shuffle(characters)
    password = []
    for i in range(8):
        password.append(random.choice(characters))

    random.shuffle(password)
    return "".join(password)
def gen_new_code():
    random.shuffle(digits)
    password = []
    for i in range(8):
        password.append(random.choice(characters))

    random.shuffle(password)
    return "".join(password)

email_sender = 'tsender.app@mail.ru'
email_password = 'i2KN5GDv7mkHCuS4WmXN'
def send_email(email_sender,email_receiver,st):
    context = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL('smtp.mail.ru', 465, context=context)
    smtp.ehlo()
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, st)
api_id = 3442047
api_hash = "cacb39d73070900d11d07fe14a476394"
SLEEP_TIME = 120

ACCOUNTS = []


def load_accounts():
    rows = query("SELECT username,password,firstname,lastname,email,phone,tarif FROM users")
    for row in rows:
        account1 = ACCOUNT()
        account1.username = row[0]
        account1.password = row[1]
        account1.firstname = row[2]
        account1.lastname = row[3]
        account1.email = row[4]
        account1.phone = row[5]
        account1.tarif = row[6]
        account1.path = os.getcwd() + "/users/"+account1.username

        if os.path.exists(account1.path)==False:
            os.makedirs(account1.path+"/accounts")
        else:
            rows =  query("SELECT phone FROM accounts WHERE owner='"+account1.username+"'")
            for row in rows:
                account1.telegram_accounts.append(row[0])
        ACCOUNTS.append(account1)
load_accounts()


forget_password={}
ip = get('https://api.ipify.org').text
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, 8888))
server.listen(100)
list_of_clients=[]

async def clientthread(conn, addr):
    account = None
    def send(m):
        m += "\n"
        for i in range(0, len(m), 1024):
            conn.send(bytes((m[i:i + 1024]), 'utf-8'))
    reader = SocketStreamReader(conn)

    while True:
        line = reader.readline()
        print(line)
        if(line=="c"):
            break
        sp = line.split("|")
        match sp[0]:
            case "login":
                nf=True
                for acc in ACCOUNTS:
                    if acc.username==sp[1]:
                        if(acc.password==sp[2]):
                            account = acc
                            tg = ""
                            rows = query("SELECT phone,username,firstname,lastname,status,last_used FROM accounts WHERE owner='" + acc.username + "'")
                            for row in rows:
                                tg += row[0] + "/"+str(row[1])+"/"+str(row[2])+"/"+str(row[3])+"/"+str(row[4])+"/"+str(row[5]).split(".")[0]+";"
                            tg = tg[:-1]
                            ms = ""
                            rows = query("SELECT id,status,users_count,start_date,stop_date,active_accounts_count,success_count,failed_count FROM mails WHERE username='"+acc.username+"'")
                            for row in rows:
                                ms += str(row[0])+"/"+str(row[1])+"/"+str(row[2])+"/"+str(row[3]).split(".")[0]+"/"+str(row[4]).split(".")[0]+"/"+str(row[5])+"/"+str(row[6])+"/"+str(row[7])+";"
                            ms = ms[:-1]
                            send("login_success|"+acc.firstname+"|"+acc.lastname+"|"+acc.email+"|0|"+tg+"|"+ms+"|"+acc.phone+"|"+acc.tarif)
                            nf = False
                            break
                        else:
                            send("login_failed|password_is_wrong")
                            nf = False
                if nf:
                    send("login_failed|username_is_not_found")
            case "refresh_mails":
                ms = ""
                rows = query(
                    "SELECT id,status,users_count,start_date,stop_date,active_accounts_count,success_count,failed_count FROM mails WHERE username='" + acc.username + " and CAST(start_date as DATE)>=CAST(now() as DATE)'")
                for row in rows:
                    ms += str(row[0]) + "/" + str(row[1]) + "/" + str(row[2]) + "/" + str(row[3]).split(".")[0] + "/" + \
                          str(row[4]).split(".")[0] + "/" + str(row[5]) + "/" + str(row[6]) + "/" + str(row[7]) + ";"
                if ms != "":
                    ms = ms[:-1]
                    send("refresh_mails|"+ms)
            case "forget_password":
                nf = True
                for acc in ACCOUNTS:
                    if acc.username == sp[1]:
                        nf=False
                        break
                if nf:
                    send("email_is_invalid")
                else:
                    gn = gen_new_code()
                    forget_password[sp[1]] = gn
                    subject = 'Восстановление аккаунта'
                    body = "Ваш код:"+gn
                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = sp[1]
                    em['Subject'] = subject
                    em.set_content(body)
                    send_email(email_sender, sp[1], em.as_string())
                    send("email_code_sended")
            case "restore_password":
                if(forget_password[sp[1]]==sp[2]):
                    for acc in ACCOUNTS:
                        if acc.username == sp[1]:
                            account = acc
                            tg = ""
                            rows = query(
                                "SELECT phone,username,firstname,lastname,status,last_used FROM accounts WHERE owner='" + acc.username + "'")
                            for row in rows:
                                tg += row[0] + "/" + str(row[1]) + "/" + str(row[2]) + "/" + str(
                                    row[3]) + "/" + str(row[4]) + "/" + str(row[5]).split(".")[0] + ";"
                            tg = tg[:-1]
                            ms = ""
                            rows = query(
                                "SELECT id,status,users_count,start_date,stop_date,active_accounts_count,success_count,failed_count FROM mails WHERE username='" + acc.username + "'")
                            for row in rows:
                                ms += str(row[0]) + "/" + str(row[1]) + "/" + str(row[2]) + "/" + \
                                      str(row[3]).split(".")[0] + "/" + str(row[4]).split(".")[0] + "/" + str(
                                    row[5]) + "/" + str(row[6]) + "/" + str(row[7]) + ";"
                            ms = ms[:-1]
                            send("login_code|" + acc.firstname + "|" + acc.lastname + "|" + acc.email + "|0|" + tg + "|" + ms + "|" + acc.phone + "|" + acc.tarif)
                            break;
            case "send_code":
                account.my_proxy = get_proxy(account.username)
                my_proxy = {
                    'proxy_type': "http",  # (mandatory) protocol to use (see above)
                    'addr': account.my_proxy[0],  # (mandatory) proxy IP address
                    'port': int(account.my_proxy[1]),  # (mandatory) proxy port number
                    'username': account.my_proxy[2],  # (optional) username if the proxy requires auth
                    'password': account.my_proxy[3]
                }
                print(my_proxy)
                account.new_telegram_account =TELEGRAM_ACCOUNT()
                account.new_telegram_account.phone = sp[1]
                account.new_telegram_account.client = TelegramClient(account.path+"/accounts/"+sp[1], api_id, api_hash,proxy=my_proxy)
                await account.new_telegram_account.client.connect()
                try:
                    await account.new_telegram_account.client.send_code_request(sp[1])
                    send("code_sended|" + sp[1])
                except telethon.errors.rpcerrorlist.PhoneNumberInvalidError:
                    send("phone_number_is_invalid|" + sp[1])
            case "sign_in":
                try:
                    await account.new_telegram_account.client.sign_in(account.new_telegram_account.phone, code=sp[1])
                    me = await account.new_telegram_account.client.get_me()
                    await account.new_telegram_account.client.disconnect()
                    account.new_telegram_account.client = None
                    account.new_telegram_account.phone = None
                    account.new_telegram_account = None
                    account.telegram_accounts.append(me.phone)
                    query("INSERT INTO accounts (id,firstname,lastname,username,phone,owner,proxy_ip,proxy_port,proxy_user,proxy_password,proxy_type,last_used) VALUES ('" + str(me.id) + "','" + str(me.first_name) + "','" + str(me.last_name) + "','" + str(me.username) + "','" + str(me.phone) + "','"+str(account.username)+"','"+account.my_proxy[0]+"','"+account.my_proxy[1]+"','"+account.my_proxy[2]+"','"+account.my_proxy[3]+"','http',now()::timestamp)")
                    send("account_added_successfully|" + me.phone + "|" + str(me.first_name) + "|" + str(me.last_name) + "|" + str(me.username) + "")
                except telethon.errors.SessionPasswordNeededError:
                    send("enter_password|" + account.new_telegram_account.phone)
                except Exception as e:
                    print(e)
                    if "The phone code entered was invalid" in str(e):
                        send("phone_code_invalid")


            case "sign_in_with_password":
                await account.new_telegram_account.client.sign_in(password=sp[1])
                me = await account.new_telegram_account.client.get_me()
                await account.new_telegram_account.client.disconnect()
                account.new_telegram_account.client = None
                account.new_telegram_account.phone = None
                account.new_telegram_account = None
                account.telegram_accounts.append(me.phone)
                query("INSERT INTO accounts (id,firstname,lastname,username,phone,owner,proxy_ip,proxy_port,proxy_user,proxy_password,proxy_type,last_used) VALUES ('" + str(me.id) + "','" + str(me.first_name) + "','" + str(me.last_name) + "','" + str(me.username) + "','" + str(me.phone) + "','"+str(account.username)+"','"+account.my_proxy[0]+"','"+account.my_proxy[1]+"','"+account.my_proxy[2]+"','"+account.my_proxy[3]+"','http',now()::timestamp)")
                send("account_added_successfully|" + me.phone + "|" + str(me.first_name) + "|" + str(me.last_name) + "|" + str(me.username) + "")
            case "file":
                print("file")
                filetodown = open(account.path+"/"+sp[1], "wb")
                expected_bytes = int(sp[2])
                received_bytes = 0
                stream = bytes()
                while received_bytes < expected_bytes:
                    chunk = conn.recv(expected_bytes - received_bytes)
                    stream += chunk
                    received_bytes += len(chunk)
                filetodown.write(stream)
                filetodown.close()
                account.current_file = sp[1]
                print("file ready")

            case "new_mail":
                if os.path.exists(account.path+"/mails") == False:
                    os.makedirs(account.path + "/mails")
                media = ""
                try:
                    media = account.current_file
                except:
                    pass

                id = query("INSERT INTO mails (SLEEP_TIME,username,text,media,users_count) VALUES ("+str(SLEEP_TIME)+",'" + account.username + "','" + sp[3].replace("{endline}","\n") + "','" + media + "',"+sp[4]+") RETURNING id")[0][0]
                uc = 0
                for a in sp[6].split("/"):
                    if a=="":
                        continue
                    query("UPDATE accounts SET mail='" + str(id) + "' Where phone='"+a+"' and owner='"+account.username+"'")
                    uc+=1
                with open(account.path+"/mails/"+str(id)+".txt", 'w') as fp:
                    fp.write(sp[5])
                subprocess.run(["screen -dmS mail sudo python3.10 /root/tsender/mail_start.py "+str(id)], shell=True,stdout=subprocess.PIPE)
                send("new_mail_success|"+str(id)+"|"+sp[4]+"|"+str(uc))
            case "mail":
                status = query("SELECT success_count,failed_count,status FROM mails WHERE id=" + sp[1] + " and username='" + account.username + "'")[0]
                print(status)
                send("mail|" + str(sp[1]) + "|" + str(status[0]) + "|" + str(status[1]) + "|" + str(status[2]))
            case "check_status_of_account":
                row = query("SELECT status,proxy_ip,proxy_port,proxy_user,proxy_password FROM accounts WHERE phone='"+sp[1]+"' and owner='"+account.username+"'")[0]
                if(row[0]=="busy"):
                    send("status_of_account|" + sp[1] + "|busy")
                else:
                    my_proxy = None
                    if row[1]=="empty":
                        proxy = get_proxy(account.username)
                        my_proxy = (socks.HTTP, proxy[0], int(proxy[1]), True, proxy[2], proxy[3])
                        query("UPDATE accounts SET proxy_ip='" + proxy[0] + "',proxy_port='" + proxy[1] + "',proxy_user='" + proxy[2]+ "',proxy_password='" + proxy[3] + "' WHERE phone='" + sp[1] + "' and owner = '" + account.username + "'")
                    else:
                        my_proxy = (socks.HTTP, row[1], int(row[2]), True, row[3], row[4])
                    cc = TelegramClient(account.path+"/accounts/+"+sp[1], api_id, api_hash,proxy=my_proxy)
                    await cc.connect()
                    if(cc.is_user_authorized==False):
                        query("UPDATE accounts SET status='account_not_authorized',last_used=now()::timestamp WHERE phone='"+sp[1]+"' and owner='"+account.username+"'")
                        send("status_of_account|" + sp[1] + "|account_not_authorized|" + str(datetime.now()))
                    try:
                        await cc.send_message("maric000","test")
                        query("UPDATE accounts SET status='ready',last_used=now()::timestamp WHERE phone='"+sp[1]+"' and owner='"+account.username+"'")
                        send("status_of_account|" + sp[1] + "|ready|"+str(datetime.now()))
                    except Exception as e:
                        print(e)
                        if "The authorization has been invalidated" in str(e):
                            query("UPDATE accounts SET status='account_not_authorized',last_used=now()::timestamp WHERE phone='"+sp[1]+"' and owner='"+account.username+"'")
                            send("status_of_account|" + sp[1] + "|account_not_authorized|"+str(datetime.now()))
                        else:
                            print(str(e))
                            query("UPDATE accounts SET status='flood',last_used=now()::timestamp WHERE phone='" + sp[1] + "' and owner='" + account.username + "'")
                            send("status_of_account|" + sp[1] + "|flood|" + str(datetime.now()))
                    await cc.disconnect()

            case "delete_account":
                r = query("SELECT proxy_ip FROM accounts WHERE owner='" + account.username + "' and phone='" +sp[1]+"'")[0][0]
                query("DELETE FROM accounts Where phone='" + sp[1] + "' and owner='" + account.username + "'")
                try:
                    os.remove(account.path+"/telegram_accounts/+"+sp[1]+".session")
                except:
                    pass
                cc = query("SELECT COUNT(proxy_ip) FROM accounts WHERE owner='" + account.username + "' and proxy_ip='"+r+"'")[0][0]
                if cc==0:
                    query("UPDATE proxy SET owner='' WHERE ip='"+r+"' and owner='"+account.username+"'")
                send("account_deleted|"+sp[1])
            case "mail_file":
                send("file|" + sp[1] + "_result.xlsx|")
                filetosend = open(account.path+"/mails/"+sp[1] + "_result.xlsx", "rb")
                data = filetosend.read(1024)
                while data:
                    print("Sending...")
                    conn.send(data)
                    data = filetosend.read(1024)
                filetosend.close()
            case "change_info":
                query("UPDATE users SET firstname='"+sp[1]+"',lastname='"+sp[2]+"',phone='"+sp[3]+"' WHERE username='"+account.username+"'")
                account.firstname=sp[1]
                account.lastname=sp[2]
                account.phone=sp[3]
            case "change_password":
                query("UPDATE users SET password='"+sp[1]+"' WHERE username='"+account.username+"'")
                account.password = sp[1]
            case "support":
                email_receiver = "smaricpb@gmail.com"
                subject = 'Сообщение от тех поддержки'
                body = "Пользователь:\nИмя: "+account.firstname+"\nEmail: "+account.email+"\nСообщение: "+sp[1]
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)
                send_email(email_sender,email_receiver,em.as_string())
            case "start_parse":
                async with TelegramClient("userbot2", api_id, api_hash) as cc:
                    offset = 0
                    limit = 200
                    all_participants = []
                    wb = Workbook()
                    ws = wb.active
                    ws.column_dimensions['A'].width = 20
                    ws.column_dimensions['B'].width = 30
                    ws.column_dimensions['C'].width = 30
                    ws.column_dimensions['D'].width = 30
                    ws.column_dimensions['E'].width = 30
                    while True:
                        participants = await cc(GetParticipantsRequest(
                            sp[1], ChannelParticipantsSearch(''), offset, limit,
                            hash=0
                        ))
                        if not participants.users:
                            break
                        all_participants.extend(participants.users)
                        offset += len(participants.users)
                    for user in all_participants:
                        user_id = str(user.id)
                        user_username = user.username
                        user_first_name = user.first_name
                        user_last_name = ""
                        if user.last_name is not None:
                            user_last_name = user.last_name
                        user_phone = ""
                        if user.phone is not None:
                            user_phone = user.phone
                        ws.append([user_id, user_username, user_first_name, user_last_name, user_phone])

                    wb.save(account.path+"/"+sp[1]+".xlsx");
                    send("file|"+sp[1]+".xlsx|")
                    filetosend = open(account.path+"/"+sp[1]+".xlsx", "rb")
                    data = filetosend.read(1024)
                    while data:
                        print("Sending...")
                        conn.send(data)
                        data = filetosend.read(1024)
                    filetosend.close()

    print(addr[0]+" is disconnected")
def between_callback(conn,addr):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(clientthread(conn,addr))
    loop.close()

def receive():
    while True:
        try:
            conn, addr = server.accept()
            print(addr[0] + " connected")
            list_of_clients.append(conn)
            start_new_thread(between_callback,(conn,addr))
        except Exception as ee:
            print("newthread",ee)
print("xm")
t1 = Thread(target=receive)
t1.start()
print("recive")

with TelegramClient('userbot1', 3442047, "cacb39d73070900d11d07fe14a476394") as client:
    print("Бот запущен")

    @events.register(events.NewMessage(chats=[265299531]))
    async def msg_handler(event: events.NewMessage.Event):
        message = event.message
        print(message)
        fname = message.message.split("\nName: ")[1].split("\n")[0]
        email =message.message.split("\nEmail: ")[1].split("\n")[0]
        phone =message.message.split("\nPhone: ")[1].split("\n")[0]
        tarif =message.message.split("\n1. ")[1].split("\n")[0]
        new_password = gen_new_password()

        rows = query("SELECT tarif,tarif_time from users WHERE email='"+email+"'")
        if rows is not None:
            if len(rows)>0:
                user = rows[0]
                print(user)
                now = time.time()
                old = user[1].timestamp()
                print(now,old)
                прошло = int(now-old)
                осталось=(86400*30)-прошло
                print(осталось)
                t1 = 3
                t2 = 3
                if 'LIGHT' in user[0]:
                    t1=1
                elif 'STANDART' in user[0]:
                    t1=2
                if 'LIGHT' in tarif:
                    t2=1
                elif 'STANDART' in tarif:
                    t2=2
                if(t2>t1):
                    print("Повышает тариф")
                    стоимость_старого_тарифа = STANDART_cost
                    стоимость_нового_тарифа = PRO_cost
                    if t1==1:
                        стоимость_старого_тарифа= LIGHT_cost
                        стоимость_нового_тарифа=STANDART_cost
                    осталось_денег=стоимость_старого_тарифа/(86400) * (осталось/30)
                    деньги = стоимость_нового_тарифа+осталось_денег
                    new_timestamp = ((деньги * 30 * 86400) / стоимость_нового_тарифа) + now
                    new_datetime = datetime.fromtimestamp(new_timestamp)
                    query("UPDATE users SET tarif_time=(TIMESTAMP '"+str(new_datetime).split(".")[0]+"') WHERE email='"+email+"'")
                elif t1==t2:
                    print("Продлевает тариф")
                    query("UPDATE users SET tarif_time=tarif_time+interval '30 day' WHERE email='"+email+"'")
                else:
                    print("Понижает тариф")
                    стоимость_старого_тарифа = PRO_cost
                    стоимость_нового_тарифа = STANDART_cost
                    if t1 == 1:
                        стоимость_старого_тарифа = STANDART_cost
                        стоимость_нового_тарифа = LIGHT_cost
                    осталось_денег = стоимость_старого_тарифа / (86400) * (осталось / 30)
                    деньги = стоимость_нового_тарифа + осталось_денег
                    new_timestamp = ((деньги * 30 * 86400) / стоимость_нового_тарифа) + now
                    new_datetime = datetime.fromtimestamp(new_timestamp)
                    query("UPDATE users SET tarif_time=(TIMESTAMP '" + str(new_datetime).split(".")[
                        0] + "') WHERE email='" + email + "'")

                return
        '''
        email_receiver = email

        subject = 'Ваши данные для авторизации'
        body = "Привет "+fname+". Поздравляем с приобретением тарифа "+tarif+".\nВаш пароль:"+new_password+"\nВы можете скачать приложение по ссылке: какая то ссылка"
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        send_email(email_sender,email_receiver,em.as_string())
        '''
        account1 = ACCOUNT()
        account1.username = email
        account1.password = new_password
        account1.firstname = fname
        account1.lastname = ""
        account1.email = email
        account1.phone = phone
        account1.tarif = tarif
        print("Name:", fname)
        print("Mail:", email)
        print("Phone:", phone)
        print("Tarif:", tarif)
        account1.path = os.getcwd() + "/users/" + account1.username
        query("INSERT INTO users (username,password,firstname,lastname,email,phone,tarif,tarif_time) VALUES('"+email+"','"+new_password+"','"+fname+"','','"+email+"','"+phone+"','"+tarif+"',now()::timestamp)")
        if os.path.exists(account1.path)==False:
            os.makedirs(account1.path+"/accounts")
        ACCOUNTS.append(account1)
    client.add_event_handler(msg_handler)
    client.run_until_disconnected()