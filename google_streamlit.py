import streamlit as st
import requests
import time
import base64
from PIL import Image
import io
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This line loads the .env file for local development
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Artisan Co-Pilot (Multilingual)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Gemini API Configuration ---
# On Render, this will get the key from Environment Variables.
# Locally, it will get the key from the loaded .env file.
API_KEY = os.getenv("GEMINI_API_KEY")

# --- CRUCIAL: API Key Check ---
if not API_KEY:
    st.error("Your GEMINI_API_KEY is not set. Please add it to your .env file locally or as an environment variable on your deployment platform.")
    st.stop() # Stop the app from running further.

VISION_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
TEXT_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"


# --- Session State Initialization ---
if 'craft_description' not in st.session_state:
    st.session_state.craft_description = ""
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}
if 'input_lang' not in st.session_state:
    st.session_state.input_lang = "English"
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = "English"

# --- API Call Helper Functions ---
def call_gemini_api(system_prompt, user_input, image_base64=None):
    # The API_KEY is now checked at the start, so we don't need to check it here again.
    api_url = VISION_API_URL if image_base64 else TEXT_API_URL
    
    parts = [{"text": user_input}]
    if image_base64:
        parts.insert(0, {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}})

    payload = {
        "contents": [{"parts": parts}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }
    headers = {'Content-Type': 'application/json'}
    
    retries = 3
    delay = 1
    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                candidate = result.get('candidates', [{}])[0]
                return candidate.get('content', {}).get('parts', [{}])[0].get('text', "Error: Could not parse API response.")
            elif response.status_code in [429, 500, 503]:
                st.warning(f"API call failed with status {response.status_code}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return f"Error: API responded with status {response.status_code}"
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                st.warning(f"Request failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                return f"Error: A network error occurred: {e}"
    return "Error: The request failed after multiple retries."

# --- The rest of your UI functions (show_visual_analyzer, etc.) remain unchanged ---
# [The rest of the code is identical to your provided version]
def show_visual_analyzer():
    st.header("Visual Product Analyzer")
    st.markdown("Upload a photo and let AI describe your product. The analysis will be in your chosen output language.")

    uploaded_file = st.file_uploader("Upload a photo of your craft", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Your Uploaded Craft", use_container_width =True)
        
        if st.button("Analyze My Product Image", type="primary", use_container_width=True):
            with st.spinner(f"AI is analyzing your product and preparing a description in {st.session_state.output_lang}..."):
                image = Image.open(uploaded_file)
                max_size = (1024, 1024)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                language_instruction = f"Your final analysis and description must be written entirely in {st.session_state.output_lang}."
                prompt = f"You are an expert art curator. Analyze this image of a handcrafted product. Provide a rich, detailed description covering: Visual Description (colors, patterns, textures), Style & Mood, Potential Materials, and 10 descriptive Keywords. {language_instruction}"
                
                analysis = call_gemini_api(prompt, "Please analyze the attached image.", image_base64=image_base64)
                st.session_state.generated_content['visual_analysis'] = analysis
                st.session_state.craft_description = analysis

    if 'visual_analysis' in st.session_state.generated_content:
        st.divider()
        st.subheader("AI Visual Analysis")
        st.info(st.session_state.generated_content['visual_analysis'])
        st.success("This description has been saved and can now be used by the other tools!")

def show_social_media_tool():
    st.header("Social Media Campaign Generator")
    st.markdown("Get a full week's content plan in your chosen output language.")
    
    if not st.session_state.craft_description:
        st.warning("Please describe your craft first using the 'Branding Kit' or 'Visual Analyzer'.")
        return

    st.markdown(f"#### Generating campaign based on this description (assumed to be in {st.session_state.input_lang}):")
    st.info(st.session_state.craft_description)

    if st.button("Generate 7-Day Social Media Plan", type="primary", use_container_width=True):
        language_instruction = f"The user has provided their description in {st.session_state.input_lang}. Your final output, including all themes, captions, and hashtags, must be in {st.session_state.output_lang}."
        prompt = f"You are a social media marketing expert. Create a 7-day content plan for an artisan based on their craft description. For each day, provide a Theme, Post Idea, Caption, and 3-5 Hashtags. {language_instruction}"
        with st.spinner(f"Planning your campaign in {st.session_state.output_lang}..."):
            st.session_state.generated_content['social_plan'] = call_gemini_api(prompt, st.session_state.craft_description)

    if 'social_plan' in st.session_state.generated_content:
        st.divider()
        st.subheader("Your 7-Day Social Media Campaign")
        st.markdown(st.session_state.generated_content['social_plan'])

def show_market_trend_tool():
    st.header("Market Trend & Festival Advisor")
    st.markdown("Get timely marketing advice, localized for Pimpri-Chinchwad, in your chosen output language.")

    if not st.session_state.craft_description:
        st.warning("Please describe your craft first using the 'Branding Kit' or 'Visual Analyzer'.")
        return

    st.markdown(f"#### Analyzing trends for this description (assumed to be in {st.session_state.input_lang}):")
    st.info(st.session_state.craft_description)

    if st.button("Advise Me on Market Trends", type="primary", use_container_width=True):
        language_instruction = f"The user's description is in {st.session_state.input_lang}. Your entire report and all recommendations must be written in {st.session_state.output_lang}."
        prompt = f"You are a hyperlocal business consultant in Pimpri-Chinchwad, Maharashtra, India. The date is September 21, 2025. Be aware of Ganesh Chaturthi (current), and upcoming Navratri/Diwali. Based on the artisan's craft, provide a report with three sections: 1. Immediate Festival Opportunity (Ganesh Chaturthi). 2. Upcoming Holiday Strategy (Navratri/Diwali). 3. E-commerce Sales Strategy. {language_instruction}"
        
        with st.spinner(f"Analyzing local trends and preparing advice in {st.session_state.output_lang}..."):
            st.session_state.generated_content['market_advice'] = call_gemini_api(prompt, st.session_state.craft_description)

    if 'market_advice' in st.session_state.generated_content:
        st.divider()
        st.subheader("Your Localized Marketing Advisory")
        st.markdown(st.session_state.generated_content['market_advice'])

def show_branding_tool():
    st.header("Branding & Storytelling Kit")
    st.markdown(f"Describe your craft in **{st.session_state.input_lang}**. The generated content will be in **{st.session_state.output_lang}**.")
    
    st.session_state.craft_description = st.text_area(
        f"Describe your craft here, or use the 'Visual Analyzer' to generate a description.",
        value=st.session_state.craft_description, height=175, key="branding_desc"
    )
    if not st.session_state.craft_description:
        st.info("Please describe your craft above to enable the generators.")
        return

    st.subheader("Generate Your Content")
    language_instruction = f"The user has written their description in {st.session_state.input_lang}. Your final output must be in {st.session_state.output_lang}."
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate Business Names", use_container_width=True, type="primary"):
            prompt = f"You are a branding expert for Indian artisans. Generate 5 creative, culturally-rich business names based on the user's craft description. Provide a brief one-line explanation for each. {language_instruction}"
            with st.spinner(f"Crafting names in {st.session_state.output_lang}..."):
                st.session_state.generated_content['names'] = call_gemini_api(prompt, st.session_state.craft_description)
    with col2:
        if st.button("Write My Artisan Story", use_container_width=True, type="primary"):
            prompt = f"You are a master storyteller. Write a compelling 'About the Artisan' story (150 words) based on the user's description. {language_instruction}"
            with st.spinner(f"Writing your story in {st.session_state.output_lang}..."):
                st.session_state.generated_content['story'] = call_gemini_api(prompt, st.session_state.craft_description)
    with col3:
        if st.button("Create Brand Taglines", use_container_width=True, type="primary"):
            prompt = f"You are a marketing expert. Generate 5 short, catchy taglines that capture the essence of the user's craft. {language_instruction}"
            with st.spinner(f"Creating taglines in {st.session_state.output_lang}..."):
                st.session_state.generated_content['taglines'] = call_gemini_api(prompt, st.session_state.craft_description)

    if 'names' in st.session_state.generated_content or 'story' in st.session_state.generated_content or 'taglines' in st.session_state.generated_content:
        st.divider()
        st.subheader("Your Generated Assets")
        if 'names' in st.session_state.generated_content:
            st.markdown("##### Business Name Ideas")
            st.info(st.session_state.generated_content['names'])
        if 'story' in st.session_state.generated_content:
            st.markdown("##### Your Artisan Story")
            st.info(st.session_state.generated_content['story'])
        if 'taglines' in st.session_state.generated_content:
            st.markdown("##### Brand Taglines")
            st.info(st.session_state.generated_content['taglines'])

# --- Main App Sidebar and Navigation ---
st.sidebar.title("Vision Craft")
st.sidebar.markdown("**Hackathon Submission**")
# --- UPDATED: Language Selection ---
st.sidebar.subheader("Language Settings")
language_options = (
    "English", "Hindi", "Marathi", "Bengali", "Tamil", "Telugu", 
    "Gujarati", "Kannada", "Malayalam", "Punjabi", "Odia", "Urdu"
)
st.session_state.input_lang = st.sidebar.selectbox(
    "Select your input language:",
    language_options
)
st.session_state.output_lang = st.sidebar.selectbox(
    "Select your output language:",
    language_options
)
st.sidebar.divider()
st.sidebar.markdown("A suite of AI tools to empower local artisans.")
tool_selection = st.sidebar.radio(
    "Choose your tool:",
    (
        "Visual Product Analyzer",
        "Social Media Campaign Generator",
        "Market Trend & Festival Advisor",
        "Branding & Storytelling Kit",
    )
)
st.sidebar.divider()

# --- Page Routing ---
if tool_selection == "Visual Product Analyzer":
    show_visual_analyzer()
elif tool_selection == "Social Media Campaign Generator":
    show_social_media_tool()
elif tool_selection == "Market Trend & Festival Advisor":
    show_market_trend_tool()
elif tool_selection == "Branding & Storytelling Kit":
    show_branding_tool()

