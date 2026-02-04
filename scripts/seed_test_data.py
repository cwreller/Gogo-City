"""Seed script to add test data for development."""
import sys
sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models import City, CuratedTask, User

def seed_data():
    db = SessionLocal()
    
    try:
        # Create a test user
        user = User(
            email="test@example.com",
            username="testuser",
            display_name="Test User",
        )
        db.add(user)
        db.flush()
        print(f"Created user: {user.id}")
        
        # Create Nashville
        nashville = City(
            name="Nashville",
            state="Tennessee",
            country="USA",
            lat=36.1627,
            lng=-86.7816,
            timezone="America/Chicago",
        )
        db.add(nashville)
        db.flush()
        print(f"Created city: {nashville.name} ({nashville.id})")
        
        # Create curated tasks for Nashville
        tasks = [
            CuratedTask(
                city_id=nashville.id,
                name="Prince's Hot Chicken",
                description="The original hot chicken spot that started it all",
                address="123 Ewing Dr, Nashville, TN",
                lat=36.1745,
                lng=-86.7678,
                task_description="Order at least 'medium' spice level",
                verification_type="photo",
                verification_hint="Take a photo of your hot chicken plate",
                category="food",
                vibe_tags=["foodie", "adventurous", "iconic"],
                dietary_tags=[],
                price_level=2,
                avg_duration_minutes=45,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="Broadway Honky Tonk Crawl",
                description="Hit at least 3 honky tonks on Lower Broadway",
                address="Broadway, Nashville, TN",
                lat=36.1622,
                lng=-86.7743,
                task_description="Visit Tootsie's, Robert's Western World, and Legends",
                verification_type="gps",
                verification_hint="Check in when you arrive at Broadway",
                category="nightlife",
                vibe_tags=["nightlife", "music", "social"],
                dietary_tags=[],
                price_level=2,
                avg_duration_minutes=120,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="Centennial Park & Parthenon",
                description="Visit the full-scale replica of the Greek Parthenon",
                address="2500 West End Ave, Nashville, TN",
                lat=36.1496,
                lng=-86.8130,
                task_description="Find the 42-foot statue of Athena inside",
                verification_type="photo",
                verification_hint="Photo with Athena statue",
                category="culture",
                vibe_tags=["cultural", "chill", "outdoors"],
                dietary_tags=[],
                price_level=1,
                avg_duration_minutes=60,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="Hattie B's Hot Chicken",
                description="Another legendary hot chicken spot",
                address="112 19th Ave S, Nashville, TN",
                lat=36.1540,
                lng=-86.7967,
                task_description="Try the 'Shut the Cluck Up' if you dare",
                verification_type="photo",
                verification_hint="Photo of your chicken and spice level",
                category="food",
                vibe_tags=["foodie", "adventurous"],
                dietary_tags=[],
                price_level=2,
                avg_duration_minutes=45,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="The Bluebird Cafe",
                description="Intimate singer-songwriter venue where legends were discovered",
                address="4104 Hillsboro Pike, Nashville, TN",
                lat=36.1031,
                lng=-86.8172,
                task_description="Listen to at least one full song in silence",
                verification_type="gps",
                verification_hint="Check in at the venue",
                category="music",
                vibe_tags=["music", "cultural", "intimate"],
                dietary_tags=[],
                price_level=2,
                avg_duration_minutes=90,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="Biscuit Love",
                description="Southern brunch at its finest",
                address="316 11th Ave S, Nashville, TN",
                lat=36.1541,
                lng=-86.7868,
                task_description="Order the Bonuts (biscuit donuts)",
                verification_type="photo",
                verification_hint="Photo of your brunch spread",
                category="food",
                vibe_tags=["foodie", "brunch", "chill"],
                dietary_tags=["vegetarian-options"],
                price_level=2,
                avg_duration_minutes=60,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="Johnny Cash Museum",
                description="Walk through the life of the Man in Black",
                address="119 3rd Ave S, Nashville, TN",
                lat=36.1615,
                lng=-86.7761,
                task_description="Find Johnny's handwritten lyrics",
                verification_type="photo",
                verification_hint="Photo of your favorite exhibit",
                category="museum",
                vibe_tags=["cultural", "music", "history"],
                dietary_tags=[],
                price_level=2,
                avg_duration_minutes=75,
            ),
            CuratedTask(
                city_id=nashville.id,
                name="Pedestrian Bridge Sunset",
                description="Walk the John Seigenthaler Pedestrian Bridge at sunset",
                address="Pedestrian Bridge, Nashville, TN",
                lat=36.1584,
                lng=-86.7709,
                task_description="Catch the sunset over downtown",
                verification_type="photo",
                verification_hint="Sunset photo from the bridge",
                category="outdoors",
                vibe_tags=["romantic", "chill", "outdoors", "photography"],
                dietary_tags=[],
                price_level=1,
                avg_duration_minutes=30,
            ),
        ]
        
        for task in tasks:
            db.add(task)
        
        db.commit()
        print(f"Created {len(tasks)} curated tasks")
        
        print("\n✅ Test data seeded successfully!")
        print(f"\nCity ID to use for testing: {nashville.id}")
        print(f"User ID to use for testing: {user.id}")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
