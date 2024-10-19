###THIS IS THE CODE USING AN AI TOOL FOR P2. THIS CODE ASSUMES ACCESS TO BLACKBOARD REST API AND REQUIRES ... THIS CODE PARSES BLACKBOARD'S CONTENT FOR CHANGES EVERY HOUR AND WILL ADD ANY NEW ONES TO MONGODB###
import requests
import json
import schedule
import time
from pymongo import MongoClient, errors

# Blackboard API base URL and your credentials
BB_API_URL = "https://blackboard.example.com/learn/api/public/v1"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"

# MongoDB setup
mongo_client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = mongo_client['blackboard_db']  # Database
collection = db['course_content']  # Collection for storing course content

# Create an index on "contentId" to ensure uniqueness
try:
    collection.create_index("contentId", unique=True)
    print("Index on 'contentId' created successfully.")
except errors.DuplicateKeyError:
    print("Index on 'contentId' already exists.")
except Exception as e:
    print(f"Error creating index: {e}")

# Function to get the OAuth2 token
def get_access_token():
    url = f"{BB_API_URL}/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print(f"Error getting token: {response.status_code}")
        return None

# Function to get course content using the Blackboard REST API
def get_course_content(course_id, token):
    url = f"{BB_API_URL}/courses/{course_id}/contents"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        course_content = response.json()
        return course_content['results']  # List of course content items
    else:
        print(f"Error getting course content: {response.status_code}")
        return None

# Function to check if the content is new
def is_new_content(item):
    # Check if the content already exists in MongoDB by its Blackboard content ID
    if collection.find_one({"contentId": item['id']}):
        return False  # Content already exists
    else:
        return True

# Function to add new content to MongoDB
def add_new_content_to_db(content_item):
    document = {
        "contentId": content_item['id'],
        "title": content_item['title'],
        "modified": content_item['modified'],
        "created": content_item.get('created', None),
        "description": content_item.get('description', None),
        "courseId": content_item['courseId']  # Ensure courseId is part of the item
    }
    # Insert the new document into MongoDB
    try:
        collection.insert_one(document)
        print(f"Added new content: {content_item['title']} to MongoDB.")
    except errors.DuplicateKeyError:
        print(f"Duplicate content found: {content_item['title']}")
    except Exception as e:
        print(f"Error inserting content to MongoDB: {e}")

# Function to check for changes and add new events to MongoDB
def check_for_changes():
    print("Checking for course content updates...")
    access_token = get_access_token()
    if not access_token:
        return

    course_id = "course_id_here"  # Blackboard course ID
    content = get_course_content(course_id, access_token)

    if content:
        for item in content:
            # Check if the content is new
            if is_new_content(item):
                # Add the new content to MongoDB
                add_new_content_to_db(item)
            else:
                print(f"Content already exists: {item['title']}")
    else:
        print("No content found or error occurred.")

# Schedule the scan to run every hour
schedule.every().hour.do(check_for_changes)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
