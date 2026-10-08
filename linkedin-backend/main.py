import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

# 🔓 ALLOW THE FRONTEND TO COMMUNICATE WITH THE BACKEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your GitHub Pages link to talk to this code securely
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛠️ CONFIGURE YOUR PERMANENT MASTER BRAND INSTRUCTIONS (System Prompt)
MASTER_SYSTEM_INSTRUCTIONS = (
    "You are an elite LinkedIn Ghostwriter and Executive Brand Strategist.\n\n"
    "CRITICAL LAYOUT & STRUCTURAL RULES:\n"
    "1. LINE SPACING: You must leave exactly ONE BLANK LINE between EVERY single sentence or short fragment. "
    "Never merge sentences into dense paragraphs. LinkedIn users scroll fast on mobile and need clean white space.\n"
    "2. THE HOOK: The first sentence must be a short, bold, magnetic statement (under 10 words). Do not use emojis in the hook.\n"
    "3. CORE VALUES: Break down the value from the user's uploaded file into 3-4 crisp bullet points. Use custom visual bullet indicators (like ‣ or ⚡) instead of generic dashes.\n"
    "4. ENGAGEMENT LOOP: End the post with an open-ended, thought-provoking question to encourage comments.\n"
    "5. SENIOR TAGGING HOOK: Add a specific line right before the hashtags that prompts peer interaction, formatted exactly like this: "
    "'(Tagging [Insert Senior Leader Name] & [Insert Peer Name] here—would love to get your perspective on this layout!)'\n"
    "6. HASHTAGS: Use exactly 3 highly relevant industry hashtags at the very bottom. No spam.\n\n"
    "TONE AND LANGUAGE DIRECTIVE:\n"
    "Maintain a highly professional, authoritative, yet approachable tone. Use active verbs. Avoid corporate fluff, robotic jargon (like 'delve', 'testament', 'revolutionize'), and unnecessary exclamation marks."
)

@app.post("/api/generate")
async def generate_linkedin_post(
    file: UploadFile = File(...),
    token: str = Form(...),
    tone: str = Form(...)
):
    # 🔒 SECURITY VERIFICATION CHECK
    # This reads the secret password you save in your hosting environment (e.g., Render)
    SECRET_PASSWORD = os.environ.get("MY_SECRET_PASSWORD", "SuperSecureFallbackPassword123!")
    
    if token != SECRET_PASSWORD:
        raise HTTPException(status_code=401, detail="Access Denied: Invalid Security Token Password.")

    try:
        # 🔑 INITIALIZE GEMINI AI WITH YOUR SECURE API KEY
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Configuration Error: Backend is missing the Gemini API Key.")
            
        genai.configure(api_key=GEMINI_API_KEY)

        # 🧠 CONFIGURING THE MODEL WITH THE SYSTEM BRAND GUIDELINES
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", # Natively supports text, pdfs, images, and videos
            system_instruction=MASTER_SYSTEM_INSTRUCTIONS
        )

        # 📂 READ THE INCOMING FILE DATA
        file_bytes = await file.read()
        
        # Prepare the file payload for the AI model
        file_payload = {
            "mime_type": file.content_type,
            "data": file_bytes
        }

        # ⚡ PROMPT SENT ALONG WITH THE FILE
        user_prompt = f"Analyze this uploaded material and translate it into a compelling LinkedIn post optimized for a '{tone}' style execution."

        # 🚀 CALL THE AI PIPELINE
        response = model.generate_content([file_payload, user_prompt])
        
        return {"linkedin_post": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine Processing Error: {str(e)}")

# This ensures it can run locally for your testing purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
