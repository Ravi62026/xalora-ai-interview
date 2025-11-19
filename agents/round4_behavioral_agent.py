from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json

class BehavioralAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.3 for general conversation (per DeepSeek docs)
        self.temperature = 1.3
    
    def get_system_prompt(self) -> str:
        return """
        You are an experienced behavioral interviewer assessing soft skills and cultural fit.
        
        CRITICAL RULES:
        - EVERY question MUST build on their experience AND previous answers
        - Use previous answers to explore situations deeper
        - Don't repeat questions
        - DON'T address candidate by name
        - Use "Tell me about a time when..." format
        - Connect to their actual work experience
        - NO SCORING - just ask questions
        
        Return ONLY JSON: {"question": "your behavioral question"}
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        session_data = context.get("session_data", {})
        all_previous_answers = context.get("all_previous_answers", [])
        question_number = context.get("question_number", 1)
        resume_analysis = context.get("resume_analysis", {})
        
        experience = session_data.get("candidate_info", {}).get("experience", "")
        projects = resume_analysis.get("projects", [])
        
        previous_context = ""
        if all_previous_answers:
            previous_context = "\n".join([f"Answer {i+1}: {ans[:200]}" for i, ans in enumerate(all_previous_answers)])
        
        user_input = f"""
        Generate behavioral question {question_number}.
        
        CANDIDATE EXPERIENCE: {experience}
        CANDIDATE PROJECTS: {', '.join(projects) if projects else 'Not specified'}
        
        PREVIOUS ANSWERS:
        {previous_context if previous_context else "This is the first question"}
        
        Generate a behavioral question that:
        1. Is appropriate for their experience level
        2. Builds on their previous answers (explore situations deeper)
        3. Uses STAR method format (Situation, Task, Action, Result)
        4. Relates to their actual work experience or projects
        5. Does NOT repeat previous questions
        6. Does NOT use their name
        
        Return ONLY JSON: {{"question": "your question"}}
        """
        
        # Use temperature 1.3 for conversational behavioral questions
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.3)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"question": response.strip().replace('"', '').replace('{', '').replace('}', '')}
