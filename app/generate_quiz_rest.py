"""
Quiz Generation using Google Gemini AI (REST API version)
This version uses direct HTTP requests instead of the SDK to avoid timeout issues
"""
import requests
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
    Generate a single quiz question using Gemini AI via REST API
    
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

    # User prompt
    user_prompt = f"""Generate a {difficulty_desc} level multiple-choice question about '{topic}' in the context of {specialization}.

The question should:
- Be practical and relevant to real-world scenarios
- Test understanding, not just memorization
- Have {num_options} plausible options
- Be appropriate for someone learning {specialization}

Topic focus: {topic}

Return the question in JSON format as specified."""

    try:
        # Call the REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": user_prompt
                }]
            }],
            "systemInstruction": {
                "parts": [{
                    "text": system_instruction
                }]
            },
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors in response
        if 'error' in result:
            raise Exception(f"API Error: {result['error'].get('message', 'Unknown error')}")
        
        # Extract text from response
        if 'candidates' not in result or len(result['candidates']) == 0:
            raise Exception(f"No candidates in response: {json.dumps(result)[:200]}")
        
        candidate = result['candidates'][0]
        if 'content' not in candidate:
            raise Exception(f"No content in candidate: {json.dumps(candidate)[:200]}")
        
        if 'parts' not in candidate['content']:
            raise Exception(f"No parts in content: {json.dumps(candidate['content'])[:200]}")
        
        text = candidate['content']['parts'][0]['text'].strip()
        
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
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "API request timed out"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse AI response as JSON: {str(e)}",
            "raw_response": text if 'text' in locals() else None
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
