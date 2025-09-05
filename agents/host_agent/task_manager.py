from common.a2a_client import call_agent
import json
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def sanitize_url(url):
    return url.strip().replace("\t", "").replace("\n", "").replace(" ", "")

# Define agent endpoints
BUYER_URL = sanitize_url("http://localhost:8001/run")
SELLER_URL = sanitize_url("http://localhost:8002/run")
PRICE_URL = sanitize_url("http://localhost:8003/run")
NEIGHBORHOOD_URL = sanitize_url("http://localhost:8004/run")

# Format Buyer results
def format_buyer_markdown(buyer_list):
    if not buyer_list or len(buyer_list) == 0:
        return "No buyer recommendations available."
    
    markdown = "### Buyer Recommendations:\n\n"
    for buyer in buyer_list:
        markdown += f"* **{buyer.get('Property name/title', 'Property')}**\n"
        markdown += f"  * {buyer.get('Description', 'No description')}\n"
        markdown += f"  * Price: {buyer.get('Price in INR', 'N/A')}\n"
        markdown += f"  * Location: {buyer.get('Location', 'N/A')}\n"
        markdown += f"  * Size: {buyer.get('Size', 'N/A')}\n"
        features = buyer.get("Key features", [])
        if features:
            markdown += "  * Features:\n"
            for f in features:
                markdown += f"    * {f}\n"
        markdown += "\n"
    return markdown

# Format Seller results
def format_seller_markdown(seller_list):
    if not seller_list or len(seller_list) == 0:
        return "No seller listings available."
    
    markdown = "### Seller Listings:\n\n"
    for seller in seller_list:
        markdown += f"* **{seller.get('Property name/title', 'Property')}**\n"
        markdown += f"  * {seller.get('Description', 'No description')}\n"
        markdown += f"  * Asking Price: {seller.get('Asking price in INR', 'N/A')}\n"
        markdown += f"  * Location: {seller.get('Location', 'N/A')}\n"
        markdown += f"  * Size: {seller.get('Size', 'N/A')}\n"
        amenities = seller.get("Amenities", [])
        if amenities:
            markdown += "  * Amenities:\n"
            for a in amenities:
                markdown += f"    * {a}\n"
        markdown += "\n"
    return markdown

# Format Price Estimator results
def format_price_markdown(prices):
    if not prices or len(prices) == 0:
        return "No price estimation available."
    
    markdown = "### Price Estimates:\n\n"
    for price in prices:
        markdown += f"* **{price.get('Property name/title', 'Property')}**\n"
        markdown += f"  * Estimated Price: {price.get('Estimated price in INR', 'N/A')}\n"
        markdown += f"  * Confidence: {price.get('Confidence level', 'N/A')}\n\n"
    return markdown

# Format Neighborhood results
def format_neighborhood_markdown(neighborhoods):
    if not neighborhoods or len(neighborhoods) == 0:
        return "No neighborhood insights available."
    
    markdown = "### Neighborhood Insights:\n\n"
    for hood in neighborhoods:
        markdown += f"* **{hood.get('Neighborhood name', 'Area')}**\n"
        markdown += f"  * {hood.get('Description', 'No description')}\n"
        markdown += f"  * Average Price: {hood.get('Average price in INR', 'N/A')}\n"
        markdown += f"  * Safety: {hood.get('Safety rating', 'N/A')}\n"
        highlights = hood.get("Highlights", [])
        if highlights:
            markdown += "  * Highlights:\n"
            for h in highlights:
                markdown += f"    * {h}\n"
        markdown += "\n"
    return markdown

# Main runner
async def run(payload):
    try:
        # Call all agents
        buyer = await call_agent(BUYER_URL, payload)
        seller = await call_agent(SELLER_URL, payload)
        price = await call_agent(PRICE_URL, payload)
        neighborhood = await call_agent(NEIGHBORHOOD_URL, payload)

        # Parse JSON if needed
        buyer_data = json.loads(buyer) if isinstance(buyer, str) else buyer
        seller_data = json.loads(seller) if isinstance(seller, str) else seller
        price_data = json.loads(price) if isinstance(price, str) else price
        neighborhood_data = json.loads(neighborhood) if isinstance(neighborhood, str) else neighborhood

        # Log raw responses
        logger.debug(f"Buyer response: {buyer_data}")
        logger.debug(f"Seller response: {seller_data}")
        logger.debug(f"Price Estimator response: {price_data}")
        logger.debug(f"Neighborhood response: {neighborhood_data}")

        return {
            "buyer": format_buyer_markdown(buyer_data.get("buyer", [])),
            "seller": format_seller_markdown(seller_data.get("seller", [])),
            "price": format_price_markdown(price_data.get("price", [])),
            "neighborhood": format_neighborhood_markdown(neighborhood_data.get("neighborhood", [])),
        }
    except Exception as e:
        logger.error(f"Error in host agent run: {e}")
        return {
            "buyer": "Error fetching buyer data.",
            "seller": "Error fetching seller data.",
            "price": "Error fetching price data.",
            "neighborhood": "Error fetching neighborhood data.",
        }
