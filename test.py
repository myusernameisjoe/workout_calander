import unittest
import requests
import time
import logging
from app import app, db, Event, Rule

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestWorkoutPlanner(unittest.TestCase):
    BASE_URL = 'http://127.0.0.1:5000'

    @classmethod
    def setUpClass(cls):
        # Start the Flask app in a separate thread
        import threading
        threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False}).start()
        time.sleep(2)  # Give the server more time to start

    def setUp(self):
        # Clear the database before each test
        with app.app_context():
            db.drop_all()
            db.create_all()

    def test_add_events_with_rule_violation(self):
        # Add a rule
        rule_data = {
            'tag1': 'running',
            'tag2': 'swimming',
            'minDays': 2
        }
        response = requests.post(f'{self.BASE_URL}/rules', json=rule_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertTrue(response.json()['success'])

        # Add first event
        event1_data = {
            'title': 'Morning Run',
            'date': '2023-06-01',
            'tags': ['running']
        }
        response = requests.post(f'{self.BASE_URL}/events', json=event1_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertTrue(response.json()['success'])

        # Try to add second event that violates the rule
        event2_data = {
            'title': 'Afternoon Swim',
            'date': '2023-06-02',
            'tags': ['swimming']
        }
        response = requests.post(f'{self.BASE_URL}/events', json=event2_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertFalse(response.json()['success'])

        # Add second event that doesn't violate the rule
        event2_data['date'] = '2023-06-04'
        response = requests.post(f'{self.BASE_URL}/events', json=event2_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertTrue(response.json()['success'])

    def test_update_event_with_rule_violation(self):
        # Add a rule
        rule_data = {
            'tag1': 'weightlifting',
            'tag2': 'yoga',
            'minDays': 3
        }
        response = requests.post(f'{self.BASE_URL}/rules', json=rule_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")

        # Add two events
        event1_data = {
            'title': 'Weightlifting Session',
            'date': '2023-06-01',
            'tags': ['weightlifting']
        }
        response = requests.post(f'{self.BASE_URL}/events', json=event1_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        event1_id = response.json()['event']['id']

        event2_data = {
            'title': 'Yoga Class',
            'date': '2023-06-05',
            'tags': ['yoga']
        }
        response = requests.post(f'{self.BASE_URL}/events', json=event2_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")

        # Try to update first event to violate the rule
        update_data = {
            'date': '2023-06-03'
        }
        response = requests.put(f'{self.BASE_URL}/events/{event1_id}', json=update_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertFalse(response.json()['success'])

        # Update first event without violating the rule
        update_data['date'] = '2023-06-02'
        response = requests.put(f'{self.BASE_URL}/events/{event1_id}', json=update_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertTrue(response.json()['success'])

    def test_delete_event_and_rule(self):
        # Add a rule
        rule_data = {
            'tag1': 'cycling',
            'tag2': 'running',
            'minDays': 1
        }
        response = requests.post(f'{self.BASE_URL}/rules', json=rule_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        rule_id = response.json()['rule']['id']

        # Add an event
        event_data = {
            'title': 'Morning Ride',
            'date': '2023-06-01',
            'tags': ['cycling']
        }
        response = requests.post(f'{self.BASE_URL}/events', json=event_data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        event_id = response.json()['event']['id']

        # Delete the event
        response = requests.delete(f'{self.BASE_URL}/events/{event_id}')
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertTrue(response.json()['success'])

        # Verify event is deleted
        response = requests.get(f'{self.BASE_URL}/events')
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertEqual(len(response.json()), 0)

        # Delete the rule
        response = requests.delete(f'{self.BASE_URL}/rules/{rule_id}')
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertTrue(response.json()['success'])

        # Verify rule is deleted
        response = requests.get(f'{self.BASE_URL}/rules')
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        self.assertEqual(len(response.json()), 0)

if __name__ == '__main__':
    unittest.main()