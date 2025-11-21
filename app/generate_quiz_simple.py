"""
ULTRA SIMPLE Quiz Generator - uses os.system instead of subprocess
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_quiz_question(topic="React Hooks", difficulty="Beginner"):
    """Generate one quiz question"""
    
    prompt = f"""Generate ONE multiple-choice quiz question about {topic} for a {difficulty} level developer.

Return ONLY valid JSON (no markdown, no code blocks) in this format:
{{
    "question": "question text",
    "options": [
        {{"id": "A", "text": "first option"}},
        {{"id": "B", "text": "second option"}},
        {{"id": "C", "text": "third option"}},
        {{"id": "D", "text": "fourth option"}}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct"
}}"""
    
    # Escape prompt for shell
    prompt_escaped = prompt.replace('"', '\\"').replace('\n', ' ')
    
    # Create temp file for output
    output_file = "/tmp/gemini_response.json"
    
    # Build curl command
    cmd = f'''curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}" -H "Content-Type: application/json" -d '{{"contents":[{{"parts":[{{"text":"{prompt_escaped}"}}]}}],"generationConfig":{{"temperature":0.3,"maxOutputTokens":1024}}}}' > {output_file}'''
    
    # Execute
    return_code = os.system(cmd)
    
    if return_code != 0:
        return {"success": False, "error": f"Command failed with code {return_code}"}
    
    try:
        # Read response
        with open(output_file, 'r') as f:
            api_response = json.load(f)
        
        if 'error' in api_response:
            return {"success": False, "error": api_response['error'].get('message', 'API error')}
        
        # Extract text
        text = api_response['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Clean markdown
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Parse question
        question_data = json.loads(text)
        
        return {"success": True, "data": question_data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("Testing ULTRA SIMPLE quiz generator...\n")
    
    result = generate_quiz_question("React Hooks", "Beginner")
    
    if result["success"]:
        print("✅ SUCCESS!\n")
        print(json.dumps(result["data"], indent=2))
    else:
        print(f"❌ ERROR: {result['error']}")
