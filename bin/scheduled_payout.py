import os
import sys
import datetime
import sqlite3
import pathlib

# Set up app context to reuse send_payment_seller
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from insta485.views.manage import send_payment_seller
import insta485

DB_PATH = os.environ.get("INSTA485_DATABASE", "var/insta485.sqlite3")

def main():
    now = datetime.datetime.now()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Find transactions eligible for auto-payout:
    # - status is 'event_occurred'
    # - No complaint filed
    # - Event time + 1 min < now
    cursor.execute('''
        SELECT t.transaction_id, e.event_datetime, t.status, t.complaint_reason
        FROM transactions t
        JOIN events e ON t.event_id = e.event_id
        WHERE t.status = 'event_occurred' AND (t.complaint_reason IS NULL OR t.complaint_reason = '')
    ''')
    for row in cursor.fetchall():
        event_dt = datetime.datetime.strptime(row['event_datetime'], "%Y-%m-%d %H:%M:%S")
        if now > event_dt + datetime.timedelta(minutes=1):
            print(f"[SCHEDULER] Auto-payout: Transaction {row['transaction_id']} eligible.")
            try:
                send_payment_seller(row['transaction_id'])
            except Exception as e:
                print(f"[SCHEDULER][ERROR] Failed to pay seller for transaction {row['transaction_id']}: {e}")
    conn.close()

if __name__ == "__main__":
    main()
