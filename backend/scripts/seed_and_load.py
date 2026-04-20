import asyncio
import aiohttp
import random
import time
import uuid

API_BASE = "http://localhost:8000"

async def fetch_levels(session):
    print("Fetching imported levels...")
    async with session.get(f"{API_BASE}/level") as response:
        if response.status != 200:
            print(f"Failed to fetch levels: {await response.text()}")
            return []
        data = await response.json()
        print(f"Found {len(data)} levels.")
        return data

async def register_user(session, i):
    username = f"loadtest_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "email": email,
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!"
    }
    
    async with session.post(f"{API_BASE}/auth/registration", json=payload) as response:
        if response.status in (200, 201):
            return {"username": username, "password": "TestPassword123!"}
        else:
            print(f"Error registering {username}: {await response.text()}")
            return None

async def login_user(session, user_creds):
    payload = {
        "login": user_creds["username"],
        "password": user_creds["password"]
    }
    async with session.post(f"{API_BASE}/auth/login", json=payload) as response:
        if response.status == 200:
            data = await response.json()
            user_creds["access"] = data.get("access")
        else:
            print(f"Error logging in {user_creds['username']}")

async def submit_attempt(session, user_creds, level):
    headers = {"Authorization": f"Bearer {user_creds['access']}"}
    
    wpm = random.randint(20, 180)
    accuracy = random.randint(50, 100)
    
    payload = {
        "level_id": level["id"],
        "wpm": wpm,
        "accuracy": accuracy
    }
    
    start = time.time()
    try:
        async with session.post(f"{API_BASE}/level/submit", json=payload, headers=headers) as response:
            latency = (time.time() - start) * 1000
            if response.status in (200, 201):
                return True, latency
            else:
                return False, latency
    except Exception as e:
         return False, 0

async def main():
    async with aiohttp.ClientSession() as session:
        levels = await fetch_levels(session)
        if not levels:
            print("No levels available to attempt. Ensure migrations have run!")
            return

        print("\n--- Phase 1: Heavy Registration Burst (100 Users) ---")
        tasks = [register_user(session, i) for i in range(100)]
        users = await asyncio.gather(*tasks)
        users = [u for u in users if u]
        print(f"Successfully registered {len(users)} mock users.")

        print("\n--- Phase 2: Logging in Mock Users ---")
        login_tasks = [login_user(session, u) for u in users]
        await asyncio.gather(*login_tasks)
        authenticated = [u for u in users if "access" in u]
        print(f"Successfully authenticated {len(authenticated)} users.")

        print("\n--- Phase 3: MASSIVE ATTEMPT BURST ---")
        print("Each user will concurrently submit 5 random attempts...")
        
        attempt_tasks = []
        for user in authenticated:
            for _ in range(5):
                lvl = random.choice(levels)
                attempt_tasks.append(submit_attempt(session, user, lvl))
                
        print(f"Firing {len(attempt_tasks)} concurrent requests to Debezium/Kafka Outbox...")
        
        start_time = time.time()
        results = await asyncio.gather(*attempt_tasks)
        total_time = time.time() - start_time
        
        successes = sum(1 for r, _ in results if r)
        fails = len(results) - successes
        avg_latency = sum(lat for _, lat in results) / len(results) if results else 0
        
        print("\n--- BURST COMPLETE ---")
        print(f"Total time elapsed: {total_time:.2f} seconds")
        print(f"Successfully submitted via API Gateway: {successes}")
        print(f"Failures (Gateway timeout/error): {fails}")
        print(f"Average Round-Trip Latency: {avg_latency:.2f}ms")
        print("\n=> Check Kafka-UI at http://localhost:8085 to see Debezium capturing and replicating the events in real time!")

if __name__ == "__main__":
    asyncio.run(main())
