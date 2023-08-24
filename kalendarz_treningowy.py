import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def create_event(service, event_details, guest_emails, calendar_id='primary'):
    event = {
        'summary': event_details['summary'],
        'location': event_details['location'],
        'description': event_details.get('description', ''),
        'start': {
            'dateTime': event_details['start_datetime'],
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': event_details['end_datetime'],
            'timeZone': 'UTC',
        },
        'attendees': [{'email': email} for email in guest_emails],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')

def main():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    event_details = {
        'summary': 'Sample Event',
        'location': 'Virtual',
        'start_datetime': '2023-08-25T10:00:00Z',
        'end_datetime': '2023-08-25T12:00:00Z',
        'description': 'This is a sample event description.',
    }

    guest_emails = ['guest1@example.com', 'guest2@example.com']
    calendar_id = 'your_calendar_id_here'  # Replace with the specific Calendar ID

    create_event(service, event_details, guest_emails, calendar_id)

if __name__ == '__main__':
    main()
