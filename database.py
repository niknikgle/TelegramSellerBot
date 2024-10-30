import sqlite3
import time

orders = []

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()
cur.execute(
    f"CREATE TABLE IF NOT EXISTS accs(name, price, img TEXT UNIQUE primary key, login, password, desc)"
)
cur.execute(
    f"CREATE TABLE IF NOT EXISTS users(user_id TEXT UNIQUE primary key, address TEXT, balance)"
)

cur.execute(
    f"CREATE TABLE IF NOT EXISTS payments(user_id INTEGER, order_id primary key, amount, time INT)"
)


def get_accounts():
    res = cur.execute("SELECT name, price, img, login, password, desc FROM accs")

    data = res.fetchall()
    return data


def user_wallet(user_id, wallet_address):
    data = [user_id, wallet_address, 0]
    cur.execute(f"INSERT OR IGNORE INTO users VALUES(?, ?, ?)", data)
    con.commit()


def find_users_balance(user_id):
    users_res = cur.execute(f"SELECT balance FROM users WHERE user_id = {user_id}")

    users_wallet = users_res.fetchone()[0]

    return users_wallet


def add_balance(address, value_coin):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Step 2: Write the SQL query to update the wallet balance where the address matches
    sql_query = """UPDATE users 
                   SET balance = ? + balance 
                   WHERE address = ?"""

    # Step 3: Execute the query with the provided address and new_balance
    cursor.execute(sql_query, (value_coin, address))

    # Step 4: Commit the changes to the database
    conn.commit()


def sub_balance(address, value_coin):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Step 2: Write the SQL query to update the wallet balance where the address matches
    sql_query = """UPDATE users 
                   SET balance = balance - ?
                   WHERE address = ?"""

    # Step 3: Execute the query with the provided address and new_balance
    cursor.execute(sql_query, (value_coin, address))

    # Step 4: Commit the changes to the database
    conn.commit()


def delete_bought_item(img):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    delete_stm = f"DELETE FROM accs WHERE img = ?"
    cur.execute(delete_stm, (img,))
    con.commit()


def select_add_orderid_by_user(user_id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM payments WHERE user_id = '1260011714'")
    data = res.fetchall()
    for i in range(len(data)):
        if data[i][1] not in orders:
            orders.append(data[i][1])

    return orders


def add_payment_paypal(user_id, order_id, amount):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    data = [user_id, order_id, amount, time.time()]

    cur.execute(f"INSERT OR IGNORE INTO payments VALUES(?, ?, ?, ?)", data)
    con.commit()


def select_latest_attempt(user_id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    res = cur.execute(
        f"SELECT order_id FROM payments WHERE user_id = {user_id} ORDER BY time DESC"
    )

    return res.fetchone()[0]


def select_latest_attempt_amount(order_id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    order_id = (order_id,)

    res = f"SELECT amount FROM payments WHERE order_id = ? ORDER BY time DESC"
    res = cur.execute(res, order_id)

    return res.fetchone()[0]
