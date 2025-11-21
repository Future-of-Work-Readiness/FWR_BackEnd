"""
Quiz Generation - Final Working Version
Calls the bash script which we know works
"""
import subprocess
import json
import os

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASH_SCRIPT = os.path.join(SCRIPT_DIR, "quiz_api_call.sh")

def generate_quiz_question(
    specialization: str,
    topic: str,
    difficulty: int = 3,
    num_options: int = 4
):
    """Generate a single quiz question"""
    
    difficulty_map = {
        1: "Beginner",
        2: "Intermediate", 
        3: "Advanced",
        4: "Expert",
        5: "Master"
    }
    
    difficulty_desc = difficulty_map.get(difficulty, "Intermediate")
    
    prompt = f"""Generate ONE multiple-choice quiz question about "{topic}" in {specialization} for a {difficulty_desc} level developer.

Return ONLY valid JSON (no markdown, no code blocks) in this exact format:
{{
    "question": "the question text here",
    "options": [
        {{"id": "A", "text": "first option"}},
        {{"id": "B", "text": "second option"}},
        {{"id": "C", "text": "third option"}},
        {{"id": "D", "text": "fourth option"}}
    ],
    "correct_answer": "A",
    "explanation": "why A is correct"
}}"""
    
    try:
        # Call the bash script with the prompt
        result = subprocess.run(
            [BASH_SCRIPT, prompt],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Script failed: {result.stderr}"
            }
        
        # Parse the API response
        api_response = json.loads(result.stdout)
        
        if 'error' in api_response:
            return {
                "success": False,
                "error": api_response['error'].get('message', 'API error')
            }
        
        # Extract the generated text
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
        
        # Validate
        required_keys = ["question", "options", "correct_answer", "explanation"]
        if not all(key in question_data for key in required_keys):
            raise ValueError("Generated question missing required fields")
        
        return {
            "success": True,
            "data": question_data
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
    """Generate a complete quiz"""
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


if __name__ == "__main__":
    print("=" * 60)
    print("GENERATING QUIZ QUESTIONS")
    print("=" * 60)
    
    quiz = generate_full_quiz(
        specialization="Frontend Development",
        topics=["React Hooks", "State Management"],
        questions_per_topic=2,
        difficulty=3
    )
    
    print(f"\n✅ Generated {len(quiz)} questions total!")
    if len(quiz) > 0:
        print("\nFirst question:")
        print(json.dumps(quiz[0], indent=2))
