import requests
import random
import os

BASE_URL = "http://127.0.0.1:8000"
POST_BOOK_URL = f"{BASE_URL}/api/post-book"

# --- User 1 Data ---
ACCESS_TOKEN_1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGlzaEBnbWFpbC5jb20ifQ.El3htw19At_VEJ1d1rcl-oEUS5ahqV3Bb_2cymQQvjM"
LOCATIONS_1 = [
    {"location": "Sanga, Kavrepalanchok", "latitude": 27.634768, "longitude": 85.490298},
    {"location": "Tathali, Bhaktapur", "latitude": 27.670197, "longitude": 85.446696},
    {"location": "Godawari Marble Factory, Lalitpur", "latitude": 27.591883, "longitude": 85.376210}
]

# --- User 2 Data ---
ACCESS_TOKEN_2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGlzaHRAZ21haWwuY29tIn0.HuVvyoeK3BODKuF_casy9f-x7ALMKsFjAJ5DXWPxNSo"
LOCATIONS_2 = [
    {"location": "Kupondole, Lalitpur", "latitude": 27.687576, "longitude": 85.3138489}
]

# --- Common Book Data ---
BOOK_TITLES = [
    "The Silent Patient", "Educated: A Memoir", "Where the Crawdads Sing",
    "The Great Gatsby", "To Kill a Mockingbird", "1984", "The Catcher in the Rye",
    "Pride and Prejudice", "The Hobbit", "The Alchemist", "The Lord of the Rings",
    "Harry Potter and the Sorcerer's Stone", "The Diary of a Young Girl",
    "Sapiens: A Brief History of Humankind", "Atomic Habits"
]

CONDITIONS = ["new", "like new", "used", "old"]
CATEGORIES = [
    "School", "+2 College", "Bachelor & Above", "Novels & Fiction",
    "Religion & Spirituality", "Self-Help", "Children's Books", "Others"
]

# --- Dummy Image Files ---
IMAGE_DIR = "dummy_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

DUMMY_IMAGES = []
for i in range(5):
    img_path = os.path.join(IMAGE_DIR, f"dummy_{i}.jpg")
    if not os.path.exists(img_path):
        with open(img_path, "wb") as f:
            f.write(os.urandom(1024)) # Create a 1KB dummy file
    DUMMY_IMAGES.append(img_path)


def post_book(access_token, location_details):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    form_data = {
        "title": random.choice(BOOK_TITLES),
        "condition": random.choice(CONDITIONS),
        "price": round(random.uniform(5.0, 50.0), 2),
        "quantity": random.randint(1, 10),
        "description": "This is a sample book description.",
        "location": location_details["location"],
        "latitude": location_details["latitude"],
        "longitude": location_details["longitude"],
        "category": random.choice(CATEGORIES),
    }

    # Add 1 to 3 random images
    num_images = random.randint(1, 3)
    files = [("images", (os.path.basename(p), open(p, "rb"), "image/jpeg")) for p in random.sample(DUMMY_IMAGES, num_images)]

    try:
        response = requests.post(POST_BOOK_URL, headers=headers, data=form_data, files=files)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Close the files
        for _, file_tuple in files:
            file_tuple[1].close()
            
        print(f"Successfully posted book: {form_data['title']} at {form_data['location']}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error posting book: {form_data['title']}. Error: {e}")
        if e.response:
            print(f"Response content: {e.response.text}")
        return None

def main():
    print("--- Seeding books for User 1 ---")
    for i in range(10):
        print(f"Posting book {i+1}/10...")
        location = random.choice(LOCATIONS_1)
        post_book(ACCESS_TOKEN_1, location)

    print("\n--- Seeding books for User 2 ---")
    for i in range(10):
        print(f"Posting book {i+1}/10...")
        location = random.choice(LOCATIONS_2)
        post_book(ACCESS_TOKEN_2, location)

    print("\n--- Seeding complete ---")

if __name__ == "__main__":
    main()
