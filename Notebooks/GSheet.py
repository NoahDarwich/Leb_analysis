import os
import re
import pickle
import google.auth
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def authenticate_google_api():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google.auth.default(scopes=['https://www.googleapis.com/auth/drive'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def extract_drive_link(row):
    drive_link = ''
    for cell in row:
        if re.match(r'https:\/\/drive\.google\.com\/', str(cell)):
            drive_link = cell
            break
    return drive_link


def add_drive_column(sheet_id):
    creds = authenticate_google_api()

    service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)

    sheet_range = 'Sheet1!A1:Z'
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return

    drive_links = []
    for row in values:
        drive_link = extract_drive_link(row)
        drive_links.append([drive_link])

    update_range = 'Sheet1!AA1:AA' + str(len(drive_links))
    request_body = {'values': drive_links}
    request = service.spreadsheets().values().update(spreadsheetId=sheet_id, range=update_range,
                                                     valueInputOption='RAW', body=request_body)
    response = request.execute()
    print('Drive links added to the "drive" column.')


if __name__ == '__main__':
    spreadsheet_id = 'YOUR_SPREADSHEET_ID'
    add_drive_column(spreadsheet_id)
