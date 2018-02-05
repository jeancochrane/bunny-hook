# queue.py -- run tasks from a queue
import sqlite3
import time
import json
from uuid import uuid4

from api.worker import Worker


class Queue(object):
    # Default connection string
    db_conn = 'hook.db'

    def __init__(self):
        # Establish persistent database connection
        self.conn = sqlite3.connect(db_conn)
        self.cursor = self.conn.cursor()

        # Create the table if it doesn't exist
        create_table = '''
            CREATE TABLE IF NOT EXISTS queue
                (id TEXT, payload TEXT, date_added NUMERIC)
        '''
        self.cursor.execute(create_table)

    def add(self, payload):
        # Package up the payload and drop it into the queue
        insert = '''
            INSERT INTO queue
                     (id, payload, date_added)
              VALUES (?, ?, ?)
        '''
        self.cursor.execute(insert, (str(uuid4()), json.dumps(payload), time.time()))

    def pop(self):
        # Select the most recent job in the queue
        self.cursor.execute('SELECT * FROM queue ORDER BY date_added LIMIT 1')

        work = self.cursor.fetchone()
        work_id = work[0]

        # Delete the job from the queue
        self.cursor.execute('DELETE FROM queue WHERE id = ?', (work_id,))

        return work

    def run(self):
        while True:
            work = self.pop()
            if work:
                worker = Worker()
                worker.deploy(work)
