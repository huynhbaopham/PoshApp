import streamlit as st
from streamlit_option_menu import option_menu
import calendar
from datetime import date, timedelta

from twilio.rest.verify import Verify
from database import *
from messaging import verify_send_token, verify_check_token


# ---------------Settings -----------------

page_title = "Posh Lounge | Sign Up"
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

# ----- session variables ----
years = [
    date.today() - timedelta(days=100 * 365.25),
    date.today() - timedelta(days=16 * 365.25),
]


# ---------Function & Callbacks --------
def phone_validated(phone):
    phone_digit = "".join(filter(str.isdigit, phone))
    return len(phone_digit) == 10


def token_validated(token):
    phone_digit = "".join(filter(str.isdigit, token))
    return len(phone_digit) == 6


def name_validated(name):
    return name.isalpha()


def birthdate_validated(birthdate):
    if birthdate is None:
        return False
    return birthdate <= years[1]


# --------------- Nav Bar -----------------
selected = option_menu(
    menu_title=None,
    options=["Sign Up"],
    icons=["plus-square"],
    orientation="horizontal",
    styles={
        "icon": {"font-size": "20px"},
        "nav-link": {"font-size": "20px"},
    },
)
# ------- Input & Save periods ----
box = st.empty()
signup = box.container(border=True)
col1, col2 = signup.columns(2)
fname = col1.text_input(
    label="First name",
    value="",
    placeholder="Pretty",
    max_chars=20,
    key="fname",
)
lname = col2.text_input(
    label="Last Name",
    value="",
    placeholder="Bella",
    max_chars=20,
    key="lname",
)
phone = signup.text_input(
    label="Phone Number",
    value="",
    placeholder="(480) 590-6703",
    max_chars=16,
    key="phone",
)

birthdate = signup.date_input(
    label="Birthdate",
    value=years[1],
    format="YYYY-MM-DD",
    min_value=years[0],
    max_value=date.today(),
    key="birthdate",
)
clicked = signup.button("Submit", type="primary", use_container_width=True)
valid = False

if clicked:
    valid = True
    if not phone_validated(phone):
        st.warning(f"{phone}: Invalid phone number", icon="⚠️")
        valid = False

    if not name_validated(fname):
        st.warning(f"{fname}: Invalid first name. Only alphabet allowed.", icon="⚠️")
        valid = False

    if not name_validated(lname):
        st.warning(f"{lname}: Invalid last name. Only alphabet allowed.", icon="⚠️")
        valid = False

    if not birthdate_validated(birthdate):
        st.warning(
            f"{birthdate}: Invalid birthdate name. Must be 16 or older.", icon="⚠️"
        )
        valid = False

    client = get_client(phone) if valid else None

    # if client != None:
    #     st.warning(f"{phone}: Existing client. Sign in here.", icon="⚠️")
    #     valid = False

    verified = verify_send_token(phone) if valid else None

    if valid and verified == None:
        st.warning(f"{phone}: Invalid phone number.", icon="⚠️")
        valid = False

if valid:
    box.empty()
    otp = st.container(border=True)
    # box.success(f"Welcome to Posh Nail Lounge, {fname}!")
    token = otp.text_input(
        label="One time passcode", value="", max_chars=6, key="token"
    )
    otp_sent = otp.button("Send", type="primary", use_container_width=True)
    if otp_sent:
        while verify_check_token(phone, token) != "approved":
            otp.success("Invalid OTP code!")

        otp.success(f"Welcome to Posh, {fname}!")

    # otp = box.container()
    # token = box.text_input(
    #     label="One time passcode", value="", max_chars=6, key="token"
    # )
    # if box.button("Send", type="primary", use_container_width=True):
    #     if verify_check_token(phone, token) == "approved":
    #         box.success(f"Welcome to Posh Nail Lounge, {fname}!")
