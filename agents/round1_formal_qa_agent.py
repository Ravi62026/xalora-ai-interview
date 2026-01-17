from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json

class FormalQAAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.2 for natural conversation
        self.temperature = 1.2
    
    def get_system_prompt(self) -> str:
        return """
        You are a friendly HR interviewer conducting the initial screening round.
        
        YOUR ROLE:
        - Warm, professional HR interviewer (not technical)
        - Ask SIMPLE, GENERIC questions about background and motivation
        - Focus on resume, experience, and personal fit
        - Keep questions easy to understand and answer
        - Build rapport and make candidate comfortable
        
        QUESTION STYLE:
        - Simple and straightforward
        - Resume-based (ask about their experience, projects, skills)
        - Personal (motivation, strengths, career goals)
        - NOT too technical or deep
        - Friendly and conversational tone
        
        QUESTION STRUCTURE (10 questions total):
        1. Greeting & Introduction (warm welcome)
        2. Why this role/company? (motivation)
        3. Tell me about a project from your resume (general overview)
        4. What are your key strengths?
        5. What technologies/skills are you most comfortable with?
        6. Describe your work style or team experience
        7. What challenges have you faced and how did you handle them?
        8. Where do you see yourself growing in this role?
        9. What interests you most about this position?
        10. Do you have any questions for us?
        
        CRITICAL RULES:
        - Question 1 MUST be personalized greeting with candidate's name
        - Keep questions SIMPLE and GENERIC
        - Focus on RESUME content (projects, skills, experience)
        - Ask about PERSONAL aspects (motivation, strengths, goals)
        - DON'T ask sharp technical questions (save for Round 2)
        - DON'T ask "Why X over Y?" or trade-off questions
        - DON'T mention scale, failures, or bottlenecks
        - Build on previous answers naturally
        
        EXAMPLES OF GOOD QUESTIONS:
        - "Can you tell me about one of the projects listed on your resume?"
        - "What motivated you to apply for this role?"
        - "What are your strongest technical skills?"
        - "How do you handle working in a team?"
        - "What kind of work environment helps you perform best?"
        
        Return ONLY JSON: {"question": "your simple, friendly question"}
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        resume_analysis = context.get("resume_analysis", {})
        resume_text = context.get("resume_text", "")
        all_previous_answers = context.get("all_previous_answers", [])
        question_number = context.get("question_number", 1)
        job_description = context.get("job_description", "")
        session_data = context.get("session_data", {})
        candidate_info = session_data.get("candidate_info", {})
        
        # QUESTION 1: Personalized greeting
        if question_number == 1:
            name = candidate_info.get('name', '')
            first_name = name.split()[0] if name else "there"
            position = candidate_info.get('position', 'this role')
            
            return {
                "question": f"Hello {first_name}! Thank you for joining us today for the {position} interview. Could you please introduce yourself and tell me a bit about your background?"
            }
        
        skills = resume_analysis.get("extracted_skills", [])
        projects = resume_analysis.get("projects", [])
        
        previous_context = ""
        if all_previous_answers:
            recent_answers = all_previous_answers[-2:]
            previous_context = "\n".join([f"Previous answer {i+1}: {ans[:200]}..." for i, ans in enumerate(recent_answers)])
        
        jd_snippet = job_description[:400] if job_description else "General role"
        position = candidate_info.get('position', 'this role')
        
        # Extract resume specifics
        tech_stack = ', '.join(skills[:8]) if skills else 'various technologies'
        project_names = ', '.join(projects[:3]) if projects else 'your projects'
        
        user_input = f"""
        Generate question {question_number} of 10 for HR screening round.
        
        JOB ROLE:
        {jd_snippet}
        
        CANDIDATE BACKGROUND:
        - Position applying for: {position}
        - Experience: {candidate_info.get('experience', 'Not specified')}
        - Tech Stack: {tech_stack}
        - Key Projects: {project_names}
        
        RECENT CONVERSATION:
        {previous_context if previous_context else "Just introduced themselves"}
        
        QUESTION {question_number} GUIDELINES (SIMPLE & GENERIC):
        
        Q2: Why this role/company?
        Example: "What motivated you to apply for this {position} position?"
        
        Q3: Tell me about a project from your resume
        Example: "I see you worked on [project name]. Can you tell me about that project?"
        
        Q4: What are your key strengths?
        Example: "What would you say are your strongest skills or qualities?"
        
        Q5: Technologies/skills you're comfortable with
        Example: "Which technologies or programming languages are you most comfortable working with?"
        
        Q6: Work style or team experience
        Example: "How do you prefer to work - independently or as part of a team?"
        
        Q7: Challenges you've faced
        Example: "Can you describe a challenge you faced in a project and how you handled it?"
        
        Q8: Growth in this role
        Example: "Where do you see yourself growing or learning in this role?"
        
        Q9: What interests you about this position?
        Example: "What aspect of this role excites you the most?"
        
        Q10: Their questions
        Example: "Do you have any questions for us about the role or the team?"
        
        REQUIREMENTS:
        1. Keep questions SIMPLE and EASY to understand
        2. Focus on RESUME content (mention their projects, skills)
        3. Ask about PERSONAL aspects (motivation, strengths, goals)
        4. DON'T ask technical depth questions (save for Round 2)
        5. DON'T ask about scale, failures, bottlenecks, or trade-offs
        6. Build naturally on previous answers
        7. Keep questions SHORT (1-2 sentences)
        8. Be FRIENDLY and CONVERSATIONAL
        
        Return ONLY JSON: {{"question": "your simple, friendly question"}}
        """
        
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.2)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"question": response.strip().replace('"', '').replace('{', '').replace('}', '')}
