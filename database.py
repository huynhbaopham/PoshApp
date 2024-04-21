import streamlit as st
from supabase import create_client, Client
from datetime import datetime, time, timezone


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# supabase = init_connection()


# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
# @st.cache_data(ttl=600)
# def run_query():
#     return supabase.table("mytable").select("*").execute()

def get_client(phone):
    conn = init_connection()
    data, _ = conn.table("Client").select("id", "fname", "point").eq("phone", phone).execute()
    return data[1]

def insert_client(phone):
    conn = init_connection()
    try:
        data, _ = conn.table("Client").insert({"phone": phone, "point": 0}).execute()
        return data[1]
    except:
        return None

def insert_visit(client_id, services):
    conn = init_connection()
    try:
        data, _ = conn.table("Client").insert({"service": services, "client_id": client_id}).execute()
        return data[1]
    except:
        return None

def checkin(phone, services):
    conn = init_connection()
    # get client data from checkin or signup
    client = get_client(phone)
    if client.empty():
        client = insert_client(phone)

    client_id = client[0]["id"]


        # client exists in DB
        if r != None:
            conn.execute(
                f"SELECT * FROM CheckIns WHERE DATE(dateTime)=CURDATE() and phoneNumber={phone};"
            )
            # new checkin of an active session
            if conn.fetchone() == None:
                conn.execute(
                    f"UPDATE Clients SET points={r[1]+1} WHERE phoneNumber={phone}"
                )
                # insert checkin input
                if len(services) == 0:
                    conn.execute(
                        f"INSERT INTO CheckIns (phoneNumber) VALUES ({phone});"
                    )
                else:
                    services = ", ".join(services)
                    conn.execute(
                        f"INSERT INTO CheckIns (phoneNumber, services) VALUES ({phone}, '{services}');"
                    )

    except:
        conn.close()
        return -1

    conn.close()
    return r


def signup(client):
    db = poshdb_connect()
    conn = db.cursor()

    try:
        conn.execute(
            f"SELECT firstName, points FROM Clients WHERE phoneNumber={client[0]};"
        )
        c = conn.fetchone()
        if c != None:
            conn.close()
            checkin(phone=client[0], services=client[-1], client=c)
            return 0, c

        conn.execute(
            """
                     INSERT INTO Clients (phoneNumber, firstName, lastName, birthdate)
                     VALUES (%s, %s, %s, %s)
                     """,
            client[:-1],
        )
        # insert checkin input
        if len(client[-1]) == 0:
            conn.execute(f"INSERT INTO CheckIns (phoneNumber) VALUES ({client[0]});")
        else:
            services = ", ".join(client[-1])
            conn.execute(
                f"INSERT INTO CheckIns (phoneNumber, services) VALUES ({client[0]}, '{services}');"
            )

    except:
        conn.close()
        return -1, None

    conn.close()
    return 1, None


def get_checkins(sdate, edate):
    sdate = datetime.combine(sdate, time.fromisoformat("00:00:01-07:00")).astimezone()
    edate = datetime.combine(edate, time.fromisoformat("23:59:59-07:00")).astimezone()

    db = poshdb_connect()
    conn = db.cursor()

    try:
        conn.execute(
            f"SELECT CONCAT(firstName, ' ', lastName) as name, birthdate, points, Clients.phoneNumber, services, dateTime FROM Clients, CheckIns WHERE Clients.phoneNumber = CheckIns.phoneNumber AND dateTime BETWEEN '{sdate}' AND '{edate}';"
        )
        clients = conn.fetchall()
        conn.close()
    except:
        conn.close()
        return -1
    return clients





def updateClientInfo(edited_rows, df):
    instances = []
    rows = edited_rows.keys()
    for row in rows:
        phone = df.at[row, "phoneNumber"]
        changes = map(lambda i: f"{i[0]}='{i[1]}'", edited_rows[row].items())
        changes = ", ".join(list(changes))
        instances.append((changes, phone))

    cmds = [f"UPDATE Clients SET {i[0]} WHERE phoneNumber={i[1]};" for i in instances]
    db = poshdb_connect()
    conn = db.cursor()
    try:
        for cmd in cmds:
            conn.execute(cmd)
        conn.close()
        print("success")
        return
    except:
        conn.close()
        print("fail")
        return -1


def redeemDB(points: list, phones: list):
    db = poshdb_connect()
    conn = db.cursor()
    try:
        [
            conn.execute(
                f"UPDATE Clients SET points={point} WHERE phoneNumber={phone};"
            )
            for point, phone in zip(points, phones)
        ]
        conn.close()
        print("success")
        return
    except:
        conn.close()
        print("fail")
        return -1
