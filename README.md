Vision Craft: The AI Co-Pilot for Artisans
==========================================

### A Hackathon Submission for "AI-Powered Marketplace Assistant for Local Artisans"

**Repo Link:** [https://github.com/VaradRane12/Genai-hack](https://github.com/VaradRane12/Genai-hack)

Vision Craft is a comprehensive, AI-powered web application designed to empower local Indian artisans by bridging the gap between traditional craftsmanship and the modern digital marketplace. This tool acts as a personal marketing assistant, helping artisans tell their stories, create professional branding, and develop strategic marketing campaigns with ease, regardless of their digital literacy or language.

The Challenge
-------------

Indian artisans, rich in cultural heritage, often face significant barriers in the digital world. A lack of marketing skills, limited resources, and the difficulty of translating traditional art forms for contemporary audiences severely restrict their reach and profitability. Vision Craft directly addresses this by providing an intuitive suite of AI tools that are accessible, powerful, and culturally aware.

Core Features
-------------

This application is more than just a text generator; it's a multi-faceted co-pilot that assists artisans at every step of their journey to get online.

*   **Visual Product Analyzer (Multimodal AI):** Artisans can upload a photo of their craft, and the AI uses vision capabilities to generate a rich, detailed, and professional product description. This solves the "blank page" problem instantly.
    
*   **Branding & Storytelling Kit:** Generates culturally resonant business names, compelling "About the Artisan" stories, and catchy brand taglines based on a simple description of the craft.
    
*   **Social Media Campaign Generator:** Creates a full 7-day social media content plan, complete with daily themes, post ideas, captions, and relevant hashtags, turning a single product into a week's worth of marketing.
    
*   **Hyper-Local Market Trend Advisor:** This context-aware tool provides timely and localized marketing advice. For the demo, it is set to Pimpri-Chinchwad, September 2025, and provides specific strategies related to major local festivals like Ganesh Chaturthi and Diwali.
    
*   **Pan-India Multilingual Support:** The entire platform is multilingual. An artisan can provide input in one of 12 major Indian languages (e.g., Marathi, Bengali, Tamil) and receive professionally crafted marketing content in another (e.g., English), breaking down language barriers to global markets.
    

Technology Stack
----------------

The prototype is built with a focus on rapid development and leveraging powerful, cutting-edge AI.

*   **Programming Language:** Python
    
*   **Web Framework:** Streamlit
    
*   **Core AI Model:** Google Gemini API (gemini-2.5-flash-preview-05-20) for its powerful multimodal (text + image) and multilingual capabilities.
    
*   **Python Libraries:**
    
    *   requests for making API calls
        
    *   Pillow for image processing
        
    *   python-dotenv for managing environment variables
        

Local Setup & Installation
--------------------------

To run this project on your local machine, follow these steps:

1.  Bashgit clone https://github.com/VaradRane12/Genai-hack.gitcd Genai-hack
    
2.  Make sure you have Python 3.8+ installed. Then, install the required libraries from the requirements.txt file.Bashpip install -r requirements.txt
    
3.  Create a file named .env in the root of the project folder. Add your Google Gemini API key to this file:GEMINI\_API\_KEY="AIzaSy...your-actual-api-key..."
    
4.  Execute the following command in your terminal:Bashstreamlit run app.pyYour web browser will automatically open with the application running.
    

Deployment on Render
--------------------

This application is designed for easy deployment on a platform like Render for a stable, always-on demo.

1.  **Push to GitHub:** Ensure your project (including app.py and requirements.txt) is in your GitHub repository.
    
2.  **Create a Web Service on Render:** Connect your GitHub account to Render and create a new "Web Service", selecting your repository.
    
3.  **Configure Settings:**
    
    *   **Runtime:** Python 3
        
    *   **Build Command:** pip install -r requirements.txt
        
    *   **Start Command:** streamlit run app.py
        
4.  **Add Environment Variable:** In the "Environment" section, add a secret key:
    
    *   **Key:** GEMINI\_API\_KEY
        
    *   **Value:** AIzaSy...your-actual-api-key... (Paste your key here)
        
5.  **Deploy:** Click "Create Web Service". Render will build and deploy your application, providing a public URL.
    

Project Diagrams
----------------

The application includes a built-in section with diagrams that explain its architecture and user flow.

Use Case Diagram
