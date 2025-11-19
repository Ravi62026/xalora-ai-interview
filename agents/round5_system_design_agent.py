from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json

class SystemDesignAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.0 for data analysis/system design (per DeepSeek docs)
        self.temperature = 1.0
    
    def get_system_prompt(self) -> str:
        return """
        You are a system design expert conducting architecture interviews.
        
        CRITICAL RULES:
        - EVERY question MUST be based on their experience AND previous answers
        - Use previous answers to explore design decisions deeper
        - Adjust complexity based on experience level
        - Don't repeat questions
        - DON'T address candidate by name
        - Focus on design thinking and trade-offs
        - NO SCORING - just ask questions
        
        Return ONLY JSON: {"question": "your system design question"}
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        session_data = context.get("session_data", {})
        all_previous_answers = context.get("all_previous_answers", [])
        question_number = context.get("question_number", 1)
        resume_analysis = context.get("resume_analysis", {})
        
        experience = session_data.get("candidate_info", {}).get("experience", "")
        skills = resume_analysis.get("extracted_skills", [])
        
        previous_context = ""
        if all_previous_answers:
            previous_context = "\n".join([f"Answer {i+1}: {ans[:200]}" for i, ans in enumerate(all_previous_answers)])
        
        user_input = f"""
        Generate system design question {question_number}.
        
        CANDIDATE EXPERIENCE: {experience}
        CANDIDATE SKILLS: {', '.join(skills) if skills else 'General software development'}
        
        PREVIOUS ANSWERS:
        {previous_context if previous_context else "This is the first question"}
        
        Generate a system design question that:
        1. Is appropriate for their experience level
        2. Builds on their previous answers (explore design decisions deeper)
        3. Tests design thinking, scalability, and trade-offs
        4. Relates to technologies they know
        5. Does NOT repeat previous questions
        6. Does NOT use their name
        
        Return ONLY JSON: {{"question": "your question"}}
        """
        
        # Use temperature 1.0 for system design analysis
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.0)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"question": response.strip().replace('"', '').replace('{', '').replace('}', '')}
