import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import speech_recognition as sr
import tempfile
import os
import base64
from translate import Translator
from gtts import gTTS
import time

# 🔹 Set Streamlit Page Config
st.set_page_config(page_title="AI Learning Companion", layout="wide", initial_sidebar_state="expanded")

# 🔹 Function to Set Background Image
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# 🔹 Set Background (Provide Your Image Path)
bg_image_path = "C:/Users/gudav/OneDrive/Desktop/aiml/img1.jpg"
set_background(bg_image_path)

# 🔹 Set up Google API Key
GOOGLE_API_KEY = "AIzaSyDDTwNlr8Piai1xLOLEQ_hgl6PM3MtVihA"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# 🔹 Load Gemini Model
model = genai.GenerativeModel("gemini-2.0-flash-001")

# 🔹 Custom CSS for Styling + Moving Footer (Left to Right)
st.markdown("""
    <style>
    /* 🔹 Change All Text Color to Red */
    html, body, .stApp {
        color: red !important;
    }

    /* 🔹 Specific Changes for Headings */
    h1, h2, h3, h4, h5, h6 {
        color: red !important;
        font-weight: bold;
        text-shadow: 2px 2px 5px rgba(255, 0, 0, 0.5);
    }

    /* 🔹 Buttons */
    .stButton>button {
        background-color: #ff0000; /* Red button */
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #cc0000;
        transform: scale(1.05);
    }

    /* 🔹 Moving Footer (Left to Right) */
    @keyframes moveFooter {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .footer-text {
        color: white !important;  
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        position: fixed;
        bottom: 0;
        left: 0;
        white-space: nowrap;
        overflow: hidden;
        animation: moveFooter 15s linear infinite alternate;
    }
            /* AI Response Box */
    .stAlert {
    background: rgba(0, 0, 0, 0.85); /* Dark Transparent Black */
    color: #00FF66 !important; /* Neon Green Text */
    font-size: 18px;
    font-weight: bold;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 15px rgba(0, 255, 102, 0.5); /* Neon Glow */
    border: 2px solid #00FF66; /* Green Neon Border */
    text-align: left;
    transition: all 0.3s ease-in-out;
}

.stAlert:hover {
    transform: scale(1.02); /* Slight hover effect */
    box-shadow: 0px 6px 20px rgba(0, 255, 102, 0.8); /* Stronger glow on hover */
}

/* AI Text Animation (Optional) */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.stAlert p {
    animation: fadeIn 0.6s ease-in-out;
}


    </style>
""", unsafe_allow_html=True)

# 🔹 Footer (Moves Left to Right)
st.markdown('<div class="footer-text">🚀 Powered by Gemini AI & gTTS | Developed by DHANESH GUDAVALLI 🧑‍🎓</div>', unsafe_allow_html=True)

# 🔹 Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/236/236832.png", width=80)
with col2:
    st.title("📚 AI-Powered Learning Companion")
    st.markdown("#### 🤖 Your Personal Tutor for Math, Physics & Chemistry")

# 🔹 Sidebar
with st.sidebar:
    st.header("🌍 Language Settings")
    language_options = {
        "English": "en",
        "Telugu": "te",
        "Hindi": "hi",
        "Spanish": "es",
        "French": "fr"
    }
    selected_language = st.selectbox("Choose Language", list(language_options.keys()))
    st.info(f"🔄 Responses in {selected_language}")

    st.header("🎮 Learning Progress")
    st.progress(75)
    st.write("🏆 75% to next badge!")
    
    st.header("✨ Features")
    st.markdown("""
    - 📸 Image Analysis
    - 🎤 Voice Input
    - 🗣️ Audio Response
    - 🌍 Multi-language
    - 📊 Interactive Learning
    """)

# 🔹 Image Upload
def capture_or_upload_image():
    uploaded_file = st.file_uploader("📸 Upload an image (e.g., problem screenshot)", 
                                    type=["jpg", "png", "jpeg"],
                                    help="Upload an image of your problem")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Uploaded Problem", width=400)
        return image
    return None

# 🔹 Speech-to-Text
def listen_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak your question!")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.warning("⚠️ Couldn't understand your speech")
            return ""
        except sr.RequestError:
            st.error("⚠️ Speech service unavailable")
            return ""
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            return ""

# 🔹 Text-to-Speech
def speak_text(text, lang):
    try:
        time.sleep(1)
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_file_path = temp_audio.name
            tts.save(temp_file_path)
        
        with open(temp_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
        
        os.remove(temp_file_path)
    except Exception as e:
        st.error(f"⚠️ Audio error: {str(e)}")

# 🔹 Convert Image to Bytes
def image_to_bytes(image):
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()

# 🔹 AI Response
def get_ai_response(query, image=None):
    try:
        if image:
            response = model.generate_content([
                {"mime_type": "image/jpeg", "data": image_to_bytes(image)},
                query if query else "Describe this image and solve any problem shown."
            ])
        else:
            response = model.generate_content([query])
        return response.text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# 🔹 Main Interface
st.markdown("---")
col_input, col_output = st.columns([1, 1])

with col_input:
    st.subheader("🎯 Ask Your Question")
    query = st.text_input("Type your question here", placeholder="ASK ANYTHING...", help="Enter your question manually")

    if st.button("🎤 Speak Question", help="Click to record your question"):
        with st.spinner("🎙️ Recording..."):
            spoken_query = listen_and_transcribe()
            if spoken_query:
                query = spoken_query
                st.success(f"🎙️ You said: {query}")
    
    image = capture_or_upload_image()

with col_output:
    st.subheader("📝 AI Explanation")
    if st.button("🔍 Get Explanation", help="Click to get your answer"):
        if query or image:
            with st.spinner("🤓 Processing your request..."):
                response_text = get_ai_response(query, image)
                translator = Translator(to_lang=language_options[selected_language])
                translated_text = translator.translate(response_text)
                st.success(translated_text)
                speak_text(translated_text, language_options[selected_language])
        else:
            st.warning("⚠️ Please provide a question or image!")