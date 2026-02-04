#!/usr/bin/env python3
"""
GoGoCity Demo Script
====================
Demonstrates the AI-powered route generation flow.

Run with: uv run python scripts/demo.py
(Make sure the server is running: uv run uvicorn app.main:app --reload)
"""

import httpx
import json
import time

API_URL = "http://localhost:8000"

# Nashville city ID from our seed data
NASHVILLE_ID = "33abdf28-42f2-4704-bfc8-90c906b042a0"


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step: int, text: str):
    """Print a step indicator."""
    print(f"\n[Step {step}] {text}")
    print("-" * 40)


def demo():
    """Run the demo."""
    print_header("GoGoCity Route Generation Demo")
    
    # Step 1: Show the preferences
    print_step(1, "User fills out preferences form")
    
    preferences = {
        "city_id": NASHVILLE_ID,
        "time_available_hours": 4,
        "budget": "medium",
        "vibe_tags": ["foodie", "adventurous"],
        "dietary_restrictions": [],
        "group_size": 2
    }
    
    print("User preferences:")
    print(f"  City: Nashville")
    print(f"  Time available: {preferences['time_available_hours']} hours")
    print(f"  Budget: {preferences['budget']}")
    print(f"  Vibes: {', '.join(preferences['vibe_tags'])}")
    print(f"  Group size: {preferences['group_size']}")
    
    # Step 2: Call the API
    print_step(2, "Calling AI to generate personalized route...")
    
    start_time = time.time()
    
    try:
        response = httpx.post(
            f"{API_URL}/api/routes/generate",
            json=preferences,
            timeout=60.0
        )
        response.raise_for_status()
    except httpx.ConnectError:
        print("Error: Server not running!")
        print("   Start it with: uv run uvicorn app.main:app --reload")
        return
    except httpx.HTTPStatusError as e:
        print(f"Error: {e.response.json()}")
        return
    
    elapsed = time.time() - start_time
    route = response.json()
    
    print(f"Route generated in {elapsed:.1f} seconds")
    
    # Step 3: Show the generated route
    print_step(3, "AI selected these tasks for you")
    
    print(f"\n{route['title']}")
    print(f"City: {route['city_name']}")
    print(f"Estimated time: {route['estimated_duration_minutes']} minutes")
    print(f"Tasks: {route['total_tasks']}\n")
    
    for i, task in enumerate(route['tasks'], 1):
        print(f"  {i}. {task['name']}")
        print(f"     Address: {task['address']}")
        if task['task_description']:
            print(f"     Task: {task['task_description']}")
        print(f"     ~{task['avg_duration_minutes']} min | {'$' * (task['price_level'] or 1)}")
        print()
    
    # Step 4: Show the share code
    print_step(4, "Route saved to database")
    print(f"  Template ID: {route['template_id']}")
    print(f"  Users can now import this route and track their own progress!")
    
    print_header("Demo Complete!")
    print("\nThe flow:")
    print("  1. User preferences -> Backend")
    print("  2. Backend fetches curated tasks from DB")
    print("  3. OpenAI selects best matches")
    print("  4. Route template saved to DB")
    print("  5. User gets personalized route!\n")


if __name__ == "__main__":
    demo()
