import sqlite3


class DBHandler:
    def __init__(self, db_name="merchantpoint.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_name TEXT,
                mcc TEXT,
                address TEXT,
                org_name TEXT,
                org_description TEXT,
                source_url TEXT,
                UNIQUE(mcc, merchant_name, address)
            )
        """)
        self.conn.commit()

    def save_data(self, data):
        try:
            self.cursor.execute("""
                SELECT id FROM merchants 
                WHERE mcc = ? AND merchant_name = ? AND address = ?
            """, (data['mcc'], data['merchant_name'], data['address']))
            existing_record = self.cursor.fetchone()

            if existing_record:
                self.cursor.execute("""
                    UPDATE merchants
                    SET org_description = ?, source_url = ?
                    WHERE id = ?
                """, (data['org_description'], data['source_url'], existing_record[0]))
                result = "updated"
            else:
                self.cursor.execute("""
                    INSERT INTO merchants (merchant_name, mcc, address, org_name, org_description, source_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (data['merchant_name'], data['mcc'], data['address'], data['org_name'], data['org_description'], data['source_url']))
                result = "inserted"
            self.conn.commit()
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "error"

    def close(self):
        self.conn.close()
