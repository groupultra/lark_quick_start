import os
os.environ['APP_ID'] =''
os.environ['APP_SECRET'] = ''
os.environ['VERIFICATION_TOKEN'] = ''
os.environ['ENCRYPT_KEY'] = ''
os.environ['LARK_HOST'] = 'https://open.larksuite.com'
port = 5050

import datetime
import json
import logging
import traceback

import requests
from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify

from api import MessageApiClient
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager, InvalidEventException
from frog_bot import FrogBot
from message import message_factory


# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")

# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()

# feature
bot = FrogBot(message_api_client)

# 记录启动时间，用于过滤历史消息
now = datetime.datetime.now() 


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    try:
        # 过滤掉启动之前的消息
        create_time = datetime.datetime.fromtimestamp(int(req_data.header.create_time) // 1000)
        if create_time < now:
            pass # 历史文件不具备现实意义！
        else:
            msg = message_factory(req_data, message_api_client)
            if msg.is_text and msg.is_group:
                # is group text
                bot.on_group_text_message(msg)
            else:
                pass
    except Exception as e:
        traceback.print_exc()
    finally:
        return jsonify() # 无论如何都要返回200，不然会被lark服务器一直轰炸


@event_manager.register("im.message.reaction.created_v1")
def message_reaction_created_event_handler(req_data):
    try:
        # 过滤掉启动之前的消息
        create_time = datetime.datetime.fromtimestamp(int(req_data.header.create_time) // 1000)
        if create_time < now:
            pass # 历史文件不具备现实意义！
        else:
            msg = message_factory(req_data, message_api_client)
            # TODO: call your function here, such as bot.on_reaction(msg)
    except Exception as e:
        traceback.print_exc()
    finally:
        return jsonify() # 无论如何都要返回200，不然会被lark服务器一直轰炸


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    try:
        # init callback instance and handle
        event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
        if not event_handler:
            return jsonify()
        else:
            return event_handler(event)
    except InvalidEventException:
        return jsonify() # 炸了也要返回200，不然会重试


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
