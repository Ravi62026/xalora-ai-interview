from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json
import re

class ResumeAnalysisAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.0 for data analysis (per DeepSeek docs)
        self.temperature = 1.0
    
    def get_system_prompt(self) -> str:
        return """
        You are an expert HR and Technical Recruiter AI specializing in holistic resume analysis.
        
        Your task is to extract COMPLETE information about the candidate:
        1. Technical skills (programming languages, frameworks, tools)
        2. Soft skills (communication, leadership, teamwork)
        3. Education (degree, university, major, graduation year, GPA if mentioned)
        4. Projects (personal, academic, professional)
        5. Work experience (companies, roles, duration)
        6. Hobbies and interests (sports, music, reading, etc.)
        7. Certifications and courses
        8. Volunteer work or community involvement
        9. Extracurricular activities
        10. Languages spoken
        11. Career goals and aspirations (if mentioned)
        
        Always respond in JSON format with the following structure:
        {
            "extracted_skills": ["skill1", "skill2", ...],
            "soft_skills": ["communication", "leadership", ...],
            "experience_years": number,
            "projects": ["project1", "project2", ...],
            "education": {
                "degree": "Bachelor's/Master's/PhD",
                "major": "Computer Science",
                "university": "University Name",
                "graduation_year": "2020",
                "gpa": "3.8/4.0"
            },
            "hobbies": ["hobby1", "hobby2", ...],
            "interests": ["interest1", "interest2", ...],
            "certifications": ["cert1", "cert2", ...],
            "languages": ["English", "Spanish", ...],
            "volunteer_work": ["activity1", ...],
            "extracurricular": ["activity1", ...],
            "role_alignment": {
                "matching_skills": ["skill1", ...],
                "skill_gaps": ["gap1", ...],
                "alignment_score": 0.0-1.0
            },
            "interview_plan": {
                "focus_areas": ["area1", "area2", ...],
                "difficulty_level": "beginner|intermediate|advanced",
                "estimated_duration": minutes,
                "personalized_topics": ["topic1", ...]
            },
            "context_for_rounds": {
                "strengths_to_probe": ["strength1", ...],
                "weaknesses_to_explore": ["weakness1", ...],
                "follow_up_angles": ["angle1", ...]
            }
        }
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        resume_text = context.get("resume_text", "")
        job_description = context.get("job_description", "")
        company_type = context.get("company_type", "")
        
        user_input = f"""
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        COMPANY TYPE: {company_type}
        
        Please analyze this resume against the job description and create a comprehensive interview plan.
        """
        
        # Use temperature 1.0 for data analysis
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.0)
        
        try:
            # Clean the response to extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group())
            else:
                # Fallback parsing
                analysis_result = self._parse_fallback_response(response)
            
            return {
                "analysis": analysis_result,
                "raw_response": response,
                "status": "success"
            }
        except json.JSONDecodeError as e:
            return {
                "analysis": self._parse_fallback_response(response),
                "raw_response": response,
                "status": "partial_success",
                "error": str(e)
            }
    
    def _parse_fallback_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        return {
            "extracted_skills": self._extract_skills_from_text(response),
            "experience_years": 0,
            "key_projects": [],
            "education": "Not specified",
            "role_alignment": {
                "matching_skills": [],
                "skill_gaps": [],
                "alignment_score": 0.5
            },
            "interview_plan": {
                "focus_areas": ["General Technical", "Problem Solving"],
                "difficulty_level": "intermediate",
                "estimated_duration": 150,
                "personalized_topics": ["Technical Skills", "Experience"]
            },
            "context_for_rounds": {
                "strengths_to_probe": [],
                "weaknesses_to_explore": [],
                "follow_up_angles": []
            }
        }
    
    def _extract_skills_from_text(self, text: str) -> list:
        """Extract common technical skills from text"""
        common_skills = [
            "Python", "JavaScript", "Java", "C++", "React", "Node.js",
            "Machine Learning", "Deep Learning", "SQL", "MongoDB",
            "AWS", "Docker", "Kubernetes", "Git", "TensorFlow", "PyTorch"
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills