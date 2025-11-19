from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json

class TechnicalAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.0 for data analysis/technical discussion (per DeepSeek docs)
        self.temperature = 1.0
    
    def get_system_prompt(self) -> str:
        return """
        You are a senior technical interviewer conducting in-depth technical assessments.
        
        CRITICAL RULES:
        - EVERY question MUST be based on resume skills AND previous answers
        - Use previous answers to explore technical depth
        - Don't repeat questions
        - DON'T address candidate by name
        - Keep questions technical but clear
        - Ask about specific technologies they mentioned
        - NO SCORING - just ask questions
        
        Return ONLY JSON: {"question": "your technical question"}
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        resume_analysis = context.get("resume_analysis", {})
        all_previous_answers = context.get("all_previous_answers", [])
        question_number = context.get("question_number", 1)
        job_description = context.get("job_description", "")
        
        skills = resume_analysis.get("extracted_skills", [])
        
        previous_context = ""
        if all_previous_answers:
            previous_context = "\n".join([f"Answer {i+1}: {ans[:200]}" for i, ans in enumerate(all_previous_answers)])
        
        user_input = f"""
        Generate technical question {question_number}.
        
        CANDIDATE SKILLS: {', '.join(skills) if skills else 'General programming'}
        JOB REQUIREMENTS: {job_description[:200]}
        
        PREVIOUS ANSWERS:
        {previous_context if previous_context else "This is the first question"}
        
        Generate a technical question that:
        1. Tests their knowledge of specific skills from their resume
        2. Builds on their previous answers (go deeper or explore related concepts)
        3. Explores technical depth and understanding
        4. Does NOT repeat previous questions
        5. Does NOT use their name
        
        Return ONLY JSON: {{"question": "your question"}}
        """
        
        # Use temperature 1.0 for technical analysis
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.0)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"question": response.strip().replace('"', '').replace('{', '').replace('}', '')}
