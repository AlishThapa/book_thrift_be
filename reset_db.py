from app.database import engine, Base
from app.models import user, book, cart, wishlist

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

if __name__ == "__main__":
    reset_database()