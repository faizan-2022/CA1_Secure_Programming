"""Create expenses.db with sample data. No real people, no real money."""
import hashlib, os, sqlite3
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")
if os.path.exists(DB):
    os.remove(DB)
c = sqlite3.connect(DB)
c.executescript("""
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, name TEXT, role TEXT);
CREATE TABLE claims (id INTEGER PRIMARY KEY, user_id INTEGER, merchant TEXT,
                     amount REAL, note TEXT, status TEXT);
""")
md5 = lambda p: hashlib.md5(p.encode()).hexdigest()
users = [("jdoe", "password1", "Jane Doe", "staff"),
         ("rsmith", "letmein", "Rob Smith", "staff"),
         ("achen", "Summer2026", "Ada Chen", "finance"),
         ("admin", "admin", "System Admin", "admin")]
for u, p, n, r in users:
    c.execute("INSERT INTO users (username,password,name,role) VALUES (?,?,?,?)",
              (u, md5(p), n, r))
claims = [(1, "Dublin Coach", 24.50, "Client visit", "approved"),
          (1, "Aer Lingus", 310.00, "Conference travel", "pending"),
          (2, "Tesco", 18.20, "Team lunch", "approved"),
          (3, "Hotel Riu", 480.00, "Offsite accommodation", "pending"),
          (4, "Amazon", 129.99, "Spare laptop charger", "approved")]
for cl in claims:
    c.execute("INSERT INTO claims (user_id,merchant,amount,note,status) VALUES (?,?,?,?,'pending')",
              cl[:4])
c.commit()
os.makedirs(os.path.join(os.path.dirname(DB), "receipts"), exist_ok=True)
for i in range(1, 6):
    open(os.path.join(os.path.dirname(DB), "receipts", f"claim-{i}.txt"), "w").write(
        f"Meridian Expenses — receipt for claim {i}\nSample data. Not a real receipt.\n")
print("seeded:", DB)
