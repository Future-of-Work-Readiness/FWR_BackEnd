"""
Quiz Generation using Google Gemini AI (using subprocess + curl)
This version uses curl directly to avoid Python SDK/requests issues
"""
import subprocess
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_quiz_question(
    specialization: str,
    topic: str,
    difficulty: int = 3,
    num_options: int = 4
):
    """
    Generate a single quiz question using Gemini AI via curl
    
    Args:
        specialization: e.g., "Frontend Development", "Data Science"
        topic: e.g., "React Hooks", "Machine Learning Algorithms"
        difficulty: 1-5 (1=Beginner, 5=Expert)
        num_options: Number of answer options (default 4)
    
    Returns:
        dict with question, options, correct_answer, explanation
    """
    
    # Map difficulty to description
    difficulty_map = {
        1: "Beginner - Basic concepts and definitions",
        2: "Intermediate - Practical application of concepts",
        3: "Advanced - Complex scenarios and best practices",
        4: "Expert - Architectural decisions and trade-offs",
        5: "Master - Cutting-edge techniques and deep expertise"
    }
    
    difficulty_desc = difficulty_map.get(difficulty, "Intermediate")
    
    # System instruction
    system_instruction = f"""You are an expert curriculum designer and assessment specialist in {specialization}.

Your task is to generate ONE high-quality multiple-choice question that:
1. Tests {difficulty_desc}
2. Has {num_options} answer options (A, B, C, D, etc.)
3. Has EXACTLY ONE correct answer
4. All options must be plausible and similar in length
5. Avoid obvious answers or "all of the above" / "none of the above"
6. Include a brief explanation of why the answer is correct

Return ONLY valid JSON in this exact format:
{{
    "question": "The question text here",
    "options": [
        {{"id": "A", "text": "First option"}},
        {{"id": "B", "text": "Second option"}},
        {{"id": "C", "text": "Third option"}},
        {{"id": "D", "text": "Fourth option"}}
    ],
    "correct_answer": "A",
    "explanation": "Why option A is correct and others are not"
}}"""

    # User prompt - combine system instruction into the main prompt
    full_prompt = f"""{system_instruction}

Generate a {difficulty_desc} level multiple-choice question about '{topic}' in the context of {specialization}.

The question should:
- Be practical and relevant to real-world scenarios
- Test understanding, not just memorization
- Have {num_options} plausible options
- Be appropriate for someone learning {specialization}

Topic focus: {topic}

Return the question in JSON format as specified."""

    try:
        # Prepare the payload (WITHOUT systemInstruction - it seems to cause hangs)
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
            }
        }
        
        payload_json = json.dumps(payload)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        # Use curl
        curl_command = [
            'curl', '-s', '-X', 'POST',
            url,
            '-H', 'Content-Type: application/json',
            '-d', payload_json,
            '--max-time', '30'
        ]
        
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=35)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"curl command failed: {result.stderr}"
            }
        
        # Parse response
        response_data = json.loads(result.stdout)
        
        # Debug: print raw response
        print(f"\n[DEBUG] API Response: {json.dumps(response_data, indent=2)}\n")
        
        # Check for API errors
        if 'error' in response_data:
            return {
                "success": False,
                "error": f"API Error: {response_data['error'].get('message', 'Unknown error')}"
            }
        
        # Extract text with better error handling
        try:
            text = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        except (KeyError, IndexError, TypeError) as e:
            return {
                "success": False,
                "error": f"Failed to extract text from response: {str(e)}",
                "raw_response": json.dumps(response_data)[:500]
            }
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Parse JSON
        question_data = json.loads(text)
        
        # Validate structure
        required_keys = ["question", "options", "correct_answer", "explanation"]
        if not all(key in question_data for key in required_keys):
            raise ValueError("Generated question missing required fields")
        
        return {
            "success": True,
            "data": question_data
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "API request timed out"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse response as JSON: {str(e)}",
            "raw_response": result.stdout if 'result' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_full_quiz(
    specialization: str,
    topics: list,
    questions_per_topic: int = 2,
    difficulty: int = 3
):
    """
    Generate a complete quiz with multiple questions
    
    Args:
        specialization: e.g., "Frontend Development"
        topics: List of topics, e.g., ["React Hooks", "State Management"]
        questions_per_topic: How many questions per topic
        difficulty: 1-5
    
    Returns:
        List of generated questions
    """
    all_questions = []
    
    for topic in topics:
        print(f"\n📝 Generating {questions_per_topic} questions for: {topic}")
        
        for i in range(questions_per_topic):
            print(f"   Question {i+1}/{questions_per_topic}...", end=" ", flush=True)
            
            result = generate_quiz_question(
                specialization=specialization,
                topic=topic,
                difficulty=difficulty
            )
            
            if result["success"]:
                all_questions.append({
                    "topic": topic,
                    "difficulty": difficulty,
                    **result["data"]
                })
                print("✅")
            else:
                print(f"❌ {result['error']}")
    
    return all_questions


# Example usage
if __name__ == "__main__":
    # Generate a single question
    print("=" * 60)
    print("GENERATING SINGLE QUESTION")
    print("=" * 60)
    
    result = generate_quiz_question(
        specialization="Frontend Development",
        topic="React Hooks and useEffect",
        difficulty=3
    )
    
    if result["success"]:
        print("\n✅ Generated Question:\n")
        print(json.dumps(result["data"], indent=2))
    else:
        print(f"\n❌ Error: {result['error']}")
    
    # Generate multiple questions
    print("\n" + "=" * 60)
    print("GENERATING FULL QUIZ")
    print("=" * 60)
    
    quiz = generate_full_quiz(
        specialization="Frontend Development",
        topics=[
            "React Hooks",
            "State Management",
            "Component Lifecycle"
        ],
        questions_per_topic=2,
        difficulty=3
    )
    
    print(f"\n✅ Generated {len(quiz)} questions total!")
    if len(quiz) > 0:
        print("\nFirst question:")
        print(json.dumps(quiz[0], indent=2))
