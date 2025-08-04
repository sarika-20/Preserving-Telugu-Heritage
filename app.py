import streamlit as st
import geocoder
import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import glob

# ---------------------- Language Toggle ---------------------- #
if "language" not in st.session_state:
    st.session_state.language = "English"

lang_toggle = st.button("🌐 Change Language (Current: English)" if st.session_state.language == "English" else "🌐 భాష మార్చండి (ప్రస్తుతము: తెలుగు)")

if lang_toggle:
    st.session_state.language = "Telugu" if st.session_state.language == "English" else "English"

TEXT = {
    "English": {
        "title": "Preserving Telugu Heritage",
        "welcome": "Welcome to the Telugu Cultural Collection Portal!",
        "home_subheading": "✨ Let’s celebrate the voices of our people, one story at a time.",
        "home_description": """
🧚 Explore and preserve our culture through:

- 📚 **Fairy Tales** passed through generations  
- 🏞️ **Place-Based Histories** from your region

Share your story or explore others — in your language, your voice, your memories.
        """,
        "sections": ["🏠 Home", "📚 Fairy Tales", "🏞️ Place-Based Histories"],
        "sub_actions": ["📬 Submit", "📖 Read"],
        "name": "Full Name",
        "age": "Age",
        "location": "Your Current Location",
        "story_title": "Story Title",
        "story_summary": "Short Description / Summary",
        "story_moral": "Moral of the Story",
        "submit_btn": "📬 Submit Story",
        "success_msg": "Thank you! Your story has been submitted successfully.",
        "error_msg": "⚠️ Please fill in all fields correctly.",
        "place_title": "Place Name",
        "place_desc": "Describe the Place",
        "place_significance": "Historical or Cultural Importance",
        "place_submit_btn": "📬 Submit History",
        "read_title": "📖 Submitted Telugu Folk Tales",
        "place_read_title": "📖 Submitted Place-Based Histories"
    },
    "Telugu": {
        "title": "తెలుగు వారసత్వాన్ని సంరక్షించండి",
        "welcome": "తెలుగు సాంస్కృతిక సేకరణ పోర్టల్‌కు స్వాగతం!",
        "home_subheading": "✨ మన కథల ద్వారా మన స్వరం మళ్లీ వినిపిద్దాం.",
"home_description": """
🧚 మన సంస్కృతిని అన్వేషించండి మరియు పరిరక్షించండి:

- 📚 తరాలుగా చెప్పుకొస్తున్న **జానపద కథలు**  
- 🏞️ మన ప్రాంతంలోని **ప్రదేశ ఆధారిత చరిత్రలు**

మీ కథను పంచుకోండి లేదా ఇతరుల కథలను అన్వేషించండి — మీ భాషలో, మీ స్వరంలో, మీ జ్ఞాపకాలతో.
""",
        "sections": ["🏠 హోమ్", "📚 జానపద కథలు", "🏞️ చారిత్రక ప్రదేశాలు"],
        "sub_actions": ["📬 సమర్పించు", "📖 చదువు"],
        "name": "పూర్తి పేరు",
        "age": "వయస్సు",
        "location": "మీ ప్రస్తుత స్థానము",
        "story_title": "కథ శీర్షిక",
        "story_summary": "చిన్న వివరణ",
        "story_moral": "కథ నైతికత",
        "submit_btn": "📬 కథను సమర్పించు",
        "success_msg": "ధన్యవాదాలు! మీ కథ విజయవంతంగా సమర్పించబడింది.",
        "error_msg": "⚠️ దయచేసి అన్ని ఖాళీలను సరైన రీతిలో పూరించండి.",
        "place_title": "ప్రదేశం పేరు",
        "place_desc": "ప్రదేశాన్ని వివరించండి",
        "place_significance": "చారిత్రక లేదా సాంస్కృతిక ప్రాముఖ్యత",
        "place_submit_btn": "📬 చారిత్రక సమాచారం సమర్పించు",
        "read_title": "📖 సమర్పించిన జానపద కథలు",
        "place_read_title": "📖 సమర్పించిన ప్రదేశాల చరిత్రలు"
    }
}

# ---------------------- Page Config ---------------------- #
st.set_page_config(page_title=TEXT[st.session_state.language]["title"], layout="centered")
st.sidebar.title("📂 Navigate")
main_page = st.sidebar.selectbox("Choose Section", TEXT[st.session_state.language]["sections"])

if main_page != TEXT[st.session_state.language]["sections"][0]:
    sub_page = st.sidebar.radio("Choose Action", TEXT[st.session_state.language]["sub_actions"])

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///story_submissions.db")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(String)
    location = Column(String)
    story_title = Column(String)
    story_summary = Column(Text)
    story_moral = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PlaceHistory(Base):
    __tablename__ = 'place_histories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(String)
    location = Column(String)
    place_name = Column(String)
    place_description = Column(Text)
    historical_significance = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

for folder in ["stories", "place_histories", "admin_data"]:
    os.makedirs(folder, exist_ok=True)

# ---------------------- Home ---------------------- #
if main_page == TEXT[st.session_state.language]["sections"][0]:
    st.title("🌟 " + TEXT[st.session_state.language]["title"])
    st.markdown(f"### {TEXT[st.session_state.language]['welcome']}")
    st.markdown(f"##### {TEXT[st.session_state.language]['home_subheading']}")
    st.markdown(TEXT[st.session_state.language]['home_description'])

# ---------------------- Fairy Tales ---------------------- #
elif main_page == TEXT[st.session_state.language]["sections"][1]:
    if sub_page == TEXT[st.session_state.language]["sub_actions"][0]:
        st.title(TEXT[st.session_state.language]["submit_btn"])
        try:
            location_info = geocoder.ip('me')
            location = f"{location_info.city}, {location_info.country}" if location_info.ok else "Unavailable"
        except:
            location = "Unavailable"
        st.markdown(f"📍 **{TEXT[st.session_state.language]['location']}:** `{location}`")

        name = st.text_input(TEXT[st.session_state.language]["name"])
        age = st.text_input(TEXT[st.session_state.language]["age"])
        story_title = st.text_input(TEXT[st.session_state.language]["story_title"])
        story_summary = st.text_area(TEXT[st.session_state.language]["story_summary"])
        story_moral = st.text_input(TEXT[st.session_state.language]["story_moral"])

        if st.button(TEXT[st.session_state.language]["submit_btn"]):
            if not name or not age or not story_title or not story_summary or not story_moral or not age.isdigit():
                st.error(TEXT[st.session_state.language]["error_msg"])
            else:
                story = Story(name=name, age=age, location=location,
                              story_title=story_title, story_summary=story_summary,
                              story_moral=story_moral)
                session.add(story)
                session.commit()
                user_folder = f"stories/{sanitize_filename(name)}"
                os.makedirs(user_folder, exist_ok=True)
                story_json = {
                    "name": name, "age": age, "location": location,
                    "story_title": story_title, "story_summary": story_summary,
                    "story_moral": story_moral, "timestamp": datetime.now().isoformat()
                }
                with open(f"{user_folder}/story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
                    json.dump(story_json, f, ensure_ascii=False, indent=2)
                st.success(TEXT[st.session_state.language]["success_msg"])

    elif sub_page == TEXT[st.session_state.language]["sub_actions"][1]:
        st.title(TEXT[st.session_state.language]["read_title"])
        df = pd.read_sql("SELECT * FROM stories ORDER BY timestamp DESC", engine)
        for _, row in df.iterrows():
            st.markdown(f"""
                <div style='background-color:#f9f9f9; color:black; padding:20px; border-radius:12px; margin-bottom:1rem;'>
                    <h4>{row['story_title']}</h4>
                    <p><b>{TEXT[st.session_state.language]['name']}:</b> {row['name']} ({row['age']} yrs, {row['location']})</p>
                    <p><b>{TEXT[st.session_state.language]['story_summary']}:</b> {row['story_summary']}</p>
                    <p><b>{TEXT[st.session_state.language]['story_moral']}:</b> <i>{row['story_moral']}</i></p>
                </div>
            """, unsafe_allow_html=True)

# ---------------------- Place Histories ---------------------- #
elif main_page == TEXT[st.session_state.language]["sections"][2]:
    if sub_page == TEXT[st.session_state.language]["sub_actions"][0]:
        st.title(TEXT[st.session_state.language]["place_submit_btn"])
        name = st.text_input(TEXT[st.session_state.language]["name"])
        age = st.text_input(TEXT[st.session_state.language]["age"])
        location = st.text_input(TEXT[st.session_state.language]["location"])
        place_name = st.text_input(TEXT[st.session_state.language]["place_title"])
        place_description = st.text_area(TEXT[st.session_state.language]["place_desc"])
        historical_significance = st.text_area(TEXT[st.session_state.language]["place_significance"])
        uploaded_image = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])
        if st.button(TEXT[st.session_state.language]["place_submit_btn"]):
            if not name or not age or not location or not place_name or not place_description:
                st.error(TEXT[st.session_state.language]["error_msg"])
            else:
                new_place = PlaceHistory(
                    name=name, age=age, location=location,
                    place_name=place_name, place_description=place_description,
                    historical_significance=historical_significance
                )
                session.add(new_place)
                session.commit()
                folder = f"place_histories/{sanitize_filename(name)}"
                os.makedirs(folder, exist_ok=True)
                if uploaded_image:
                    with open(f"{folder}/{sanitize_filename(place_name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", "wb") as f:
                        f.write(uploaded_image.read())
                st.success(TEXT[st.session_state.language]["success_msg"])

    elif sub_page == TEXT[st.session_state.language]["sub_actions"][1]:
        st.title(TEXT[st.session_state.language]["place_read_title"])
        df_places = pd.read_sql("SELECT * FROM place_histories ORDER BY timestamp DESC", engine)
        for _, row in df_places.iterrows():
            st.markdown(f"""
                <div style='background-color:#f9f9f9; color:black; padding:20px; border-radius:12px; margin-bottom:1rem;'>
                    <h4>{row['place_name']}</h4>
                    <p><b>{TEXT[st.session_state.language]['name']}:</b> {row['name']} ({row['age']} yrs, {row['location']})</p>
                    <p><b>{TEXT[st.session_state.language]['place_desc']}:</b> {row['place_description']}</p>
                    <p><b>{TEXT[st.session_state.language]['place_significance']}:</b> <i>{row['historical_significance']}</i></p>
                </div>
            """, unsafe_allow_html=True)
            image_pattern = f"place_histories/{sanitize_filename(row['name'])}/{sanitize_filename(row['place_name'])}_*.jpg"
            images = glob.glob(image_pattern)
            if images:
                st.image(images[0], caption=row['place_name'], use_container_width=True)


