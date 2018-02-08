import os
import sqlite3
from unittest import TestCase, main
from unittest.mock import patch

import env
from api.queue import Queue


class TestQueue(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.queue = Queue('test.db')

    @classmethod
    def tearDownClass(cls):
        os.remove('test.db')

    def tearDown(self):
        self.queue.cursor.execute('DELETE FROM queue')

    def test_queue_created(self):
        create_table = '''
            CREATE TABLE queue
                (id TEXT, payload TEXT, date_added NUMERIC)
        '''

        with self.assertRaises(sqlite3.OperationalError) as exc:
            queue_table = self.queue.cursor.execute(create_table)

    def test_queue_add(self):
        payload = {'test': 123}
        self.queue.add(payload)

        queue = self.queue.cursor.execute('SELECT * FROM queue').fetchall()
        self.assertTrue(len(queue) > 0)

    def test_queue_pop(self):
        payload = {'test': 123}
        self.queue.add(payload)

        work = self.queue.pop()
        self.assertTrue(work.get() == payload)

    def test_queue_pop_no_work(self):
        self.assertIsNone(self.queue.pop())

    @patch('api.queue.Worker.deploy')
    def test_queue_run(self, mock_deploy):
        payload = {'test': 123}
        self.queue.add(payload)

        # Check that work was added to the queue
        queue = self.queue.cursor.execute('SELECT * FROM queue').fetchall()
        self.assertTrue(len(queue) > 0)

        self.queue.run()

        # Check that `Worker.deploy` was called, and work was removed from the
        # queue
        self.assertTrue(mock_deploy.called)
        self.assertIsNone(self.queue.pop())
