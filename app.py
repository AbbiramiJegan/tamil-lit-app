import re
import pandas as pd
from gtts import gTTS
import streamlit as st
from datasets import load_dataset

# Load datasets with caching
@st.cache_data
def load_aathichoodi():
    dataset = load_dataset("Selvakumarduraipandian/Aathichoodi")
    return pd.DataFrame(dataset["train"])

@st.cache_data
def load_thirukural():
    dataset = load_dataset("Selvakumarduraipandian/Thirukural")
    return pd.DataFrame(dataset["train"])

# Sidebar Navigation
page = st.sidebar.radio("📚 Choose", ["ஆத்திசூடி (Aathichoodi)", "திருக்குறள் (Thirukural)"])

# Load selected dataset
if page == "ஆத்திசூடி (Aathichoodi)":
    df = load_aathichoodi()
    st.markdown("<h1 class='title'>📜 Aathichoodi Explorer</h1>", unsafe_allow_html=True)
    search_col = ["தமிழ் வாக்கியம்", "English Translation", "Transliteration"]
else:
    df = load_thirukural()
    st.markdown("<h1 class='title'>📖 Thirukural Explorer</h1>", unsafe_allow_html=True)
    search_col = ["Kural", "Couplet", "Transliteration"]

# Search bar
search_query = st.text_input("🔍 Search (Tamil, English, or Transliteration):", "")

# Function to check if search query exists
def matches_search(row, query):
    return any(str(row[col]).lower().find(query.lower()) != -1 for col in search_col if pd.notna(row[col]))

# Show Random Verse button
if st.button("✨ Show Random Verse"):
    st.session_state["random_verse"] = df.sample(1).to_dict(orient="records")[0]
    st.session_state["selected_page"] = page  # Store the selected page
    st.rerun()

# Filtering logic (Fixing random verse issue)
if search_query:
    filtered_df = df[df.apply(lambda row: matches_search(row, search_query), axis=1)]
elif "random_verse" in st.session_state and "selected_page" in st.session_state and st.session_state["selected_page"] == page:
    # Show the stored random verse only if it's for the correct page
    filtered_df = pd.DataFrame([st.session_state["random_verse"]])
else:
    filtered_df = df.head(1)  # Default to first verse



# Function to clean text (removes <br /> and other HTML tags)
def clean_text(text):
    return re.sub(r"<.*?>", "", text)  # Removes any HTML tags

# Function to generate Tamil speech
def generate_tamil_audio(text):
    cleaned_text = clean_text(text)  # Remove <br /> before passing to gTTS
    tts = gTTS(cleaned_text, lang="ta")  # Generate Tamil speech
    audio_path = "tamil_audio.mp3"
    tts.save(audio_path)
    return audio_path


# Display results
if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        tamil_verse = row.get("தமிழ் வாக்கியம்", row.get("Kural", "N/A"))
        meaning = row.get("Tamil Meaning", row.get("Vilakam", "N/A"))
        translation = row.get("English Translation", row.get("Couplet", "N/A"))
        transliteration = row.get("Transliteration", "N/A")

        st.markdown(f"""
        <div class='result-card'>
            <p class='result-title'>{tamil_verse}</p>
            <p class='result-text'><b>📖 Meaning:</b> {meaning}</p>
            <p class='result-text'><b>📝 Translation:</b> {translation}</p>
            <p class='result-text'><b>🔤 Transliteration:</b> {transliteration}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔊 Hear Pronunciation", key=f"play_{tamil_verse}"):
            audio_file = generate_tamil_audio(tamil_verse)
            st.audio(audio_file, format="audio/mp3")

        st.write("---")
else:
    st.warning("No results found. Try another search term!")
