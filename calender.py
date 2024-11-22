from flask import Flask, request, render_template_string
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """
    Authenticate the user with Google Calendar API and return the service object.

    This function checks if there are existing credentials saved in a file.
    If not, it initiates the OAuth flow to obtain new credentials and saves
    them for future use.

    Returns:
        Authenticated Google Calendar service object.
    """
    creds = None
    if creds_file := "token.pickle":
        try:
            with open(creds_file, 'rb') as token:
                creds = pickle.load(token)
        except FileNotFoundError:
            pass
    # If no valid credentials, authenticate using OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def create_event(calendar_service, event_name, event_date):
    """
    Create a new event in Google Calendar.

    Args:
        calendar_service (googleapiclient.discovery.Resource): Authenticated Google Calendar service object.
        event_name (str): The name or title of the event.
        event_date (str): The date of the event in YYYY-MM-DD format.

    Returns:
        link to the event in Google Calendar.
    """
    event = {
        'summary': event_name,
        'start': {
            'dateTime': f"{event_date}T09:00:00",  
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': f"{event_date}T10:00:00",  
            'timeZone': 'America/New_York',
        },
    }
    return calendar_service.events().insert(calendarId='primary', body=event).execute()


html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Google Calendar Event</title>
</head>
<body>
    <h1>Create Google Calendar Event</h1>
    <form method="POST" action="/create_event">
        <input type="text" name="event_name" placeholder="Event Name" required>
        <input type="date" name="event_date" required>
        <button type="submit">Create Event</button>
    </form>
    <div class="events-list">
        <h2>Events</h2>
        <ul id="event-list">
            {% for event_id, event_name in events.items() %}
                <li>
                    {{ event_name }}
                    <form method="POST" action="/delete_event" style="display:inline;">
                        <input type="hidden" name="event_id" value="{{ event_id }}">
                        <button type="submit">Delete</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""
event_store = {}
@app.route("/", methods=["GET"])
def index():
    """
    Display the HTML form for creating a Google Calendar event.

    Returns:
        str: The rendered HTML form template.
    """
    return render_template_string(html_template,events=event_store)

@app.route("/create_event", methods=["POST"])
def handle_form_submission():
    """
    Handle form submission, create a Google Calendar event, and display the result.

    Extracts event name and date from the submitted form, authenticates with Google Calendar,
    and creates the event. Returns a success message with the event link or an error message.

    Returns:
        str: A success or error message based on the outcome.
    """
    event_name = request.form.get("event_name")
    event_date = request.form.get("event_date")
    
    try:
        service = authenticate_google_calendar()
        event_result = create_event(service, event_name, event_date)
        event_store[event_result['id']] = event_name
        return render_template_string(html_template, events=event_store)
    except Exception as e:
        return f"An error occurred: {e}"

def delete_event(calendar_service, event_id):
    """
    Delete an event from Google Calendar.

    Args:
        calendar_service (googleapiclient.discovery.Resource): Authenticated Google Calendar service object.
        event_id (str): The ID of the event to be deleted.
    """
    try:
        calendar_service.events().delete(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        raise Exception(f"Failed to delete event with ID {event_id}: {e}")

@app.route("/delete_event", methods=["POST"])
def handle_event_deletion():
    """
    Handle event deletion from Google Calendar.

    Extracts the event ID from the request, deletes the event from Google Calendar,
    and removes it from the in-memory store.
    """
    event_id = request.form.get("event_id")
    if not event_id:
        return "Event ID is missing. Cannot delete the event.", 400

    try:
        service = authenticate_google_calendar()
        delete_event(service, event_id)  # Delete the event from Google Calendar
        event_store.pop(event_id, None)  # Remove the event from the local in-memory store
        return render_template_string(html_template, events=event_store)
    except KeyError:
        return render_template_string(html_template, events=event_store, message=f"Event ID {event_id} does not exist.")
    except Exception as e:
        return render_template_string(html_template, events=event_store, message=f"An error occurred: {e}")

if __name__ == "__main__":
    """
    Run the Flask application in debug mode.
    """
    app.run(debug=True)