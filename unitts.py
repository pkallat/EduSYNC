import unittest
from unittest.mock import patch, Mock
from calender import app, authenticate_google_calendar, fetch_events, create_event, delete_event

class TestGoogleCalendarApp(unittest.TestCase):
    """
    Test suite for the Google Calendar application.
    Tests include authentication, event creation, event deletion, and error handling.
    """    
    def setUp(self):
        """
        Set up the test client for Flask and mock credentials.
        """
        app.testing = True  
        self.client = app.test_client()  
    
    @patch('calender.pickle.load')
    @patch('calender.pickle.dump')
    @patch('calender.InstalledAppFlow.from_client_secrets_file')
    @patch('calender.build')
    def test_authenticate_google_calendar_valid_token(self, mock_build, mock_flow, mock_pickle_dump, mock_pickle_load):
        """
        Test the authenticate_google_calendar function when a valid token is available.

        - Mocks the `pickle.load` to simulate a valid token.
        - Mocks `build` to ensure the Google Calendar API is authenticated with the correct credentials.
        """
        mock_pickle_load.return_value = Mock(valid=True, expired=False)
        mock_build.return_value = Mock()
        result = authenticate_google_calendar()
        self.assertIsNotNone(result)
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_pickle_load.return_value)
        
    @patch('calender.pickle.load')
    @patch('calender.pickle.dump')
    @patch('calender.InstalledAppFlow.from_client_secrets_file')
    @patch('calender.build')
    def test_authenticate_google_calendar_no_token(self, mock_build, mock_flow, mock_pickle_dump, mock_pickle_load):
        """
        Test the authenticate_google_calendar function when the token file is not found.

        - Simulates a missing token file (via FileNotFoundError).
        - Mocks `InstalledAppFlow` to simulate the flow for authenticating with Google OAuth.
        - Verifies that the flow triggers the local server for authentication.
        """
        mock_pickle_load.side_effect = FileNotFoundError
        mock_flow.return_value = Mock(run_local_server=Mock(return_value=Mock()))
        result = authenticate_google_calendar()
        mock_flow.return_value.run_local_server.assert_called_once()
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_flow.return_value.run_local_server.return_value)
        
    @patch('calender.authenticate_google_calendar')
    def test_index(self, mock_authenticate):
        """
        Test the index route ("/") of the Flask app.

        - Mocks the `authenticate_google_calendar` function to simulate a successful authentication.
        - Mocks the event fetching API to return predefined events.
        - Verifies that the page returns the correct event data.
        """
        mock_service = Mock()
        mock_authenticate.return_value = mock_service
        mock_service.events.return_value.list.return_value.execute.return_value = {
            'items': [
                {'id': '1', 'summary': 'Sample Event 1', 'start': {'dateTime': '2024-11-23T09:00:00'}},
                {'id': '2', 'summary': 'Sample Event 2', 'start': {'date': '2024-11-24'}},
            ]
        }

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sample Event 1', response.data)
        self.assertIn(b'Sample Event 2', response.data)

    @patch('calender.authenticate_google_calendar')
    @patch('calender.create_event')
    @patch('calender.fetch_events')
    def test_create_event(self, mock_fetch_events, mock_create_event, mock_auth):
        """
        Test the create_event route (POST /create_event).

        - Mocks `authenticate_google_calendar` and `create_event` functions.
        - Mocks event creation and event retrieval to simulate adding an event.
        - Verifies that the event is correctly created and the response contains the event data.
        """
        mock_auth.return_value = Mock()
        mock_create_event.return_value = {
            'id': '12345',
            'summary': 'New Event',
            'start': {'dateTime': '2024-11-22T23:59:59'},
            'end': {'dateTime': '2024-11-23T00:59:59'},
        }
        mock_fetch_events.return_value = [
            {'id': '12345', 'name': 'New Event', 'start': '2024-11-22'}
        ]
        response = self.client.post('/create_event', data={
            'event_name': 'New Event',
            'event_date': '2024-11-22'
        }, follow_redirects=True)
        self.assertIn(b'New Event', response.data)

    @patch('calender.authenticate_google_calendar')
    @patch('calender.delete_event')
    def test_delete_event(self, mock_delete_event, mock_authenticate):
        """
        Test the delete_event route (POST /delete_event).

        - Mocks `authenticate_google_calendar` and `delete_event` functions.
        - Simulates event deletion and verifies the correct status code (200).
        """
        mock_service = Mock()
        mock_authenticate.return_value = mock_service
        mock_delete_event.return_value = None 
        response = self.client.post('/delete_event', data={
            'event_id': '12345'
        })

        self.assertEqual(response.status_code, 200)
    @patch('calender.delete_event')
    @patch('calender.authenticate_google_calendar')
    def test_delete_event_failure(self, mock_auth, mock_delete_event):
        """
        Test the failure scenario for deleting an event.

        - Simulates an exception during event deletion and verifies that the error is handled properly.
        """
        mock_auth.return_value = Mock()
        mock_delete_event.side_effect = Exception("API error")
    
        response = self.client.post('/delete_event', data={'event_id': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"An error occurred: API error", response.data)
    
    @patch('calender.authenticate_google_calendar')
    def test_fetch_events(self, mock_authenticate):
        """
        Test the fetch_events function to ensure it retrieves events correctly.

        - Mocks `authenticate_google_calendar` and event retrieval.
        - Verifies that the function correctly fetches and returns events from the Google Calendar API.
        """
        mock_service = Mock()
        mock_authenticate.return_value = mock_service
        mock_service.events.return_value.list.return_value.execute.return_value = {
            'items': [
                {'id': '1', 'summary': 'Sample Event 1', 'start': {'dateTime': '2024-11-23T09:00:00'}},
                {'id': '2', 'summary': 'Sample Event 2', 'start': {'date': '2024-11-24'}},
            ]
        }
        events = fetch_events(mock_service)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['name'], 'Sample Event 1')
        self.assertEqual(events[1]['name'], 'Sample Event 2')

    @patch('calender.authenticate_google_calendar')
    def test_create_event_function(self, mock_authenticate):
        """
        Test the create_event function to ensure it creates events with correct data.

        - Mocks the `authenticate_google_calendar` function.
        - Simulates event creation and verifies that the created event's details match the expected data.
        """
        mock_service = Mock()
        mock_authenticate.return_value = mock_service
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'id': '12345', 'summary': 'Test Event', 'start': {'dateTime': '2024-11-25T23:59:59'}
        }

        result = create_event(mock_service, 'Test Event', '2024-11-25')
        self.assertEqual(result['summary'], 'Test Event')

    @patch('calender.authenticate_google_calendar')
    @patch('calender.create_event')
    def test_handle_form_submission_error(self, mock_create_event, mock_authenticate_google_calendar):
        """
        Test error handling in form submission for event creation.

        - Simulates a failure in the Google Calendar authentication process.
        - Verifies that the error is caught and displayed in the response.
        """
        mock_authenticate_google_calendar.side_effect = Exception("Google Calendar authentication failed")
        with app.test_client() as client:
            response = client.post('/create_event', data={
                'event_name': 'Test Event',
                'event_date': '2024-12-01'
            })
            self.assertIn("An error occurred:", response.data.decode())
            self.assertIn("Google Calendar authentication failed", response.data.decode())
    @patch('calender.authenticate_google_calendar')
    def test_delete_event_function(self, mock_authenticate):
        """
        Test the delete_event function to ensure it deletes events correctly.

        - Verifies that the `delete_event` function properly interacts with the Google Calendar API to delete events.
        """
        mock_service = Mock()
        mock_authenticate.return_value = mock_service
        delete_event(mock_service, '12345')
        mock_service.events.return_value.delete.assert_called_with(
            calendarId='primary', eventId='12345'
        )

if __name__ == '__main__':
    unittest.main()