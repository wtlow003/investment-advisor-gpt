import requests
import uuid
import time

import chainlit as cl

BASE_URL: str = "http://web:8000/chat"


@cl.on_chat_start
async def init():
    time.sleep(30)
    # make first initial call to server to retrieve agent's greeting
    user_id = str(uuid.uuid4())
    cl.user_session.set("user_id", user_id)
    resp = requests.post(BASE_URL + "/" + user_id, json={"message": ""})
    data = resp.json()
    processed_msg = data["raw_message"]
    # remove prefix
    processed_msg = " ".join(processed_msg.split(": ")[1:])
    if "<END_OF_TURN>" in processed_msg:
        processed_msg = processed_msg.removesuffix(" <END_OF_TURN>")
    elif "<END_OF_CALL>" in processed_msg:
        processed_msg = processed_msg.removesuffix(" <END_OF_CALL>")
    msg = cl.Message(content=processed_msg)
    await msg.send()


@cl.on_message
async def main(message: str):
    # retrieve user_id
    user_id = cl.user_session.get("user_id")

    # send user's input
    resp = requests.post(BASE_URL + "/" + user_id, json={"message": message})
    data = resp.json()
    processed_msg = data["raw_message"]
    # remove prefix
    processed_msg = " ".join(processed_msg.split(": ")[1:])
    if "<END_OF_TURN>" in processed_msg:
        processed_msg = processed_msg.removesuffix(" <END_OF_TURN>")
    elif "<END_OF_CALL>" in processed_msg:
        processed_msg = processed_msg.removesuffix(" <END_OF_CALL>")
    msg = cl.Message(content=processed_msg)
    await msg.send()
