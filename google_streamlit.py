import streamlit as st
import requests
import time
import base64
from PIL import Image
import io
import dotenv
import os
# --- Page Configuration ---
st.set_page_config(
    page_title="AI Artisan Co-Pilot (Hackathon Edition)",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Gemini API Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY", "")
# We need to use a model that supports image and text input for the visual analyzer
VISION_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
TEXT_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"


# --- Session State Initialization ---
if 'craft_description' not in st.session_state:
    st.session_state.craft_description = ""
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}

# --- API Call Helper Functions ---
def call_gemini_api(system_prompt, user_input, image_base64=None):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is not set. Please add it to your Streamlit secrets."

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

# --- UI Rendering Functions for Each Tool ---

def show_visual_analyzer():
    st.header("📸 Visual Product Analyzer")
    st.markdown("Got a photo? Let AI describe your product's colors, patterns, and style to kickstart your marketing descriptions.")

    uploaded_file = st.file_uploader("Upload a photo of your craft", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Your Uploaded Craft", use_column_width=True)
        
        if st.button("Analyze My Product Image", type="primary", use_container_width=True):
            with st.spinner("AI is looking at your product..."):
                # Convert image to base64
                image = Image.open(uploaded_file)
                
                # Resize image if it's too large to reduce payload size
                max_size = (1024, 1024)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                prompt = "You are an expert art curator. Analyze this image of a handcrafted product. Provide a rich, detailed description covering: \n1. **Visual Description:** Describe the object, its colors, patterns, and textures. \n2. **Style & Mood:** What is the artistic style (e.g., traditional, modern, rustic)? What mood does it evoke? \n3. **Potential Materials:** Based on the visual evidence, what materials might it be made of? \n4. **Keywords:** List 10 descriptive keywords for this item."
                analysis = call_gemini_api(prompt, "Please analyze the attached image.", image_base64=image_base64)
                
                st.session_state.generated_content['visual_analysis'] = analysis
                # Also, save this analysis to the craft description to use in other tools
                st.session_state.craft_description = analysis

    if 'visual_analysis' in st.session_state.generated_content:
        st.divider()
        st.subheader("AI Visual Analysis")
        st.info(st.session_state.generated_content['visual_analysis'])
        st.success("This description has been saved and can now be used by the other tools!")

def show_social_media_tool():
    st.header("Social Media Campaign Generator")
    st.markdown("Don't just post once. Get a full week's content plan to engage your audience and tell your story.")
    
    if not st.session_state.craft_description:
        st.warning("Please describe your craft first using the 'Branding Kit' or 'Visual Analyzer'.")
        return

    st.markdown("#### Using this craft description:")
    st.info(st.session_state.craft_description)

    if st.button("Generate 7-Day Social Media Plan", type="primary", use_container_width=True):
        prompt = "You are a social media marketing expert for small businesses. Create a 7-day social media content plan for an artisan based on their craft description. The goal is to maximize engagement and tell a story. For each day, provide: \n- **Theme:** (e.g., 'Behind the Scenes', 'Meet the Maker'). \n- **Post Idea:** A concrete idea for a photo or video. \n- **Caption:** An engaging caption with a question to encourage comments. \n- **Hashtags:** 3-5 relevant hashtags. \nFormat the entire output in Markdown with clear headings for each day."
        with st.spinner("Planning your campaign..."):
            st.session_state.generated_content['social_plan'] = call_gemini_api(prompt, st.session_state.craft_description)

    if 'social_plan' in st.session_state.generated_content:
        st.divider()
        st.subheader("Your 7-Day Social Media Campaign")
        st.markdown(st.session_state.generated_content['social_plan'])

def show_market_trend_tool():
    st.header("Market Trend & Festival Advisor")
    st.markdown("Get timely marketing advice tailored to your location and upcoming cultural events.")

    if not st.session_state.craft_description:
        st.warning("Please describe your craft first using the 'Branding Kit' or 'Visual Analyzer'.")
        return

    st.markdown("#### Using this craft description:")
    st.info(st.session_state.craft_description)

    if st.button("Advise Me on Market Trends", type="primary", use_container_width=True):
        # This is where the contextual prompt engineering happens
        prompt = f"""
You are a hyperlocal business consultant for Indian artisans. Your current location is Pimpri-Chinchwad, Maharashtra, India, and the current date is September 21, 2025.

Be aware of the following context:
- **Ganesh Chaturthi:** This major festival is very important in Maharashtra and is happening right now or has just concluded.
- **Navratri & Diwali:** These major gift-giving festivals are coming up in the next 1-2 months.
- **Online Sales:** Major e-commerce platforms like Amazon and Flipkart will have their 'Great Indian Festival' and 'Big Billion Days' sales soon.

Based on the artisan's craft description, provide a report with three sections in Markdown:
1.  **Immediate Festival Opportunity (Ganesh Chaturthi):** Suggest 2-3 specific marketing angles or product ideas that connect the craft to the Ganesh Chaturthi theme.
2.  **Upcoming Holiday Strategy (Navratri/Diwali):** How can they prepare their products and marketing for the upcoming peak season? Suggest ideas for bundles, special editions, or corporate gifting.
3.  **E-commerce Sales Strategy:** Provide 3 actionable tips on how to leverage the big online sales events, even as a small seller.
"""
        with st.spinner("Analyzing local trends..."):
            st.session_state.generated_content['market_advice'] = call_gemini_api(prompt, st.session_state.craft_description)

    if 'market_advice' in st.session_state.generated_content:
        st.divider()
        st.subheader("Your Localized Marketing Advisory")
        st.markdown(st.session_state.generated_content['market_advice'])

def show_branding_tool():
    st.header("📝 Branding & Storytelling Kit")
    st.markdown("Generate names, stories, and taglines to build a strong brand identity.")
    st.session_state.craft_description = st.text_area(
        "Start by describing your craft, or use the 'Visual Analyzer' to generate a description from a photo.",
        value=st.session_state.craft_description, height=175, key="branding_desc"
    )
    # ... (Rest of the branding tool code is the same as before) ...
    if not st.session_state.craft_description:
        st.info("Please describe your craft above to enable the generators.")
        return

    st.subheader("Generate Your Content")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate Business Names", use_container_width=True, type="primary"):
            prompt = "You are a branding expert for Indian artisans. Generate 5 creative, culturally-rich business names based on the user's craft description. Provide a brief one-line explanation for each. Format as a numbered list."
            with st.spinner("Crafting names..."):
                st.session_state.generated_content['names'] = call_gemini_api(prompt, st.session_state.craft_description)
    with col2:
        if st.button("Write My Artisan Story", use_container_width=True, type="primary"):
            prompt = "You are a master storyteller for artisans. Write a compelling 'About the Artisan' story (150 words) in a warm, first-person narrative based on the user's description. Connect the craft to their heritage and passion."
            with st.spinner("Writing your story..."):
                st.session_state.generated_content['story'] = call_gemini_api(prompt, st.session_state.craft_description)
    with col3:
        if st.button("Create Brand Taglines", use_container_width=True, type="primary"):
            prompt = "You are a marketing expert for artisans. Generate 5 short, catchy taglines that capture the essence of the user's craft. Format as a numbered list."
            with st.spinner("Creating taglines..."):
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
st.sidebar.title("AI Artisan Co-Pilot")
st.sidebar.markdown("**Hackathon Edition**")
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
st.sidebar.info("This prototype leverages multimodal and context-aware generative AI to provide strategic, actionable insights for artisans.")

# --- Page Routing ---
if tool_selection == "Visual Product Analyzer":
    show_visual_analyzer()
elif tool_selection == "Social Media Campaign Generator":
    show_social_media_tool()
elif tool_selection == "Market Trend & Festival Advisor":
    show_market_trend_tool()
elif tool_selection == "Branding & Storytelling Kit":
    show_branding_tool()

