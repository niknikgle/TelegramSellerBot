import sqlite3


# Database setup
con = sqlite3.connect("database.db")
cur = con.cursor()

data = [
    "128 skins",
    "25",
    "https://i.imgur.com/kdQNBy4.jpeg",
    "simon884121@vilaisa.com",
    "NikNikGle2009!",
    "Chunky 128 skins acc",
]

cur.execute(f"INSERT OR IGNORE INTO accs VALUES(?, ?, ?, ?, ?, ?)", data)
con.commit()

data = ["1260011714", "MGM2rmhZVZwTgZNF9Rx3sBwNFkVH3kGpS2", 1000]

cur.execute(f"INSERT OR IGNORE INTO users VALUES(?, ?, ?)", data)
con.commit()
