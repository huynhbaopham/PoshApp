# import streamlit as st
from twilio.base.exceptions import TwilioException
from twilio.rest import Client
from datetime import date
import json
import toml
from time import sleep, time


# @st.cache_resource
def sms_client():
    path = ".streamlit/secrets.toml"
    with open(path, "r") as f:
        data = toml.load(f)
    account_sid = data["AID"]
    auth_token = data["TOKEN"]
    sid = data["SID"]
    vid = data["VID"]
    return Client(account_sid, auth_token), sid, vid


def send_sms(phone, msg):
    client, sid, _ = sms_client()
    try:
        message = client.messages.create(
            body=msg, messaging_service_sid=sid, to=f"+1{phone}"
        )
        return message

    # invalid phone number
    except TwilioException as e:
        print(e)
        return None


# mid=SM8064c9e8c74076f902e636e0b9ee768f
def retrieve_status(mid):
    client, sid, _ = sms_client()
    messages = client.messages(mid).fetch()
    return messages


def get_if_response(phone):
    client, sid, _ = sms_client()
    messages = client.messages.list(
        date_sent=date.today(), from_=f"+1{phone}", limit=20
    )
    return messages


def send_sms_with_status(phone, msg, thres=5):
    status = ["delivered", "read", "failed", "undelivered"]
    message = send_sms(phone, msg)
    if message == None:
        return "invalid"

    # listen to status within threshold interval (5s)
    start = time()
    while time() - start < 5 and message.status not in status:
        message = retrieve_status(message.sid)

    # if message.status in ["failed", "undelivered"]:
    #     print(message.error_message)
    return message.status


def verify_send_token(phone):
    client, _, vid = sms_client()
    try:
        verified = client.verify.v2.services(vid).verifications.create(
            to=f"+1{phone}", channel="sms"
        )
        return verified.status

    # invalid phone number
    except TwilioException as e:
        print(e)
        return None


def verify_check_token(phone, code):
    client, _, vid = sms_client()
    verified = client.verify.v2.services(vid).verification_checks.create(
        to=f"+1{phone}", code=code
    )

    return verified.status


def main():
    # msg = "Welcome to Posh Nail Lounge. Sign up to earn points & receive rewards.\nhttps://poshnails.streamlit.app/Sign_Up"
    # notified_msg = (
    #     lambda s: f"Hi {s}, welcome to Posh Nail Lounge. You're checked in!\nReply with REMOVE to take yourself off our list."
    # )

    # status = send_sms_with_status("9077929565", notified_msg("Beautiful"))
    # print(f"Status is {status}")
    #
    verify_send_token("9990000000")
    code = input()
    # print(verify_check_token("9990000000", code))


if __name__ == "__main__":
    main()
