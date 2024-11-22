from flask import Flask, request, render_template_string
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from datetime import datetime

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """
    Authenticate the user with Google Calendar API and return the service object.

    This function checks if there are existing credentials saved in a file. If not, 
    it initiates the OAuth flow to obtain new credentials and saves them for future use.

    Returns:
        googleapiclient.discovery.Resource: Authenticated Google Calendar service object.
    """
    creds = None
    if creds_file := "token.pickle":
        try:
            with open(creds_file, 'rb') as token:
                creds = pickle.load(token)
        except FileNotFoundError:
            pass
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def fetch_events(calendar_service):
    """
    Fetch upcoming events from Google Calendar.

    Args:
        calendar_service (googleapiclient.discovery.Resource): Authenticated Google Calendar service object.

    Returns:
        list: A list of events with their ID, name, and start date (formatted as YYYY-MM-DD).
    """
    now = datetime.utcnow().isoformat() + 'Z'  
    events_result = calendar_service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    formatted_events = []
    for event in events:
        event_start = event['start'].get('dateTime', event['start'].get('date'))
        formatted_date = event_start.split('T')[0] if 'T' in event_start else event_start
        formatted_events.append({'id': event['id'], 'name': event['summary'], 'start': formatted_date})
    
    return formatted_events

def create_event(calendar_service, event_name, event_date):
    """
    Create a new event in Google Calendar.

    Args:
        calendar_service (googleapiclient.discovery.Resource): Authenticated Google Calendar service object.
        event_name (str): The name or title of the event.
        event_date (str): The date of the event in YYYY-MM-DD format.

    Returns:
        dict: The created event object as returned by Google Calendar API.
    """
    event = {
        'summary': event_name,
        'start': {
            'dateTime': f"{event_date}T23:59:59",  
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': f"{event_date}T23:59:59",  
            'timeZone': 'America/New_York',
        },
    }
    return calendar_service.events().insert(calendarId='primary', body=event).execute()

def delete_event(calendar_service, event_id):
    """
    Delete an event from Google Calendar.

    Args:
        calendar_service (googleapiclient.discovery.Resource): Authenticated Google Calendar service object.
        event_id (str): The unique ID of the event to be deleted.

    Returns:
        None
    """
    calendar_service.events().delete(calendarId='primary', eventId=event_id).execute()

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Calendar Manager</title>
</head>
<body>
    <h1>Manage Google Calendar Events</h1>
    <form method="POST" action="/create_event">
        <input type="text" name="event_name" placeholder="Event Name" required>
        <input type="date" name="event_date" required>
        <button type="submit">Create Event</button>
    </form>
    <div class="events-list">
        <h2>Current Events</h2>
        <ul id="event-list">
            {% for event in events %}
                <li>
                    {{ event.name }} ({{ event.start }})
                    <form method="POST" action="/delete_event" style="display:inline;">
                        <input type="hidden" name="event_id" value="{{ event.id }}">
                        <button type="submit">Delete</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    """
    Display the HTML form for creating a Google Calendar event
    and fetch current events to display on the page.

    Returns:
        str: The rendered HTML form with current events.
    """
    try:
        service = authenticate_google_calendar()
        events = fetch_events(service)
    except Exception as e:
        events = []
        print(f"An error occurred while fetching events: {e}")
    return render_template_string(html_template, events=events)

@app.route("/create_event", methods=["POST"])
def handle_form_submission():
    """
    Handle form submission, create a Google Calendar event, and refresh the page.

    Extracts event name and date from the submitted form, authenticates with Google Calendar,
    and creates the event. Refreshes the page to show updated events.

    Returns:
        str: Rendered HTML page with updated events.
    """
    event_name = request.form.get("event_name")
    event_date = request.form.get("event_date")
    try:
        service = authenticate_google_calendar()
        create_event(service, event_name, event_date)
    except Exception as e:
        return f"An error occurred: {e}"
    return index()

@app.route("/delete_event", methods=["POST"])
def handle_event_deletion():
    """
    Handle event deletion from Google Calendar and refresh the page.

    Extracts event ID from the submitted form, authenticates with Google Calendar,
    and deletes the specified event. Refreshes the page to show updated events.

    Returns:
        str: Rendered HTML page with updated events.
    """
    event_id = request.form.get("event_id")
    try:
        service = authenticate_google_calendar()
        delete_event(service, event_id)
    except Exception as e:
        return f"An error occurred: {e}"
    return index()

if __name__ == "__main__":
    """
    Run the Flask application in debug mode.
    """
    app.run(debug=True)