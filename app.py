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

is_update_session = False


@app.route("/")
def index() -> str:
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


def get_count() -> int:
    data = db_session.query(Data.count, Data.timestamp).first()
    return data.count


def update_count(new_count: int) -> None:
    data = db_session.query(Data).filter(Data.id == 1)
    data.update({"count": new_count})
    db_session.commit()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event) -> None:
    global is_update_session
    received_text: str = event.message.text
    if is_update_session:
        if received_text.isdecimal():
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=f"人数を{received_text}人に更新しました")
            )
            update_count(int(received_text))
            is_update_session = False
        elif received_text == "人数を取得する":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=f"現在の人数は{str(get_count())}人です")
            )
            is_update_session = False
        elif received_text == "人数を更新する":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="人数を半角数字で入力してください")
            )
            is_update_session = True
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="正しい形式で再入力してください")
            )
    else:
        if received_text == "人数を取得する":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=f"現在の人数は{str(get_count())}人です")
            )
        elif received_text == "人数を更新する":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="人数を半角数字で入力してください")
            )
            is_update_session = True
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="リッチメニューから選択してください")
            )


if __name__ == "__main__":
    app.run()
