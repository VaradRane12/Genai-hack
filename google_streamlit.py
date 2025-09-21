import streamlit as st
import requests
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Artisan Toolkit",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Gemini API Configuration ---
# The API key is expected to be set in Streamlit's secrets management.
# For local development, you might set it as an environment variable.
# Canvas will inject the key automatically in production.
# API_KEY = st.secrets.get("GEMINI_API_KEY", "") 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=AIzaSyDTrwsy3tNYpUaXyml0tp5HDmAZ23kdRo8"


# --- Helper Functions ---

def get_prompt(content_type):
    """Returns the appropriate system prompt for a given content type."""
    base_prompt = "You are an expert branding and marketing assistant for local Indian artisans. Your goal is to help them build a strong online presence by creating authentic, culturally rich, and appealing content. The user will provide a description of their craft."
    
    prompts = {
        'name': f"{base_prompt}\n\nGenerate 5 creative and memorable business names based on the user's description. The names should be easy to pronounce and reflect the heritage of the craft. Provide a brief one-line explanation for each name suggestion. Format the output as a numbered list.",
        'story': f"{base_prompt}\n\nWrite a compelling \"About the Artisan\" story based on the user's description. The story should be around 150-200 words. Write in a warm, first-person narrative (from the artisan's perspective). It should connect the craft to their personal journey, family heritage, and passion. The tone should be authentic and heartfelt.",
        'tagline': f"{base_prompt}\n\nGenerate 5 short, catchy, and meaningful taglines for the artisan's brand based on their description. The taglines should capture the essence of their craft and its value. Format the output as a numbered list."
    }
    return prompts.get(content_type, base_prompt)

@st.cache_data(show_spinner=False)
def generate_content_from_api(_system_prompt, _user_input):
    """
    Calls the Gemini API to generate content with exponential backoff for retries.
    Using st.cache_data to avoid re-running the API call for the same input.
    The underscore prefix on arguments tells Streamlit to hash the values.
    """
    payload = {
        "contents": [{"parts": [{"text": _user_input}]}],
        "systemInstruction": {"parts": [{"text": _system_prompt}]},
    }
    headers = {'Content-Type': 'application/json'}
    
    retries = 3
    delay = 1  # start with 1 second
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                candidate = result.get('candidates', [{}])[0]
                if candidate and 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text']
                else:
                    return "Error: Could not extract content from the API response."
            
            elif response.status_code == 429 or response.status_code >= 500:
                # Retry on rate limit or server error
                st.warning(f"API call failed with status {response.status_code}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2 # Exponential backoff
            else:
                # Don't retry for other client-side errors
                return f"Error: API responded with status {response.status_code}\n{response.text}"
                
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                st.warning(f"Request failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                return f"Error: A network error occurred: {e}"

    return "Error: The request failed after multiple retries."


# --- UI Layout ---

# Header
st.markdown("<h1 style='text-align: center; color: #b45309;'>AI Artisan Toolkit 🎨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bring your craft to the world. Describe your art, and let AI help you build your online brand.</p>", unsafe_allow_html=True)

st.divider()

# Step 1: Input Description
st.subheader("1. Describe Your Craft & Story")
craft_description = st.text_area(
    "Describe your craft, its history, and your personal story.",
    height=150,
    placeholder="Example: I am a potter from Pune, Maharashtra. My family has been making traditional terracotta clay pots for three generations. I use natural river clay and hand-paint each piece with designs inspired by local folklore..."
)

# Step 2: Generate Content Buttons
st.subheader("2. Generate Marketing Content")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generate Business Names", use_container_width=True, type="primary"):
        if craft_description:
            with st.spinner("AI is crafting your business names..."):
                st.session_state.names = generate_content_from_api(get_prompt('name'), craft_description)
        else:
            st.warning("Please describe your craft first.")

with col2:
    if st.button("Write My Artisan Story", use_container_width=True, type="primary"):
        if craft_description:
            with st.spinner("AI is writing your artisan story..."):
                 st.session_state.story = generate_content_from_api(get_prompt('story'), craft_description)
        else:
            st.warning("Please describe your craft first.")

with col3:
    if st.button("Create a Tagline", use_container_width=True, type="primary"):
        if craft_description:
            with st.spinner("AI is creating your taglines..."):
                st.session_state.taglines = generate_content_from_api(get_prompt('tagline'), craft_description)
        else:
            st.warning("Please describe your craft first.")

st.divider()

# Step 3: Output Area
st.subheader("3. Your Generated Content")

if 'names' in st.session_state and st.session_state.names:
    st.markdown("#### Business Name Ideas")
    st.info(st.session_state.names)

if 'story' in st.session_state and st.session_state.story:
    st.markdown("#### Your Artisan Story")
    st.info(st.session_state.story)

if 'taglines' in st.session_state and st.session_state.taglines:
    st.markdown("#### Brand Taglines")
    st.info(st.session_state.taglines)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>Powered by Google's Generative AI</p>", unsafe_allow_html=True)
