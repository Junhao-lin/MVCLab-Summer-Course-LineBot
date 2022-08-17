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
load_dotenv()
app = FastAPI()

CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')
CHANNEL_ID = os.getenv('LINE_UID') 
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
My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key

# Line Developer webhook Entry powerpoint
@app.post('/')
async def callback(request: Request):
    body = await request.body() # Get request
    signature = request.headers.get('X-Line-Signature', '') # Get message signature from Line Server
    try:
        handler.handle(body.decode('utf-8'), signature) # Handler handle any message from LineBot and 
    except InvalidSignatureError:
        raise HTTPException(404, detail='LineBot Handle Body Error !')
    return 'OK'
# All message events are handling at here !
@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
    message = TextSendMessage(text= event.message.text)
    message.text = re.sub("=","",message.text)
    if ChekExpression(message.text):
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(text = eval(message.text))
        )
    else:
        url = 'https://truth.bahamut.com.tw/s01/201908/e9e7205639db85adff92d071cb44f997.PNG'
        My_LineBotAPI.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=url,
                preview_image_url=url)
        )
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app', reload=True, host='0.0.0.0', port=1234)