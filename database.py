# import streamlit as st
from supabase import create_client, Client
from datetime import datetime, time, timezone
import toml


# @st.cache_resource
def init_connection():
    path = ".streamlit/secrets.toml"
    with open(path, "r") as f:
        data = toml.load(f)
    url = data["SUPABASE_URL"]
    key = data["SUPABASE_KEY"]
    # url = st.secrets["SUPABASE_URL"]
    # key = st.secrets["SUPABASE_KEY"]
    db = create_client(url, key)
    return db


def get_client(phone):
    db = init_connection()
    try:
        data, _ = db.table("Client").select("*").eq("phone", phone).single().execute()
        return data[1]
    except:
        return None


# @st.cache_data(ttl=600)
def insert_client(phone, status="unverified"):
    conn = init_connection()
    data, _ = (
        conn.table("Client")
        .insert({"fname": "Beautiful", "phone": phone, "point": 0, "status": status})
        .execute()
    )
    return data[1]


# @st.cache_data(ttl=600)
def insert_visit(phone, client_id, services, status="waiting"):
    conn = init_connection()
    data, _ = (
        conn.table("Active")
        .upsert(
            {
                "phone": phone,
                "service": services,
                "client_id": client_id,
                "status": status,
            }
        )
        .execute()
    )
    return data[1]


# @st.cache_data(ttl=600)
def update_point(phone, point):
    conn = init_connection()
    data, _ = conn.table("Client").update({"point": point}).eq("phone", phone).execute()
    return data[1]


def main():
    phone = "9077929565"
    service = ["fill"]

    client = get_client(phone)

    if client == None:
        return ("Please sign up!")

    point = client['point'] + 1

    new_check_in = insert_visit(phone, client["id"], service)
    update_point(phone, client["point"]+1)

    print(client)
    #

    # dict = {'created_at': '2024-04-14T03:45:19.57452+00:00',
    #     'fname': 'Evan',
    #     'lname': 'Pham',
    #     'point': 43,
    #     'phone': '9077929565',
    #     'id': 'a463dc6a-ed1c-4202-9cef-6bf4d67e6660',
    #     'birthdate': '1994-05-04',
    #     'status': 'unsubscribed'}

    # print (dict['fname'])


if __name__ == "__main__":
    main()
