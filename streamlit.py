import streamlit as st
import requests
import json

# ---------------------------
# Agent Endpoints
# ---------------------------
AGENT_URLS = {
    "buyer": "http://localhost:8001/run",
    "seller": "http://localhost:8002/run",
    "price": "http://localhost:8003/run",
    "neighborhood": "http://localhost:8004/run",
}

# ---------------------------
# Helper: Call Agent
# ---------------------------
def call_agent(agent: str, payload: dict):
    try:
        response = requests.post(AGENT_URLS[agent], json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Agent error {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ---------------------------
# Helper: Price to Words (Indian numbering system)
# ---------------------------
def price_to_words(num: int) -> str:
    if not isinstance(num, (int, float)):
        return "N/A"
    num = int(num)
    if num == 0:
        return "zero rupees"

    units = [
        (10**7, "crore"),
        (10**5, "lakh"),
        (10**3, "thousand"),
        (10**2, "hundred"),
    ]
    parts = []
    for value, name in units:
        if num >= value:
            count = num // value
            num %= value
            parts.append(f"{count} {name}")
    if num > 0:
        parts.append(str(num))
    return " ".join(parts) + " rupees"

# ---------------------------
# Helper: Display Buyer Response
# ---------------------------
def display_buyer_response(result):
    if result.get("status") == "success" and result.get("buyer"):
        st.success("✅ Properties Found!")
        
        for i, prop in enumerate(result["buyer"], 1):
            with st.container():
                # Property Header
                st.markdown(f"### 🏠 Property {i}: {prop.get('name', 'Unnamed Property')}")
                
                # Property Details in Cards
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    price = prop.get("price", 0)
                    st.metric(
                        label="💰 Price",
                        value=f"₹{price:,}",
                        help=f"In words: {price_to_words(price)}"
                    )
                
                with col2:
                    st.metric(
                        label="📍 Location", 
                        value=prop.get("location", "N/A")
                    )
                
                with col3:
                    st.metric(
                        label="📏 Size",
                        value=f"{prop.get('size', 'N/A')} sq.ft"
                    )
                
                # Description
                if prop.get("description"):
                    st.markdown("**📝 Description:**")
                    st.info(prop.get("description"))
                
                # Features
                if prop.get("features"):
                    st.markdown("**✨ Features:**")
                    features = prop.get("features", [])
                    if isinstance(features, list):
                        for feature in features:
                            st.write(f"• {feature}")
                    else:
                        st.write(f"• {features}")
                
                st.markdown("---")
    else:
        st.error(f"❌ {result.get('message', 'No properties found')}")

# ---------------------------
# Helper: Display Seller Response
# ---------------------------
def display_seller_response(result):
    if result.get("status") == "success":
        # Try different possible response structures
        properties = None
        
        if result.get("seller"):
            properties = result["seller"]
        elif result.get("data"):
            properties = result["data"]
        elif result.get("listings"):
            properties = result["listings"]
        elif result.get("properties"):
            properties = result["properties"]
        elif result.get("buyer"):  # Sometimes the response comes under "buyer" key
            properties = result["buyer"]
        else:
            # Maybe the result itself is the property data
            if isinstance(result, dict) and any(key in result for key in ["title", "price", "location", "description", "name"]):
                properties = [result]
        
        if properties:
            st.success("✅ Property Listed Successfully!")
            
            if not isinstance(properties, list):
                properties = [properties]
            
            for i, prop in enumerate(properties, 1):
                with st.container():
                    # Property Header
                    title = (prop.get('title') or prop.get('name') or 
                            prop.get('property_name') or f'Property Listing {i}')
                    st.markdown(f"### 🏡 {title}")
                    
                    # Property Details in Cards
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        price = (prop.get("price_in_inr") or prop.get("price") or 
                                prop.get("cost") or prop.get("amount") or 0)
                        st.metric(
                            label="💰 Listed Price",
                            value=f"₹{price:,}",
                            help=f"In words: {price_to_words(price)}"
                        )
                    
                    with col2:
                        location = (prop.get("location") or prop.get("address") or 
                                   prop.get("area") or "N/A")
                        st.metric(label="📍 Location", value=location)
                    
                    with col3:
                        size = (prop.get("size_sq_ft") or prop.get("size") or 
                               prop.get("area_sqft") or prop.get("sqft") or 0)
                        
                        price_per_sqft = prop.get("price_per_sqft", 0)
                        if price_per_sqft == 0 and size > 0 and price > 0:
                            price_per_sqft = price // size
                        
                        st.metric(
                            label="📏 Size",
                            value=f"{size} sq.ft",
                            delta=f"₹{price_per_sqft:,}/sq.ft" if price_per_sqft > 0 else None
                        )
                    
                    # Description
                    description = (prop.get("description") or prop.get("details") or 
                                 prop.get("summary") or prop.get("info"))
                    if description:
                        st.markdown("**📝 Property Description:**")
                        st.info(description)
                    
                    # Features
                    features = (prop.get("features") or prop.get("amenities") or 
                              prop.get("highlights") or prop.get("facilities"))
                    if features:
                        st.markdown("**✨ Property Features:**")
                        if isinstance(features, list):
                            feature_cols = st.columns(2)
                            for idx, feature in enumerate(features):
                                with feature_cols[idx % 2]:
                                    st.write(f"• {feature}")
                        else:
                            st.write(f"• {features}")
                    
                    # Market Analysis
                    market_analysis = (prop.get("market_analysis") or 
                                     prop.get("analysis") or prop.get("insights"))
                    if market_analysis:
                        st.markdown("**📊 Market Analysis:**")
                        st.info(market_analysis)
                    
                    st.markdown("---")
        else:
            st.warning("⚠️ Property listed but no detailed information available")
    else:
        st.error(f"❌ {result.get('message', 'Failed to list property')}")

# ---------------------------
# Helper: Display Price Estimator Response
# ---------------------------
def display_price_response(result):
    if result.get("status") == "success":
        st.success("✅ Price Estimation Complete!")
        
        # Try different possible price fields
        estimated_price = (result.get("estimated_price") or result.get("price") or 
                          result.get("valuation") or result.get("estimate") or 
                          result.get("predicted_price") or 0)
        
        # Handle buyer data if price estimation returns property suggestions
        if result.get("buyer") and not estimated_price:
            st.markdown("### 🏠 Property Suggestions Based on Your Requirements")
            display_buyer_response(result)
            return
        
        if estimated_price > 0:
            # Main price display
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown("### 💰 Estimated Property Value")
                st.markdown(f"# ₹{estimated_price:,}")
                st.markdown(f"**In words:** {price_to_words(estimated_price)}")
            
            with col2:
                size_sqft = (result.get("size_sqft") or result.get("size") or 
                           result.get("area") or 0)
                if size_sqft > 0:
                    price_per_sqft = estimated_price // size_sqft
                    st.metric(label="Per Sq.Ft Rate", value=f"₹{price_per_sqft:,}")
            
            with col3:
                location = (result.get("location") or result.get("area") or 
                          result.get("address") or "N/A")
                st.metric(label="Location", value=location)
        
        # Show estimation details in organized format
        st.markdown("### 📊 Estimation Details")
        
        # Create organized sections
        details_to_show = {}
        for key, value in result.items():
            if key not in ["status", "estimated_price", "price", "valuation", "estimate", "predicted_price", "buyer"] and value:
                details_to_show[key] = value
        
        if details_to_show:
            for key, value in details_to_show.items():
                display_key = key.replace('_', ' ').title()
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**{display_key}:**")
                with col2:
                    if isinstance(value, list):
                        for item in value:
                            st.write(f"• {item}")
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            st.write(f"• **{k.replace('_', ' ').title()}:** {v}")
                    else:
                        st.info(str(value))
    else:
        st.error(f"❌ {result.get('message', 'Could not estimate price')}")

# ---------------------------
# Helper: Display Neighborhood Response
# ---------------------------
def display_neighborhood_response(result, location):
    if result.get("status") == "success":
        st.success(f"✅ Neighborhood Information Retrieved for {location}")
        
        # Handle buyer data if neighborhood search returns property suggestions
        if result.get("buyer"):
            st.markdown("### 🏠 Available Properties in This Area")
            display_buyer_response(result)
            return
        
        # Try different data fields for neighborhood info
        data = (result.get("data") or result.get("neighborhood") or 
               result.get("info") or result.get("details") or {})
        
        if data or any(key not in ["status", "message", "buyer"] for key in result.keys()):
            st.markdown(f"### 🌆 {location} - Neighborhood Overview")
            
            # Combine data from both 'data' field and direct result fields
            all_info = {}
            if data:
                all_info.update(data)
            
            # Add other fields from result
            for key, value in result.items():
                if key not in ["status", "message", "data", "neighborhood", "info", "details", "buyer"] and value:
                    all_info[key] = value
            
            if all_info:
                # Display information in organized cards
                info_items = list(all_info.items())
                for i in range(0, len(info_items), 2):
                    col1, col2 = st.columns(2)
                    
                    # First item
                    if i < len(info_items):
                        key, value = info_items[i]
                        display_key = key.replace('_', ' ').title()
                        with col1:
                            st.markdown(f"**📍 {display_key}**")
                            if isinstance(value, list):
                                for item in value:
                                    st.write(f"• {item}")
                            elif isinstance(value, dict):
                                for k, v in value.items():
                                    st.write(f"• **{k}:** {v}")
                            else:
                                st.info(str(value))
                    
                    # Second item
                    if i + 1 < len(info_items):
                        key, value = info_items[i + 1]
                        display_key = key.replace('_', ' ').title()
                        with col2:
                            st.markdown(f"**📍 {display_key}**")
                            if isinstance(value, list):
                                for item in value:
                                    st.write(f"• {item}")
                            elif isinstance(value, dict):
                                for k, v in value.items():
                                    st.write(f"• **{k}:** {v}")
                            else:
                                st.info(str(value))
            else:
                st.info("Neighborhood information is available but no detailed data provided.")
        else:
            st.info("Neighborhood information retrieved successfully.")
    else:
        st.error(f"❌ {result.get('message', 'Could not fetch neighborhood info')}")

# ---------------------------
# Streamlit Configuration
# ---------------------------
st.set_page_config(page_title="Real Estate Multi-Agent System", layout="wide")

st.title("🏡 Real Estate Multi-Agent System")
st.markdown("*Professional real estate platform powered by AI agents*")

# Sidebar
agent_choice = st.sidebar.selectbox(
    "Choose Agent",
    ["Buyer Agent", "Seller Agent", "Price Estimator Agent", "Neighborhood Agent"]
)

# ---------------------------
# Buyer Agent
# ---------------------------
if agent_choice == "Buyer Agent":
    st.header("🔍 Property Search - Buyer Agent")
    st.markdown("Find your ideal property based on your preferences and budget")
    
    with st.form("buyer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input("🏙️ Preferred Location", placeholder="e.g., Koramangala, Bangalore")
            budget = st.number_input("💰 Budget (INR)", min_value=100000, step=100000, value=5000000)
        
        with col2:
            property_type = st.selectbox("🏘️ Property Type", ["Apartment", "Villa", "Plot", "Other"])
            requirements = st.text_area("📝 Additional Requirements", placeholder="e.g., 2BHK, near metro...")
        
        submitted = st.form_submit_button("🔍 Search Properties", use_container_width=True)
    
    if submitted:
        payload = {
            "location": location,
            "budget": budget,
            "property_type": property_type,
            "requirements": requirements,
        }
        
        with st.spinner("🔍 Searching for properties..."):
            result = call_agent("buyer", payload)
        
        display_buyer_response(result)

# ---------------------------
# Seller Agent
# ---------------------------
elif agent_choice == "Seller Agent":
    st.header("🏠 Property Listing - Seller Agent")
    st.markdown("List your property with professional market analysis and pricing")
    
    with st.form("seller_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            seller_name = st.text_input("👤 Seller Name", placeholder="Your name")
            contact = st.text_input("📞 Contact Info", placeholder="Phone/Email")
            location = st.text_input("📍 Property Location", placeholder="Complete address")
        
        with col2:
            size = st.number_input("📏 Size (sq.ft)", min_value=100, value=1000)
            price = st.number_input("💰 Expected Price (INR)", min_value=100000, step=100000, value=5000000)
        
        submitted = st.form_submit_button("🏠 List Property", use_container_width=True)
    
    if submitted:
        payload = {
            "seller_name": seller_name,
            "contact": contact,
            "property": {
                "location": location,
                "size_sqft": size,
                "price": price,
            }
        }
        
        with st.spinner("🏠 Creating property listing..."):
            result = call_agent("seller", payload)
        
        display_seller_response(result)

# ---------------------------
# Price Estimator Agent
# ---------------------------
elif agent_choice == "Price Estimator Agent":
    st.header("💰 Property Valuation - Price Estimator")
    st.markdown("Get accurate property valuations using AI-powered market analysis")
    
    with st.form("price_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input("📍 Property Location", placeholder="Area, City")
            size = st.number_input("📏 Size (sq.ft)", min_value=100, value=1000)
        
        with col2:
            bedrooms = st.number_input("🛏️ Bedrooms", min_value=1, max_value=10, value=2)
            bathrooms = st.number_input("🚿 Bathrooms", min_value=1, max_value=10, value=2)
        
        submitted = st.form_submit_button("💰 Get Price Estimate", use_container_width=True)
    
    if submitted:
        payload = {
            "location": location,
            "size_sqft": size,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
        }
        
        with st.spinner("💰 Analyzing market data..."):
            result = call_agent("price", payload)
        
        display_price_response(result)

# ---------------------------
# Neighborhood Agent
# ---------------------------
elif agent_choice == "Neighborhood Agent":
    st.header("🌆 Area Analysis - Neighborhood Agent")
    st.markdown("Discover comprehensive insights about any neighborhood")
    
    with st.form("neighborhood_form"):
        location = st.text_input("📍 Enter Location", placeholder="Area name, City", value="")
        
        submitted = st.form_submit_button("🌆 Get Neighborhood Info", use_container_width=True)
    
    if submitted and location:
        payload = {"location": location}
        
        with st.spinner("🌆 Analyzing neighborhood..."):
            result = call_agent("neighborhood", payload)
        
        display_neighborhood_response(result, location)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("*🏡 Real Estate Multi-Agent System - Powered by AI*")