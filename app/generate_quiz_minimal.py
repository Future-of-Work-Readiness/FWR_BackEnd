#!/usr/bin/env python3
"""
MINIMAL working quiz generator using curl
"""
import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_quiz_question(topic):
    """Generate one quiz question about the given topic"""
    
    # Simple prompt
    prompt = f"""Generate ONE multiple-choice quiz question about {topic} for a beginner developer.

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
    "question": "the question text",
    "options": [
        {{"id": "A", "text": "option 1"}},
        {{"id": "B", "text": "option 2"}},
        {{"id": "C", "text": "option 3"}},
        {{"id": "D", "text": "option 4"}}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct"
}}"""

    # API payload
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024}
    }
    
    # Call API using curl
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    
    try:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', url, 
             '-H', 'Content-Type: application/json',
             '-d', json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"curl failed: {result.stderr}"}
        
        # Parse API response
        api_response = json.loads(result.stdout)
        
        if 'error' in api_response:
            return {"success": False, "error": api_response['error'].get('message', 'API error')}
        
        # Extract generated text
        text = api_response['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Clean markdown if present
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Parse the question JSON
        question_data = json.loads(text)
        
        return {"success": True, "data": question_data}
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Test it
if __name__ == "__main__":
    print("Testing minimal quiz generator...\n")
    
    result = generate_quiz_question("React Hooks")
    
    if result["success"]:
        print("✅ SUCCESS!\n")
        print(json.dumps(result["data"], indent=2))
    else:
        print(f"❌ ERROR: {result['error']}")
