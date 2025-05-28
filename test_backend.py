#!/usr/bin/env python3
"""
Quick test script to verify backend connectivity and streaming
"""
import asyncio
import httpx
import json

async def test_backend_connection():
    """Test basic backend connectivity"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test basic connectivity
            response = await client.get("http://localhost:8000/")
            print(f"✅ Backend connectivity: {response.status_code}")
            print(f"Backend response: {response.json()}")
            
            # Test streaming endpoint
            print("\n🔄 Testing streaming endpoint...")
            payload = {
                "message": "Hello, this is a test message",
                "session_id": "test_session"
            }
            
            async with client.stream(
                "POST", 
                "http://localhost:8000/chat-stream",
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as stream_response:
                print(f"Stream status: {stream_response.status_code}")
                
                if stream_response.status_code == 200:
                    event_count = 0
                    async for line in stream_response.aiter_lines():
                        if line.startswith("data: "):
                            event_count += 1
                            event_data = line[6:]  # Remove "data: " prefix
                            if event_data.strip():
                                try:
                                    event_json = json.loads(event_data)
                                    print(f"Event {event_count}: {event_json.get('type', 'unknown')} - {event_json.get('content', '')[:50]}")
                                    
                                    # Stop after a few events for testing
                                    if event_count >= 5:
                                        break
                                except json.JSONDecodeError:
                                    print(f"Event {event_count}: Non-JSON data")
                    
                    print(f"✅ Received {event_count} events")
                else:
                    error_text = await stream_response.aread()
                    print(f"❌ Stream error: {stream_response.status_code} - {error_text.decode()}")
                    
    except httpx.ConnectError:
        print("❌ Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing AIDEN backend connection...")
    asyncio.run(test_backend_connection()) 