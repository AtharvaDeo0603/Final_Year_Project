import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from model import EWasteClassifier
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import tempfile
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta


st.set_page_config(page_title="E-Waste System", layout="wide")

# Initialize classifier
classifier = EWasteClassifier()

####################################################################
import streamlit as st
import pyrebase

# Firebase Configuration (Replace with your own)
firebaseConfig = {
    "apiKey": "AIzaSyCjMwlSeDjKtLsW_9L5eaUHGOjmS8QLKqg",
    "authDomain": "e-waste-project-54032.firebaseapp.com",
    "databaseURL": "https://e-waste-project-54032-default-rtdb.firebaseio.com/",
    "projectId": "e-waste-project-54032",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "YOUR_APP_ID"

}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()  # ✅ Initialize Firebase Database

# Set page title & layout
#st.set_page_config(page_title="E-Waste System", layout="wide")
st.sidebar.image("logo.png", use_container_width =True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

# Login/Signup Page
def login_page():
    st.title("🔐 Login to Your Account")
    
    choice = st.selectbox("Login or Sign Up", ["Login", "Sign Up"])

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if choice == "Sign Up":
        if st.button("Create Account"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("✅ Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

    elif choice == "Login":
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)  # ✅ Authenticate user
                user_info = auth.refresh(user['refreshToken'])  # ✅ Refresh Token to prevent expiration

                # ✅ Store authentication details in session state
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.session_state["user_token"] = user_info['idToken']  # ✅ Store fresh token

                st.success(f"✅ Welcome, {email}!")
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Login failed: {e}")

    if st.session_state["logged_in"]:
        st.sidebar.success(f"Logged in as {st.session_state['user_email']}")
        return True
    else:
        return False

# Main Application
def main():
    if not st.session_state["logged_in"]:
        login_page()
    else:
        st.sidebar.title(f"👤 Welcome, {st.session_state['user_email']}")
        if st.sidebar.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["user_email"] = ""
            st.rerun()
        
        # Sidebar Navigation
        page = st.sidebar.radio("🔍 Navigation", ["🏠 Home", "📊 Dashboard", "📍 Recycling Centers", "💰 Price Estimator", "🚛 E-Waste Pickup", "🏆 Leaderboard", "🤖 Chatbot", "Sell for Parts", "Marketplace", "ℹ️ About"])
        
        # Load pages dynamically
        if page == "🏠 Home":
            home_page()
        elif page == "📊 Dashboard":
            show_recycling_dashboard()
        elif page == "📍 Recycling Centers":
            show_recycling_centers()
        elif page == "💰 Price Estimator":
            show_price_estimator()
        elif page == "🚛 E-Waste Pickup":
            show_pickup_request_page()
        elif page == "🏆 Leaderboard":
            show_leaderboard()
        elif page == "🤖 Chatbot":
            show_chatbot()
        elif page == "Sell for Parts":
            home_page()  # Opens the selling form from home page
        elif page == "Marketplace":
            show_sell_listings()  # Opens the marketplace to browse listings
        elif page == "ℹ️ About":
            about_page()

# Load or initialize user data
USER_DATA_FILE = "user_recycling_data.csv"

#def load_user_data():
#    try:
#        df = pd.read_csv(USER_DATA_FILE)
        # Ensure new columns exist
#        if "Streak Count" not in df.columns:
#            df["Streak Count"] = 0
#            df["Last Recycled Date"] = ""
#    except FileNotFoundError:
#        df = pd.DataFrame(columns=["Category", "Items Recycled", "Credit Points", "Streak Count", "Last Recycled Date"])
    
#    return df

def load_user_data():
    """Load the logged-in user's recycling data from Firebase."""
    user_email = st.session_state.get("user_email", "")
    user_token = st.session_state.get("user_token", "")

    if not user_email or not user_token:
        return pd.DataFrame(columns=["Category", "Items Recycled", "Credit Points", "Streak Count", "Last Recycled Date"])

    try:
        # ✅ Fetch user data from Firebase
        user_data = db.child("users").child(user_email.replace(".", ",")).get(user_token).val()

        # ✅ Ensure user_data is a dictionary, not a list
        if isinstance(user_data, list):
            user_data = {str(i): entry for i, entry in enumerate(user_data) if isinstance(entry, dict)}

        if isinstance(user_data, dict):
            return pd.DataFrame.from_dict(user_data, orient="index")
        else:
            return pd.DataFrame(columns=["Category", "Items Recycled", "Credit Points", "Streak Count", "Last Recycled Date"])

    except Exception as e:
        st.error(f"⚠️ Error fetching user data: {e}")
        return pd.DataFrame(columns=["Category", "Items Recycled", "Credit Points", "Streak Count", "Last Recycled Date"])

#def save_user_data(df):
#    df.to_csv(USER_DATA_FILE, index=False)

def save_user_data(df):
    """Save the logged-in user's recycling data to Firebase."""
    user_email = st.session_state.get("user_email", "")
    user_token = st.session_state.get("user_token", "")

    if not user_email or not user_token:
        return

    try:
        db.child("users").child(user_email.replace(".", ",")).set(df.to_dict(orient="index"), user_token)
    except Exception as e:
        st.error(f"⚠️ Error saving user data: {e}")



# Sidebar Navigation
def sidebar_navigation():
    st.sidebar.title("🔍 Navigation")
    return st.sidebar.radio("Go to", ["Home", "Dashboard", "Recycling Centers","Price Estimator", "E-Waste Pickup", "Leaderboard", "Chatbot", "About"])

# Home Page (Upload & Classification)
def home_page():
    st.title("♻️ E-Waste Classification System")
    st.header("Upload E-Waste Image")
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Image', width=300)
        
        try:
            result = classifier.predict(uploaded_file)
            
            if result['confidence'] < 0.70:
                st.warning("❌ Not an E-Waste. Please upload a different image.")
            else:
                st.success(f"✅ Identified as: {result['class']}")
                st.info(f"📊 Confidence: {result['confidence']:.2%}")
                st.success(f"🎉 You earned {result['points']} credit points!")

                # Metal composition details
                
                METALS = {
    'Batteries': '🔋 Lithium, Lead, Cobalt, Nickel - Used in rechargeable batteries, extracted for reuse in new batteries and electronics.',
    'Mobile & PCBs': '📱 Gold, Silver, Copper, Rare Earth Elements - Valuable metals recovered for use in semiconductors and circuit boards.',
    'Peripherals': '🖥️ Plastic, Copper, Gold Plating - Plastic casings are recycled, while metals are extracted for manufacturing.',
    'Printers & Screens': '🖨 Steel, Aluminum, Copper - Recycled for use in construction and new electronic devices.',
    'Large Appliances': '⚡ Steel, Copper, Aluminum - Essential materials recovered for new appliances and industrial use.',
    'Mixed Electronics': '♻️ Various components, requires manual sorting - Components are sorted for separate recycling processes to maximize material recovery.'
}

                st.info(f"🔬 Metal Composition: {METALS.get(result['class'], 'Unknown')}")

                # Load and update user data
                user_data = load_user_data()
                today = datetime.today().strftime('%Y-%m-%d')

                if result['class'] in user_data["Category"].values:
                    idx = user_data[user_data["Category"] == result['class']].index[0]

                    # Update items recycled & points
                    user_data.loc[idx, "Items Recycled"] += 1
                    user_data.loc[idx, "Credit Points"] += result['points']

                    # Check streak
                    last_recycled = user_data.loc[idx, "Last Recycled Date"]
                    if last_recycled:
                        last_recycled = datetime.strptime(last_recycled, '%Y-%m-%d')
                        if last_recycled == datetime.today() - timedelta(days=1):
                            user_data.loc[idx, "Streak Count"] += 1  # Continue streak
                        elif last_recycled < datetime.today() - timedelta(days=1):
                            user_data.loc[idx, "Streak Count"] = 1  # Reset streak
                    else:
                        user_data.loc[idx, "Streak Count"] = 1  # First-time recycler

                    user_data.loc[idx, "Last Recycled Date"] = today

                else:
                    new_entry = pd.DataFrame([[result['class'], 1, result['points'], 1, today]],
                                            columns=["Category", "Items Recycled", "Credit Points", "Streak Count", "Last Recycled Date"])
                    user_data = pd.concat([user_data, new_entry], ignore_index=True)

                save_user_data(user_data)
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")


def home_page():
    st.title("♻️ Welcome to the E-Waste Management System")
    st.markdown("### A smart way to dispose of e-waste responsibly while earning rewards! 💡")

    # 🚀 Quick Guide
    with st.expander("📖 How It Works"):
        st.markdown("""
        1️⃣ **Upload an Image** – Identify your e-waste category.  
        2️⃣ **Earn Credit Points** – Get rewarded for recycling responsibly.  
        3️⃣ **Check Price Estimation** – See how much your e-waste is worth.  
        4️⃣ **Locate Recycling Centers** – Find nearby certified e-waste facilities.  
        5️⃣ **Request Pickup** – Schedule collection for large appliances.  
        6️⃣ **Compete on Leaderboard** – Track your progress and earn badges! 🏆
        """)

    # 🌍 Why Recycle?
    st.markdown("### 🌱 Why Should You Recycle E-Waste?")
    st.info("**✅ Reduces Pollution** – Prevents toxic materials from contaminating soil & water.  \n"
            "**✅ Saves Resources** – Extracts valuable metals for reuse in new devices.  \n"
            "**✅ Earn Rewards** – Gain credit points for every item recycled!  \n"
            "**✅ Supports Sustainability** – Helps create a cleaner, greener future. 🌍")

    # 📊 Total E-Waste Recycled
    user_data = load_user_data()
    total_recycled = user_data["Items Recycled"].sum() if not user_data.empty else 0
    st.metric(label="🌍 Total E-Waste Recycled", value=f"{total_recycled} items")

    # 🚀 Get Started Section
    st.markdown("### 🚀 Ready to Recycle?")
    
    st.title("♻️ Upload E-Waste Image")
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Image', width=300)
        
        try:
            result = classifier.predict(uploaded_file)
            
            if result['confidence'] < 0.70:
                st.warning("❌ Not an E-Waste. Please upload a different image.")
            else:
                st.success(f"✅ Identified as: {result['class']}")
                st.info(f"📊 Confidence: {result['confidence']:.2%}")
                st.success(f"🎉 You earned {result['points']} credit points!")

                # Metal composition details
                METALS = {
                    'Batteries': '🔋 Lithium, Lead, Cobalt, Nickel - Used in rechargeable batteries.',
                    'Mobile & PCBs': '📱 Gold, Silver, Copper, Rare Earth Elements - Valuable for semiconductors.',
                    'Peripherals': '🖥️ Plastic, Copper, Gold Plating - Recycled for manufacturing.',
                    'Printers & Screens': '🖨 Steel, Aluminum, Copper - Used in new electronics.',
                    'Large Appliances': '⚡ Steel, Copper, Aluminum - Reused in new appliances.',
                    'Mixed Electronics': '♻️ Various components, requires manual sorting.'
                }
                st.info(f"🔬 Metal Composition: {METALS.get(result['class'], 'Unknown')}")

                # Load and update user data
                user_data = load_user_data()
                today = datetime.today().strftime('%Y-%m-%d')

                if result['class'] in user_data["Category"].values:
                    idx = user_data[user_data["Category"] == result['class']].index[0]
                    user_data.loc[idx, "Items Recycled"] += 1
                    user_data.loc[idx, "Credit Points"] += result['points']

                    last_recycled = user_data.loc[idx, "Last Recycled Date"]
                    if last_recycled:
                        last_recycled = datetime.strptime(last_recycled, '%Y-%m-%d')
                        if last_recycled == datetime.today() - timedelta(days=1):
                            user_data.loc[idx, "Streak Count"] += 1
                        elif last_recycled < datetime.today() - timedelta(days=1):
                            user_data.loc[idx, "Streak Count"] = 1
                    else:
                        user_data.loc[idx, "Streak Count"] = 1

                    user_data.loc[idx, "Last Recycled Date"] = today

                else:
                    new_entry = pd.DataFrame([[result['class'], 1, result['points'], 1, today]],
                                            columns=["Category", "Items Recycled", "Credit Points", "Streak Count", "Last Recycled Date"])
                    user_data = pd.concat([user_data, new_entry], ignore_index=True)

                save_user_data(user_data)
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
    
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Show my Recycling Dashboard"):
            st.session_state.page = "Dashboard"
    with col2:
        if st.button("📍 Find Recycling Centers"):
            st.session_state.page = "Recycling Centers"

    if st.session_state.page == "Dashboard":
        show_recycling_dashboard()
    elif st.session_state.page == "Recycling Centers":
        show_recycling_centers()
    
    if st.button("💰 Sell Valuable Components"):
        with st.form("sell_form", clear_on_submit=True):
            st.write("📦 List Your Valuable Components for Sale")
            seller_name = st.text_input("Your Name")
            contact_info = st.text_input("Contact Details (Email/Phone)")

            # ✅ Load components dynamically based on the detected device type
            component_data = load_component_data()
            if component_data is not None:
                components_available = component_data.loc[
                    component_data["Device Type"] == result["class"], "Components Present"
                ].values  # Fetch components for detected device

                if len(components_available) > 0:
                    components_available = components_available[0].split(", ")  # Convert to list
                else:
                    components_available = ["No data available"]

            else:
                components_available = ["Error loading components"]

            # ✅ Dropdown now dynamically lists components
            components_to_sell = st.multiselect("Select Components to Sell", components_available)

            price_expectation = st.number_input("Expected Price (₹)", min_value=0, step=100)

            submit_button = st.form_submit_button("Submit Listing")

            if submit_button:
                if seller_name and contact_info and components_to_sell:
                    # ✅ Save the listing
                    new_listing = pd.DataFrame([[seller_name, contact_info, result["class"], ", ".join(components_to_sell), price_expectation, datetime.today().strftime('%Y-%m-%d')]], 
                                   columns=["Seller Name", "Contact Info", "Device Type", "Components", "Expected Price", "Date Listed"])

                    try:
                        existing_data = pd.read_csv("sell_listings.csv")
                        updated_data = pd.concat([existing_data, new_listing], ignore_index=True)
                    except FileNotFoundError:
                        updated_data = new_listing

                    updated_data.to_csv("sell_listings.csv", index=False)

                    # ✅ Show Success Message
                    st.success("✅ Your listing has been submitted successfully!")

                    # ✅ Further Directions for the User
                    st.info("📢 **Next Steps:**\n"
                            "- Your listing is now live in the **Marketplace**.\n"
                            "- Interested buyers will contact you directly.\n"
                            "- You can manage your listings in the **Dashboard**.\n"
                            "- If you want to sell another device, click **'Sell More Parts'** below.")

                    # ✅ Add a "Sell More Parts" button
                    if st.button("💰 Sell More Parts"):
                        st.experimental_rerun()  # Reload the form for a new listing
                    else:
                        st.warning("⚠️ Please fill in all fields.")



    st.markdown("---")
    st.markdown("🔎 **Explore More Features:**")
    st.write("📊 [Dashboard](#) | 💰 [Price Estimator](#) | 🚛 [Request Pickup](#) | 🏆 [Leaderboard](#) | 🤖 [Chatbot](#)")


# Load e-waste component database
def load_component_data():
    try:
        return pd.read_csv("ewaste_components.csv")
    except FileNotFoundError:
        return None  # Handle missing file

def show_recycling_centers():
    st.title("📍 Nearby Recycling Centers")
    st.write("Find the nearest recycling centers in Nashik and contribute to a cleaner environment!")

    # Define Recycling Center Locations (Latitude, Longitude)
    data = pd.DataFrame({
        'lat': [19.9975, 19.9854, 19.9615],  # Latitude of centers
        'lon': [73.7898, 73.7740, 73.7633],  # Longitude of centers
        'name': ["EcoRecycle Center", "GreenTech Recyclers", "E-Waste Solutions"]
    })

    # Display Interactive Map with Streamlit's `st.map()`
    st.map(data, zoom=12)

    # Display Recycling Center List
    for i, row in data.iterrows():
        st.write(f"**{row['name']}** - 📍 ({row['lat']}, {row['lon']})")



def show_recycling_centers():
    st.title("📍 Nearby Recycling Centers")
    st.write("Find the nearest recycling centers in Nashik and contribute to a cleaner environment!")

    # Define Recycling Center Locations with More Details
    centers = [
        {"name": "EcoRecycle Center", "lat": 19.9975, "lon": 73.7898, "address": "123 Green St", "contact": "555-0123"},
        {"name": "GreenTech Recyclers", "lat": 19.9854, "lon": 73.7740, "address": "456 Tech Ave", "contact": "555-0456"},
        {"name": "E-Waste Solutions", "lat": 19.9615, "lon": 73.7633, "address": "789 Recycle Rd", "contact": "555-0789"}
    ]

    # Create a Folium Map Centered Around Nashik
    m = folium.Map(location=[19.9975, 73.7898], zoom_start=12, control_scale=True)

    # Add Markers with Details
    for center in centers:
        folium.Marker(
            location=[center["lat"], center["lon"]],
            popup=f"<b>{center['name']}</b><br>📍 {center['address']}<br>📞 {center['contact']}",
            tooltip=center["name"],
            icon=folium.Icon(color="green", icon="recycle", prefix="fa")
        ).add_to(m)

    # Display the Map in Streamlit
    folium_static(m)

    # Display Recycling Center List
    st.markdown("### 📜 List of Recycling Centers")
    for center in centers:
        st.markdown(f"**{center['name']}** - 📍 {center['address']} - 📞 {center['contact']}")



# Predefined responses for common recycling questions
FAQ_RESPONSES = {
    "What is e-waste?": "E-waste refers to discarded electrical or electronic devices such as mobiles, laptops, and TVs.",
    "Where can I recycle e-waste?": "You can drop off e-waste at certified recycling centers. Check the 'Recycling Centers' page in this app.",
    "Why is e-waste recycling important?": "E-waste contains hazardous materials that can harm the environment. Recycling helps recover valuable metals and reduces pollution.",
    "Can I get money for recycling e-waste?": "Yes! Some recyclers offer cash or discounts for old electronics. Use the 'Price Estimator' to check e-waste value.",
    "What items can be recycled?": "Common recyclable items include laptops, mobiles, TVs, batteries, refrigerators, and washing machines.",
    "How do I schedule a pickup?": "You can request an e-waste pickup from our 'E-Waste Pickup' page in this app."
}

def show_chatbot():
    st.title("🤖 E-Waste Chatbot")

    # Chat Interface
    user_question = st.text_input("Ask me anything about e-waste recycling:")

    if st.button("Ask"):
        response = FAQ_RESPONSES.get(user_question, "I'm sorry, I don't have an answer for that yet. Try asking another question.")
        st.write("💬 **Chatbot:**", response)




PICKUP_REQUESTS_FILE = "pickup_requests.csv"

def show_pickup_request_page():
    st.title("🚛 Request an E-Waste Pickup")

    # User Inputs
    name = st.text_input("Your Name")
    contact = st.text_input("Contact Number")
    address = st.text_area("Pickup Address")
    item_type = st.selectbox("Type of E-Waste", ["Laptop", "Mobile", "TV", "Refrigerator", "Washing Machine", "Other"])
    preferred_date = st.date_input("Preferred Pickup Date")

    if st.button("📦 Request Pickup"):
        if name and contact and address:
            # Save request
            new_request = pd.DataFrame([[name, contact, address, item_type, preferred_date]], 
                                       columns=["Name", "Contact", "Address", "Item Type", "Pickup Date"])

            try:
                existing_requests = pd.read_csv(PICKUP_REQUESTS_FILE)
                updated_requests = pd.concat([existing_requests, new_request], ignore_index=True)
            except FileNotFoundError:
                updated_requests = new_request  # First entry

            updated_requests.to_csv(PICKUP_REQUESTS_FILE, index=False)
            st.success("✅ Your pickup request has been submitted successfully!")
        else:
            st.warning("⚠️ Please fill in all required fields.")

    # Show past pickup requests
    st.markdown("### 📜 Your Past Pickup Requests")
    try:
        past_requests = pd.read_csv(PICKUP_REQUESTS_FILE)
        st.table(past_requests)
    except FileNotFoundError:
        st.info("No pickup requests submitted yet.")

def show_leaderboard():
    st.title("🏆 Top Recycled Items Leaderboard")

    # Load user recycling data
    try:
        user_data = pd.read_csv("user_recycling_data.csv")

        if user_data.empty:
            st.info("No recycling data available yet.")
            return

        # Sort by Credit Points (or Items Recycled)
        leaderboard = user_data.groupby("Category").agg(
            {"Items Recycled": "sum", "Credit Points": "sum"}
        ).reset_index()

        leaderboard = leaderboard.sort_values(by="Credit Points", ascending=False)

        # Display the leaderboard table
        st.table(leaderboard)

    except FileNotFoundError:
        st.warning("No data found. Start recycling to appear on the leaderboard!")

#price prediction

import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Load the trained model
model = joblib.load("ewaste_price_model.pkl")

# Define device categories and conditions
device_types = ["Laptop", "Mobile", "TV", "Refrigerator", "Washing Machine", "Monitor", "Tablet"]
conditions = ["New", "Used", "Damaged"]
brands = ["Apple", "Samsung", "Dell", "HP", "Sony", "LG", "Lenovo", "Panasonic", "OnePlus", "Asus"]
market_demand_levels = ["Low", "Medium", "High"]

def show_price_estimator():
    st.title("💰 E-Waste Price Estimator")

    st.markdown("🔢 **Enter details to estimate the e-waste price**")
    
    # User Inputs
    device_type = st.selectbox("Device Type", device_types)
    #weight = st.number_input("Weight (kg)", min_value=0.1, max_value=100.0, step=0.1)
    condition = st.selectbox("Condition", conditions)
    brand = st.selectbox("Brand", brands)
    market_demand = st.selectbox("Market Demand", market_demand_levels)

    if st.button("Estimate Price"):
        # Convert inputs into the format expected by the model
        input_data = pd.DataFrame([[device_type, condition, brand, market_demand]], 
                                  columns=['Device Type', 'Condition', 'Brand', 'Market Demand'])

        # Perform one-hot encoding (ensure column names match model)
        input_data = pd.get_dummies(input_data)
        model_columns = joblib.load("model_columns.pkl")  # Load saved column order
        input_data = input_data.reindex(columns=model_columns, fill_value=0)

        # Make prediction
        predicted_price = model.predict(input_data)

        st.success(f"💰 Estimated E-Waste Price: ₹{predicted_price[0]:,.2f}")


def show_recycling_dashboard():
    st.title("📊 Your Recycling Dashboard")
    
    # ✅ Load user-specific data
    user_data = load_user_data()
    
    if user_data.empty:
        st.warning("No recycling data available. Start by uploading e-waste images!")
    else:
        st.subheader("📋 Recycling Summary")
        st.table(user_data)
        
        # Total statistics
        total_points = user_data["Credit Points"].sum()
        total_recycled = user_data["Items Recycled"].sum()
        highest_streak = user_data["Streak Count"].max()
        
        # Define Badges
        def get_badge(total_recycled):
            if total_recycled >= 50:
                return "🌍 Earth Saver"
            elif total_recycled >= 30:
                return "♻️ Sustainability Hero"
            elif total_recycled >= 15:
                return "🔋 Green Recycler"
            elif total_recycled >= 5:
                return "🌱 Eco Starter"
            else:
                return "🏁 Keep Recycling!"
        
        badge = get_badge(total_recycled)
        
        # Show streaks and badges
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="🔥 Longest Streak", value=f"{highest_streak} days")
        with col2:
            st.metric(label="🏆 Your Badge", value=badge)
        with col3:
            st.metric(label="🌱 Total Credit Points Earned", value=total_points)
        
        # Generate and Download PDF Report
        if st.button("📥 Download Recycling Report"):
            pdf_buffer = generate_pdf_report(user_data)
            st.download_button("Download Report", pdf_buffer, file_name="Recycling_Report.pdf", mime="application/pdf")

def generate_pie_chart(user_data):
    plt.figure(figsize=(5, 5))
    plt.pie(user_data["Items Recycled"], labels=user_data["Category"], autopct='%1.1f%%', startangle=90)
    plt.title("Recycled E-Waste Distribution")
    
    # Save chart as BytesIO object
    chart_stream = BytesIO()
    plt.savefig(chart_stream, format='png')
    plt.close()
    
    return chart_stream

def generate_pdf_report(user_data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    pdf.setTitle("E-Waste Recycling Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(300, 770, "E-Waste Recycling Report")
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 730, f"Total Items Recycled: {user_data['Items Recycled'].sum()}")
    pdf.drawString(50, 710, f"Total Credit Points Earned: {user_data['Credit Points'].sum()}")
    
    # Load pie chart
    chart_stream = generate_pie_chart(user_data)
    
    # Save the pie chart as a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_chart:
        temp_chart.write(chart_stream.getvalue())
        temp_chart_path = temp_chart.name
    
    # Draw the saved image in the PDF
    pdf.drawImage(ImageReader(temp_chart_path), 150, 500, width=300, height=200)
    
    # Detailed Recycling Report
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 470, "Detailed Recycling Breakdown:")
    
    pdf.setFont("Helvetica", 12)
    y = 450
    for index, row in user_data.iterrows():
        pdf.drawString(50, y, f"{row['Category']}: {row['Items Recycled']} items recycled, {row['Credit Points']} points earned")
        y -= 20
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 750
    
    # Incentives & Environmental Impact Section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y - 30, "💰 Government Incentives & Benefits:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y - 50, "✔️ Tax deductions for responsible e-waste disposal.")
    pdf.drawString(50, y - 70, "✔️ Eligibility for cashback or rebates under green programs.")
    pdf.drawString(50, y - 90, "✔️ Certification for corporate social responsibility (CSR) contributions.")
    
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y - 120, "🌿 Environmental Impact:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y - 140, "✔️ Reduction of hazardous waste in landfills.")
    pdf.drawString(50, y - 160, "✔️ Conservation of rare metals and valuable resources.")
    pdf.drawString(50, y - 180, "✔️ Contribution to a cleaner and greener planet.")
    
    pdf.save()
    buffer.seek(0)
    return buffer


# Recycling Centers Page
def recycling_centers_page():
    st.title("📍 Nearby Recycling Centers")

    facilities = pd.DataFrame({
        'Name': ['EcoRecycle Center', 'GreenTech Recyclers', 'E-Waste Solutions'],
        'Address': ['123 Green St', '456 Tech Ave', '789 Recycle Rd'],
        'Distance': ['2.5 km', '3.8 km', '5.1 km'],
        'Contact': ['555-0123', '555-0456', '555-0789']
    })

    for _, facility in facilities.iterrows():
        st.markdown(f"**{facility['Name']}** - 📍 {facility['Address']} - 📞 {facility['Contact']} - 🚗 {facility['Distance']}")

# About Page

def about_page():
    st.title("ℹ️ About This App")
        #st.write("This AI-powered system classifies e-waste and encourages responsible recycling through a credit system.")    
    st.markdown("""
    ## ♻️ E-Waste Management System
    Welcome to the **E-Waste Management System**! This platform helps individuals and businesses 
    **dispose of electronic waste responsibly** while earning rewards. Our goal is to 
    **reduce environmental pollution** and promote sustainable recycling practices.

    ---
    
    ## 🌍 Why E-Waste Recycling Matters?
    - **Hazardous Materials:** E-waste contains **toxic substances** like lead, mercury, and cadmium that can harm the environment.
    - **Recovering Precious Metals:** Recycling helps extract **gold, silver, copper, and rare earth elements** for reuse.
    - **Reducing Landfill Waste:** Proper e-waste disposal prevents electronic devices from piling up in landfills.

    ---

    ## ⚡ Key Features
    - ✅ **E-Waste Classification System** – Identify different categories of e-waste.
    - ✅ **E-Waste Price Estimator** – Get an estimated value for your discarded electronics.
    - ✅ **Nearby Recycling Centers** – Locate certified recycling centers near you.
    - ✅ **E-Waste Pickup Requests** – Schedule a pickup for large appliances and electronics.
    - ✅ **Leaderboard & Rewards** – Earn points for responsible recycling and track progress.
    - ✅ **Chatbot Support** – Find answers to common recycling-related questions.

    ---

    ## 🏆 Our Mission
    We aim to **create awareness** and encourage people to **recycle e-waste properly** by making it:
    - 🔹 **Easy to dispose of electronics** with local recycling centers.
    - 🔹 **Rewarding for recyclers** through incentives and leaderboard challenges.
    - 🔹 **Sustainable** by promoting **eco-friendly disposal practices**.

    ---

    ## 📞 Contact & Support
    Have questions? Need assistance? Reach out to us!
    - 📩 **Email:** support@ewasteapp.com
    - 🌐 **Website:** www.ewasteapp.com
    """)

def show_sell_listings():
    st.title("🛒 E-Waste Parts Marketplace")
    st.write("🔎 Browse valuable e-waste components listed for sale.")

    try:
        listings = pd.read_csv("sell_listings.csv")
        if listings.empty:
            st.info("No listings available yet. Be the first to sell!")
        else:
            for _, row in listings.iterrows():
                with st.expander(f"{row['Device Type']} - {row['Components']}"):
                    st.write(f"📅 **Date Listed:** {row['Date Listed']}")
                    st.write(f"💰 **Expected Price:** ₹{row['Expected Price']}")
                    st.write(f"📞 **Seller Contact:** {row['Contact Info']}")
                    st.write("---")
    except FileNotFoundError:
        st.info("No listings available yet. Start by selling your e-waste parts!")


if __name__ == "__main__":
    main()
