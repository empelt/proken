from itertools import count
from flask import Flask, request, abort
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
from datetime import datetime

from assets.database import db_session
from assets.models import Data

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return "OK"


@app.route("/update_count", methods=["POST"])
def update_count() -> str:
    payload = request.json
    new_count = payload.get("count")
    data = db_session.query(Data).filter(Data.id == 1)
    data.update({"count": new_count})
    db_session.commit()
    return "OK"


@app.route("/callback", methods=["POST"])
def callback() -> str:
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"

async def get_count() -> int:
    data = await db_session.query(Data.count, Data.timestamp).first()
    return data.count

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text=="人数":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=str(get_count()))
        )
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )


if __name__ == "__main__":
    app.run()
