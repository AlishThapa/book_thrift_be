import requests
import json

# Base URL of your FastAPI application
BASE_URL = "http://127.0.0.1:8000"

# API endpoint for posting a book
POST_BOOK_URL = f"{BASE_URL}/api/post-book"

# Bearer tokens
TOKEN_1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGlzaHRoYXBhNDQ1MEBnbWFpbC5jb20ifQ.MhNItbz_7B1cIHAgi3pZkxl33BbPffMMK9SKgTDm5nw"
TOKEN_2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGlzaEBnbWFpbC5jb20ifQ.El3htw19At_VEJ1d1rcl-oEUS5ahqV3Bb_2cymQQvjM"

def post_book(token, book_data):
    """
    Posts a single book to the API.
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # The endpoint expects multipart/form-data, so we'll send files and data
    files = {
        'title': (None, book_data['title']),
        'condition': (None, book_data['condition']),
        'price': (None, str(book_data['price'])),
        'quantity': (None, str(book_data['quantity'])),
        'description': (None, book_data['description']),
        'location': (None, book_data['location']),
        'category': (None, book_data['category']),
    }
    
    response = requests.post(POST_BOOK_URL, headers=headers, files=files)
    
    if response.status_code == 201:
        print(f"Successfully posted '{book_data['title']}'")
        return response.json()
    else:
        print(f"Failed to post '{book_data['title']}'. Status code: {response.status_code}")
        try:
            print("Error details:", response.json())
        except json.JSONDecodeError:
            print("Error details:", response.text)
        return None

def main():
    """
    Main function to add books for two different users.
    """
    # --- User 1: Add 10 books named "book1" to "book10" ---
    print("--- Posting books for User 1 ---")
    for i in range(1, 11):
        book_data = {
            "title": f"book{i}",
            "condition": "used",
            "price": 15.99 + i,
            "quantity": 1,
            "description": f"This is a great book titled book{i}.",
            "location": "Kathmandu",
            "category": "Fiction"
        }
        post_book(TOKEN_1, book_data)

    # --- User 2: Add 5 books named "kitab1" to "kitab5" ---
    print("\n--- Posting books for User 2 ---")
    for i in range(1, 6):
        book_data = {
            "title": f"kitab{i}",
            "condition": "new",
            "price": 25.50 + i,
            "quantity": 1,
            "description": f"Brand new book: kitab{i}.",
            "location": "Pokhara",
            "category": "Non-Fiction"
        }
        post_book(TOKEN_2, book_data)

if __name__ == "__main__":
    main()
