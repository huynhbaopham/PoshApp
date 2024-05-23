from logging import PlaceHolder
from google.protobuf.message import Message
import streamlit as st
from streamlit_option_menu import option_menu
import calendar
from datetime import datetime
from database import get_client, insert_client, insert_visit, update_point
from messaging import send_sms_with_status


# ---------------Settings -----------------

page_title = "Posh Lounge | Check In"
page_icon = "💅"
layout = "centered"


# -----------------------------------------

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="collapsed",
)
st.title("Welcome to Posh Nail Lounge")

# ----- HIDE Streamlit Style --------------

hide_st_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility:hidden;}
        header {visibility:hidden;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)


# ---------Functions & Callbacks --------
service_options = (
    "Pedicure",
    "Reg. Manicure",
    "Gel Manicure",
    "Liquiq full set",
    "Liquiq Fill",
    "Full set",
    "Fill",
    "Dip",
    "Wax",
)

signup_msg = "Welcome to Posh Nail Lounge. Sign up to earn points & receive rewards. https://poshnails.streamlit.app/Sign_Up"
notified_msg = lambda s: f"Hi {s}, welcome to Posh Nail Lounge. You're checked in!\nReply with REMOVE to take yourself off our list."

def phone_validated(phone):
    phone_digit = "".join(filter(str.isdigit, phone))
    return len(phone_digit) == 10

def submitted(container):
    phone = st.session_state.get("phone")
    services = st.session_state.get("services")
    # notified = st.session_state.get("notified")

    if not phone_validated(phone):
        container.warning(f"{phone}: Invalid phone number", icon="⚠️")
        return

    client = get_client(phone)
    if client == None:
        sms_success = send_sms(phone, signup_message)
        if not sms_success:
            container.warning(f"{phone}: Invalid phone number", icon="⚠️")
            return
        client = insert_client(phone)[0]

    insert_visit(client["id"], services)
    update_point(phone, client["point"]+1)
    # if notified:
    #     msg = f"Hi {client["fname"]}! {notified_OptIn_message}"
        # send_sms(phone, msg)

    st.session_state.phone = ""
    st.session_state.services = []
    st.session_state.notified = False
    container.success(f"Welcome, {client["fname"]}!")
    return


# --------------- Nav Bar -----------------

selected = option_menu(
    menu_title=None,
    options=["Check In"],
    icons=["box-arrow-in-left"],
    orientation="horizontal",
    styles={
        "icon": {"font-size": "20px"},
        "nav-link": {"font-size": "20px"},
    },
)

# ------- Input & Save periods ----

box = st.empty()
checkin = box.container(border=True)

checkin.text_input(
    label="Phone Number",
    placeholder="(480) 590-6703",
    max_chars=16,
    key="phone",
)
checkin.multiselect(
    label="Services",
    options=service_options,
    placeholder="Choose your service(s)",
    key="services",
)
checkin.checkbox("Text me when it's my turn!", key="notified", disabled=True)
clicked = checkin.button(
    "Submit",
    type="primary",
    use_container_width=True,
)
if clicked:
    phone = st.session_state.get("phone")
    services = st.session_state.get("services")
    notified = st.session_state.get("notified")
    valid = True
    status = "unverified"

    # invalid input
    if not phone_validated(phone):
        checkin.warning(f"{phone}: Invalid phone number", icon="⚠️")
        valid = False

    client = get_client(phone)
    # new client
    if client == None:
        signup_sent_status = send_sms_with_status(phone, signup_msg)

        if signup_sent_status == "invalid":
            checkin.warning(f"{phone}: Invalid phone number", icon="⚠️")
            valid = False

        if signup_sent_status == "undelivery":
            checkin.warning(f"{phone}: Unreachable phone number", icon="⚠️")
            valid = False

        # Unsubscribed number, still add to db, no text to rejoin for now
        if signup_sent_status == "failed":
            status = "unsubscribed"
            valid = True

        # new client, valid number, insert to db with default profile
        if valid:
            client = insert_client(phone, status)[0]

    # With client existing or new default profile added
    if client != None and valid:
        if notified:
            if client["status"] == "unsubscribed":
                box.success(f"Welcome, {client["fname"]}!")
                box.warning("Your phone number is unsubscribed.", icon="⚠️")
                box.warning("Please text START to ‭+1 (602) 806-7782‬ to re-join.", icon="⚠️")
                notified_status = "unsubscribed"
            else:
                notified_sent_status = send_sms_with_status(phone, notified_msg(client["fname"]))
                box.success(f"Welcome, {client["fname"]}!")
                notified_status = "sms"
        else:
            box.success(f"Welcome, {client["fname"]}!")
            notified_status = "waiting"

        insert_visit(client["phone"], client["id"], services, status=notified_status)
