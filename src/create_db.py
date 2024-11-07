import sqlite3
import constants as const
import json

def main():
    con = sqlite3.connect(const.DB_NAME)
    try:
        cur = con.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS objects (
                object_id TEXT PRIMARY KEY,
                object_type TEXT NOT NULL,
                object_data TEXT NOT NULL
            )
        ''')
        con.commit()  

        genesis_block_id = const.GENESIS_BLOCK_ID
        genesis_block_data = json.dumps(const.GENESIS_BLOCK) 
        cur.execute("SELECT 1 FROM objects WHERE object_id = ?", (genesis_block_id,))
        if cur.fetchone() is None:
            cur.execute('''
                INSERT INTO objects (object_id, object_type, object_data)
                VALUES (?, ?, ?)
            ''', (genesis_block_id, "block", genesis_block_data))
            con.commit()  

    except Exception as e:
        con.rollback() 
        print(str(e))
    finally:
        con.close()  


if __name__ == "__main__":
    main()
