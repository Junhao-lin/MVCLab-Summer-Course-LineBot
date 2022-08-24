'''
This is my LineBot API
How to Start:
    > Step 0. Go to ./MVCLab-Summer-Course/LineBot/
        > cd ./MVCLab-Summer-Course/LineBot
    > Step 1. Install Python Packages
        > pip install -r requirements.txt
    > Step 2. Run main.py
        > python main.py
Reference:
1. LineBot API for Python
    > https://github.com/line/line-bot-sdk-python
2. Pokemon's reference
    > https://pokemondb.net/pokedex/all
3. Line Developer Messaging API Doc
    > https://developers.line.biz/en/docs/messaging-api/
'''
import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from influxdb import InfluxDBClient
"""
init DB
"""
class DB():
    def __init__(self, ip, port, user_id, password, db_name):
        self.client = InfluxDBClient(ip, port, user_id, password, db_name)
        print('Influx DB init.....')

    def insertData(self, data):
        """
        [data] should be a list of datapoint JSON,
        "measurement": means table name in db
        "tags": you can add some tag as key
        "fields": data that you want to store
        """

        if self.client.write_points(data):
            return True
        else:
            print('Falied to write data')
            return False

    def queryData(self, query):
        """
        [query] should be a SQL like query string
        """
        return self.client.query(query)
# Init a Influx DB and connect to it
db = DB('0.0.0.0', 8086, 'root', '', 'accounting_db')

load_dotenv()
app = FastAPI()

CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')

My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key
'''
For first testing, you can comment the code below after you check your linebot can send you the message below
'''
CHANNEL_ID = os.getenv('LINE_UID') # For any message pushing to or pulling from Line Bot using this ID
def ChekExpression(string):
    check_result = True   # 標誌位

    if not string.count("(") == string.count(")"):   # 檢查括號是否完整
        print("輸入錯誤，未匹配到完整括號!")
        check_result = False

    if re.findall('[A-Za-z#@!~^&_]+', string.lower()):   # 檢查是否包含字母
        print("輸入錯誤，包含非法字符!")
        check_result = False

    if string.count("/")!=0 and string.split('/')[1] == '0':
        print("輸入錯誤，被除數等於 0")
        check_result = False

    return check_result

# Line Developer Webhook Entry Point
@app.post('/')
async def callback(request: Request):
    body = await request.body() # Get request
    signature = request.headers.get('X-Line-Signature', '') # Get message signature from Line Server
    try:
        handler.handle(body.decode('utf-8'), signature) # Handler handle any message from LineBot and 
    except InvalidSignatureError:
        raise HTTPException(404, detail='LineBot Handle Body Error !')

    return 'OK'
# Events for message reply
my_event = ['#calculator', '#help', '#note', '#report', '#delete', '#drop','#sum']
# All message events are handling at here !
@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
    recieve_message = str(event.message.text).split(' ')
    case_ = recieve_message[0].lower().strip()
    #Case 1: calculator
    if re.match(my_event[0], case_):
        if len(recieve_message) < 1:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text = '請輸入數值' )
            )
        else:
            message = recieve_message[1]
            message = re.sub("=","",message)
            if ChekExpression(message):
                My_LineBotAPI.reply_message(
                    event.reply_token,
                    TextSendMessage(text = eval(message))
                )
            else:
                url = 'https://truth.bahamut.com.tw/s01/201908/e9e7205639db85adff92d071cb44f997.PNG'
                My_LineBotAPI.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        original_content_url=url,
                        preview_image_url=url)
                )
    # Case 2: help
    elif re.match(my_event[1], case_):
        command_describtion = 'Commands:\n\
        #calculator <formula>\n\t-->four fundamental operations of arithmetic\n\
        #note [事件] [+/-] [錢]\n\t-->add new event\n\
        #report \n\t-->show all event\n\
        #delete <number>\n\t-->Delete an event\n\
        #drop \n\t-->Delete all event\n\
        #sum \n\t-->print one day total money'
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(text=command_describtion)
        )

    # Case 3: note
    elif re.match(my_event[2], case_):
        # cmd: #note [事件] [+/-] [錢]
        if len(recieve_message) != 4:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Wrong input"
                )
            )
            return
        event_ = recieve_message[1]
        op = recieve_message[2]
        money = int(recieve_message[3])
        # process +/-
        if op == '-':
            money *= -1
        # get user id
        user_id = event.source.user_id
        # build data
        data = [
            {
                "measurement" : "accounting_items",
                "tags": {
                    "user": str(user_id),
                    # "category" : "food"
                },
                "fields":{
                    "event": str(event_),
                    "money": money
                }
            }
        ]
        if db.insertData(data):
            # successed
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Write to DB Successfully!"
                )
            )
    # Case 4:report
    elif re.match(my_event[3], case_):
        # get user id
        user_id = event.source.user_id
        query_str = """
        select * from accounting_items
        """
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        print(result)
        reply_text = ''
        for i, point in enumerate(points):
            time = point['time']
            event_ = point['event']
            money = point['money']
            reply_text += f'[{i}] -> [{time}] : {event_}   {money}\n'
        if len(reply_text) != 0:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=reply_text
                )
            )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='No data'
                )            
    # Case 5: delete
    elif re.match(my_event[4], case_):
        if len(recieve_message)!=2:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='Wrong input'
                )
            )
            return
        user_id = event.source.user_id
        items = recieve_message[1]
        query_str = """
        select * from accounting_items
        """
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        time_tmp = []
        for i, point in enumerate(points):
            time = point['time']
            time_tmp.append(time)      

        if int(items) == 0 and len(time_tmp) == 1:
            db.queryData('drop measurement accounting_items')
        elif int(items) == 0 and len(time_tmp) != 1:
            db.queryData(f"delete from accounting_items where time < '{time_tmp[int(items) + 1]}' -1ms")
        elif int(items) == len(time_tmp) - 1:
            db.queryData(f"delete from accounting_items where time > '{time_tmp[int(items) -1]}' +1ms")
        else:
            db.queryData(f"delete from accounting_items where time < '{time_tmp[int(items) + 1]}' -1ms and time > '{time_tmp[int(items) -1]}' +1ms")  

        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        reply_text = ''
        for i, point in enumerate(points):
            time = point['time']
            event_ = point['event']
            money = point['money']
            reply_text += f'[{i}] -> [{time}] : {event_}   {money}\n'
        if len(reply_text) != 0:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=reply_text
                )
            )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='No data'
                )
            )
    # Case 6: deleteall
    elif re.match(my_event[5], case_):
        db.queryData('drop measurement accounting_items')
    # Case 7: sum  
    elif re.match(my_event[6], case_):
        query_str = """
            select * from accounting_items where time > now() - 1d 
        """
        user_id = event.source.user_id        
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        total = 0
        for i, point in enumerate(points):
            money = point['money']
            total += money
        My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text= f"Total spend today : {total} 元"
                )
            )
    else:
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(text='Welcome to my pokedex ! Enter "#help" for commands !')
        )
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app', reload=True, host='0.0.0.0', port=1234)