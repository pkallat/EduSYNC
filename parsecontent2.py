###THIS CODE IS FOR P2 AND WAS CREATED USING AN AI TOOL. THIS CODE IS SUPPOSED TO PERFORM THE SAME ACTIONS AS PARSECONTENT1.PY BUT WITHOUT ACCESS TO BLACKBOARD'S REST API. ###
import requests
from bs4 import BeautifulSoup
import schedule
import time
from pymongo import MongoClient

# MongoDB setup
mongo_client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = mongo_client['blackboard_db']  # Database
collection = db['course_content']  # Collection for storing course content

# Create an index on "contentId" to ensure uniqueness
collection.create_index("contentId", unique=True)

# Blackboard URLs
LOGIN_URL = "https://blackboard.example.com/webapps/login/"
COURSE_URL = "https://blackboard.example.com/learn/course_content/course_id_here"

# Your login credentials (modify accordingly)
USERNAME = 'your_username'
PASSWORD = 'your_password'

# Start session for requests
session = requests.Session()

# Function to log in to Blackboard
def login_to_blackboard():
    # This will vary depending on Blackboard's login form (inspect form structure for field names)
    login_payload = {
        'user_id': USERNAME,
        'password': PASSWORD,
        'login': 'Login'
    }

    # Send POST request for login
    response = session.post(LOGIN_URL, data=login_payload)
    if "Welcome" in response.text:  # Change based on what the response looks like
        print("Logged in successfully!")
    else:
        print("Login failed.")

# Function to scrape course content
def scrape_course_content():
    # Make a GET request to the course page after logging in
    response = session.get(COURSE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find content blocks, assuming they have a specific HTML structure
    # Example: Modify selectors based on the Blackboard structure
    content_blocks = soup.find_all('div', class_='content-block')  # Adjust the selector

    course_updates = []

    # Loop through content blocks and extract title, description, etc.
    for block in content_blocks:
        title = block.find('h3').text  # Assuming the title is in an <h3> tag
        description = block.find('p').text  # Assuming the description is in a <p> tag
        modified = block.find('time')['datetime']  # Assuming modified date is stored in <time>

        # Create a content item dictionary
        content_item = {
            'contentId': hash(title + modified),  # Use a hash of title + modified date as the contentId
            'title': title,
            'description': description,
            'modified': modified
        }
        course_updates.append(content_item)

    return course_updates

# Function to check if the content is new
def is_new_content(item):
    if collection.find_one({"contentId": item['contentId']}):
        return False
    return True

# Function to add new content to MongoDB
def add_new_content_to_db(content_item):
    try:
        collection.insert_one(content_item)
        print(f"Added new content: {content_item['title']} to MongoDB.")
    except Exception as e:
        print(f"Error inserting content to MongoDB: {e}")

# Function to scrape and check for new content
def check_for_new_content():
    print("Checking for new course content...")
    course_updates = scrape_course_content()

    if course_updates:
        for item in course_updates:
            if is_new_content(item):
                add_new_content_to_db(item)
            else:
                print(f"Content already exists: {item['title']}")
    else:
        print("No new content found or error occurred.")

# Schedule the scraper to run every hour
schedule.every().hour.do(check_for_new_content)

# Login to Blackboard before starting the scraper
login_to_blackboard()

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
