from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json

class FormalQAAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.3 for general conversation (per DeepSeek docs)
        self.temperature = 1.3
    
    def get_system_prompt(self) -> str:
        return """
        You are a warm, friendly HR interviewer conducting an initial conversation with a candidate.
        
        YOUR PERSONALITY:
        - Warm and welcoming, like a friendly HR professional
        - Genuinely interested in the candidate as a person
        - Conversational and natural, not robotic
        - Encouraging and positive
        - Make the candidate feel comfortable
        
        WHAT TO EXPLORE (NOT just technical skills):
        - Educational background (degree, university, favorite subjects)
        - Hobbies and interests outside work
        - Career journey and motivations
        - Personal projects and passions
        - Work-life balance and interests
        - Soft skills (communication, teamwork, leadership)
        - Career goals and aspirations
        - Why they're interested in this role
        - Cultural fit and values
        - Extracurricular activities
        - Volunteer work or community involvement
        - Learning style and growth mindset
        
        CONVERSATION STYLE:
        - Ask open-ended questions
        - Show genuine curiosity
        - Build on their previous answers naturally
        - Mix professional and personal topics
        - Make it feel like a friendly chat, not an interrogation
        - Use phrases like "That's interesting!", "Tell me more about...", "I'm curious..."
        
        CRITICAL RULES:
        - EVERY question MUST build on resume AND previous answers
        - DON'T just focus on technical skills
        - DON'T address candidate by name repeatedly
        - DO make it conversational and warm
        - DO explore the WHOLE person, not just their code
        
        Return ONLY JSON: {"question": "your warm, conversational question"}
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        resume_analysis = context.get("resume_analysis", {})
        resume_text = context.get("resume_text", "")
        all_previous_answers = context.get("all_previous_answers", [])
        question_number = context.get("question_number", 1)
        job_description = context.get("job_description", "")
        session_data = context.get("session_data", {})
        candidate_info = session_data.get("candidate_info", {})
        
        skills = resume_analysis.get("extracted_skills", [])
        projects = resume_analysis.get("projects", [])
        
        previous_context = ""
        if all_previous_answers:
            previous_context = "\n".join([f"Answer {i+1}: {ans[:200]}" for i, ans in enumerate(all_previous_answers)])
        
        user_input = f"""
        Generate question {question_number} for a warm, friendly HR conversation.
        
        CANDIDATE INFO:
        - Age: {candidate_info.get('age', 'Not specified')}
        - Experience: {candidate_info.get('experience', 'Not specified')}
        
        RESUME HIGHLIGHTS:
        - Skills: {', '.join(skills[:5]) if skills else 'Not specified'}
        - Projects: {', '.join(projects[:3]) if projects else 'Not specified'}
        - Resume snippet: {resume_text[:300]}...
        
        JOB ROLE: {job_description[:200]}...
        
        PREVIOUS CONVERSATION:
        {previous_context if previous_context else "This is the opening question - make them feel welcome!"}
        
        Generate a warm, conversational question that:
        1. Builds naturally on their previous answers
        2. Explores different aspects: education, hobbies, interests, career journey, motivations
        3. Is NOT just about technical skills
        4. Feels like a friendly HR chat, not an interrogation
        5. Shows genuine interest in them as a person
        6. Does NOT repeat previous questions
        7. Does NOT use their name repeatedly
        
        Question types to vary:
        - Educational background: "What drew you to study [field]?"
        - Hobbies: "What do you enjoy doing outside of work?"
        - Career journey: "How did you get into [field]?"
        - Motivations: "What excites you most about this role?"
        - Personal growth: "What's something new you've learned recently?"
        - Work style: "How do you like to collaborate with teams?"
        - Values: "What's important to you in a workplace?"
        
        Return ONLY JSON: {{"question": "your warm question"}}
        """
        
        # Use temperature 1.3 for conversational tone
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.3)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"question": response.strip().replace('"', '').replace('{', '').replace('}', '')}
