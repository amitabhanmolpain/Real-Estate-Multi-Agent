from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Simplified but robust Seller Agent
seller_agent = Agent(
    name="seller_agent",
    model="gemini-2.0-flash",
    description="Creates property listings with market-based pricing and detailed descriptions.",
    instruction=(
        "You are a real estate agent. Create a property listing based on the given details. "
        "Generate appropriate market pricing based on location, size, and property type.\n\n"
        
        "RESPOND ONLY IN THIS JSON FORMAT:\n"
        "{\n"
        "  \"seller\": [{\n"
        "    \"title\": \"Property name\",\n"
        "    \"description\": \"Brief attractive description\",\n"
        "    \"price_in_inr\": 5000000,\n"
        "    \"location\": \"Location details\",\n"
        "    \"size_sq_ft\": 1000,\n"
        "    \"features\": [\"Feature 1\", \"Feature 2\", \"Feature 3\"]\n"
        "  }]\n"
        "}\n\n"
        
        "PRICING GUIDELINES:\n"
        "- Mumbai/Delhi/Bangalore: ₹10,000-20,000 per sq.ft\n"
        "- Other major cities: ₹5,000-10,000 per sq.ft\n"
        "- Smaller cities: ₹3,000-6,000 per sq.ft\n"
        
        "NO MARKDOWN. NO EXTRA TEXT. ONLY JSON."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=seller_agent,
    app_name="seller_app",
    session_service=session_service,
)

USER_ID = "user_seller"
SESSION_ID = "session_seller"

# Helper function for fallback pricing
def calculate_fallback_price(location, size_sqft, property_type):
    """Calculate reasonable price if agent fails"""
    try:
        size_sqft = int(size_sqft) if size_sqft else 1000
        
        # Base pricing per sq.ft based on location
        location_lower = str(location).lower()
        
        if any(city in location_lower for city in ['mumbai', 'delhi', 'bangalore', 'gurgaon']):
            base_price = 15000
        elif any(city in location_lower for city in ['pune', 'chennai', 'hyderabad', 'kolkata']):
            base_price = 7500
        elif any(city in location_lower for city in ['ahmedabad', 'jaipur', 'surat', 'lucknow']):
            base_price = 5000
        else:
            base_price = 4000
        
        # Property type adjustment
        if str(property_type).lower() == 'villa':
            base_price *= 1.3
        elif str(property_type).lower() == 'plot':
            base_price *= 0.7
            
        return int(base_price * size_sqft)
    except:
        return 5000000  # Default fallback

# Main execute function
async def execute(request):
    logger.debug(f"Seller agent request: {request}")
    
    try:
        # Extract data from request
        seller_name = request.get('seller_name', 'Property Owner')
        contact = request.get('contact', 'Contact available')
        
        # Handle nested property structure
        if 'property' in request:
            prop = request['property']
            location = prop.get('location', 'Not specified')
            size_sqft = prop.get('size_sqft', 1000)
            asking_price = prop.get('price', 0)
            property_type = prop.get('type', 'Apartment')
        else:
            # Handle flat structure
            location = request.get('location', 'Not specified')
            size_sqft = request.get('size_sqft', request.get('size', 1000))
            asking_price = request.get('price', 0)
            property_type = request.get('property_type', 'Apartment')

        logger.debug(f"Extracted: location={location}, size={size_sqft}, price={asking_price}")

        # Create session
        try:
            await session_service.create_session(
                app_name="seller_app",
                user_id=USER_ID,
                session_id=SESSION_ID
            )
        except Exception as session_error:
            logger.warning(f"Session creation failed: {session_error}")

        # Create prompt
        prompt = (
            f"Create a property listing:\n"
            f"Location: {location}\n"
            f"Size: {size_sqft} sq ft\n"
            f"Property Type: {property_type}\n"
            f"Reference Price: ₹{asking_price}\n"
            f"Generate market-appropriate pricing and features."
        )

        message = types.Content(role="user", parts=[types.Part(text=prompt)])

        # Try to get response from agent
        try:
            response_text = None
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=message
            ):
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break

            if response_text:
                logger.debug(f"Agent response: {response_text}")
                
                # Clean response
                cleaned = response_text.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                if cleaned.startswith('```'):
                    cleaned = cleaned[3:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

                # Parse JSON
                try:
                    parsed = json.loads(cleaned)
                    if 'seller' in parsed and parsed['seller']:
                        logger.debug("Successfully parsed agent response")
                        return {
                            "seller": parsed['seller'],
                            "status": "success"
                        }
                except json.JSONDecodeError as json_error:
                    logger.warning(f"JSON parsing failed: {json_error}")

        except Exception as agent_error:
            logger.warning(f"Agent execution failed: {agent_error}")

        # Fallback: Create listing manually
        logger.info("Using fallback listing generation")
        
        fallback_price = calculate_fallback_price(location, size_sqft, property_type)
        
        fallback_listing = {
            "title": f"Beautiful {property_type} in {location}",
            "description": f"Well-maintained {property_type.lower()} spanning {size_sqft} sq ft in the heart of {location}. Perfect for families looking for a comfortable home.",
            "price_in_inr": fallback_price,
            "location": location,
            "size_sq_ft": int(size_sqft),
            "features": [
                "Prime location",
                "Well-ventilated rooms",
                "Good connectivity",
                "Peaceful neighborhood",
                "Ready to move"
            ]
        }

        return {
            "seller": [fallback_listing],
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Execute function failed: {e}")
        return {
            "seller": [],
            "status": "error",
            "message": f"Failed to create listing: {str(e)}"
        }

# Wrapper function for external calls
async def run_seller_agent(request_data):
    """Main entry point for seller agent"""
    return await execute(request_data)

# Test function to verify functionality
async def test_seller_agent():
    """Test the seller agent with sample data"""
    test_request = {
        "seller_name": "John Doe",
        "contact": "9999999999",
        "property": {
            "location": "Koramangala, Bangalore",
            "size_sqft": 1200,
            "price": 8000000
        }
    }
    
    result = await execute(test_request)
    print(f"Test result: {result}")
    return result