from unittest import TestCase

import env
from api.payload import Payload


class TestPayload(TestCase):

    def setUp(self):
        self.json = {'ref': 'origin/foo',
                     'repository': 'bar'}

        self.payload = Payload(self.json)

    def test_payload_validate(self):
        self.assertFalse(self.payload.validate('baz'))
        self.assertTrue(self.payload.validate('foo'))

    def test_payload_get(self):
        self.assertEqual(self.payload.get('repository'), 'bar')
        self.assertIsNone(self.payload.get('foo'))

    def test_payload_as_dict(self):
        self.assertEqual(self.payload.as_dict, self.json)

