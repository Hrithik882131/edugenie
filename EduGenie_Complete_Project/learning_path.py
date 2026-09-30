from gemini_client import generate_text

SYSTEM = """You are EduGenie, a personalized learning-path designer.
Create practical educational paths from beginner to advanced.
Use realistic progression and explain why each stage matters.
Recommend general resource types such as official documentation, books,
practice exercises, projects, or reputable educational videos.
Do not invent exact URLs.
"""


def get_learning_recommendations(topic: str, level: str = "Beginner", goal: str = "") -> str:
    prompt = f"""Create a structured learning path for:

Topic: {topic}
Current level: {level}
Goal: {goal}

Include:
1. Prerequisites
2. Stage 1 - Beginner
3. Stage 2 - Intermediate
4. Stage 3 - Advanced
5. A suggested weekly timeline
6. Practice/project ideas
7. Resource suggestions by type
8. A simple self-check method

Keep the plan practical and easy to follow."""
    return generate_text(prompt, system_instruction=SYSTEM, temperature=0.45, max_output_tokens=1800)
