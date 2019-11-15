import imaplib
import email
import re
import pymysql
import time
import datetime
import pytz


class Fetcher():
    def __init__(self, host, username, pwd, port=993):
        self.host = host
        self.username = username
        self.pwd = pwd
        self.port = port
        self.resList = []
        self.db = pymysql.connect("localhost", "root", "mysql", "emailfetcher")
        self.cursor = self.db.cursor()
        try:
            self.serv = imaplib.IMAP4_SSL(self.host, self.port)
        except:
            self.serv = imaplib.IMAP4(self.host, self.port)
        self.serv.login(self.username, self.pwd)
        self.serv.select()
        self.index = None
        self.uid_pattern = re.compile(r'\d+ \(UID (\d+)\)')
        self.indices = list()
        self.utc = pytz.UTC

    def parseBody(self, message):
        content = ''
        for part in message.walk():
            if not part.is_multipart():
                typ = part.get_content_type()
                if typ == 'text/plain' or typ == 'text/html':
                    dr = re.compile(r'<[^>]+>', re.S)
                    raw_content = part.get_payload(decode=True)
                    try:
                        content += dr.sub('', str(raw_content, errors='ignore'))
                    except:
                        continue
        return content

    def parseUid(self, data):
        match = self.uid_pattern.match(data)
        return match.group(1)

    def getMail(self):
        typ, data = self.serv.search(None, 'ALL')
        print(data)
        offset = 0
        for num in reversed(data[0].split()):
            if offset >= 20:
                break
            try:
                """
                if self.index == None or self.index < int(num):
                    self.index = int(num)
                elif self.index >= int(num):
                    continue
                """
                if int(num) in self.indices:
                    pass
                else:
                    self.indices.append(int(num))
                res, uid = self.serv.fetch(num, '(UID)')
                uid = self.parseUid(uid[0].decode("utf-8"))
                typ, data = self.serv.fetch(num, '(RFC822)')
                text = data[0][1].decode('utf-8')
                message = email.message_from_string(text)
                t = message.get('date')
                timeStruct = time.strptime(t, "%a, %d %b %Y %H:%M:%S %z")
                timestamp = time.mktime(timeStruct)
                localTime = time.localtime(timestamp)
                strTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
                real_time = self.utc.localize(datetime.datetime.now())
                mail_time = datetime.datetime.strptime(t, "%a, %d %b %Y %H:%M:%S %z")
                if real_time - datetime.timedelta(days = 1) >= mail_time:
                    offset += 1
                content = self.parseBody(message)     
                if re.search('Student registration', content):
                    print(num)
                    content = re.sub('\r\n', ' ', content)
                    name = re.search(r'Hello\s+(.+?),', content).group(1)
                    #dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    item = {
                        'mailId': uid,
                        'name': name,
                        'content': content,
                        'add_date': strTime
                    }
                    yield item
            except:
                print('Error')
                continue


    def dataFormatting(self, item):
        for key in item.keys():
            item[key] = pymysql.escape_string(item[key])
        return item

    def insertAndUpdate(self, item):
        iemm = self.dataFormatting(item)
        keys = ', '.join(item.keys())
        values = ', '.join((value.join(('"', '"'))) for value in item.values())
        insert_sql = u"""INSERT INTO efetcher_contentmail({keys})
                        VALUES ({values}) ON DUPLICATE KEY UPDATE""".format(keys = keys, values = values)
        update = ','.join([u' {key} = "{value}"'.format(key = key, value = item[key]) for key in item.keys()])
        insert_sql += update
        try:
            self.cursor.execute(insert_sql)
            self.db.commit()
            return 1
        except:
            self.db.rollback()
            print("Insert Error")
            print("The failled sql is %s" % insert_sql)
            return -1

    def begin(self):
        while True:
            print("获取开始！")
            try:
                for item in self.getMail():
                    self.insertAndUpdate(item)
                print("获取完毕！")
            except:
                print("获取失败")
            time.sleep(60)
        serv.close()
        serv.logout()





host = "imappro.zoho.com"
port = "993"
username = "post@mail.shanl.in"
pwd = "1000aFgh"

fetcher = Fetcher(host, username, pwd, port)
fetcher.begin()