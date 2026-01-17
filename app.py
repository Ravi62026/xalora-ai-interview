"""
Xalora AI Interview System - Corrected Version
Every question based on resume + previous answers
No per-answer scoring, only final comprehensive report
"""
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from colorama import init, Fore, Style

init(autoreset=True)

from agents.round0_resume_agent import ResumeAnalysisAgent
from agents.round1_formal_qa_agent import FormalQAAgent
from agents.round2_coding_agent import CodingAgent
from agents.round3_technical_agent import TechnicalAgent
from agents.round4_behavioral_agent import BehavioralAgent
from agents.round5_system_design_agent import SystemDesignAgent

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_info(msg):
    print(f"{Fore.CYAN}[INFO] {datetime.now().strftime('%H:%M:%S')} - {msg}{Style.RESET_ALL}")

def log_success(msg):
    print(f"{Fore.GREEN}[SUCCESS] {datetime.now().strftime('%H:%M:%S')} - {msg}{Style.RESET_ALL}")

def log_ai(msg):
    print(f"{Fore.MAGENTA}[AI] {datetime.now().strftime('%H:%M:%S')} - {msg}{Style.RESET_ALL}")

def log_error(msg):
    print(f"{Fore.RED}[ERROR] {datetime.now().strftime('%H:%M:%S')} - {msg}{Style.RESET_ALL}")

def log_request(endpoint, data=None):
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"[REQUEST] {datetime.now().strftime('%H:%M:%S')} - {endpoint}")
    print(f"{'='*60}{Style.RESET_ALL}")
    if data:
        print(f"{Fore.CYAN}[DATA] {data}{Style.RESET_ALL}")

def log_response(endpoint, data=None):
    print(f"{Fore.GREEN}[RESPONSE] {endpoint} - SUCCESS{Style.RESET_ALL}")
    if data:
        print(f"{Fore.CYAN}[RESULT] {data}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

app = FastAPI(title="Xalora AI Interview System")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# NO SESSION STORAGE - Express handles sessions in MongoDB
# This is now a STATELESS AI service

log_info("Initializing AI agents...")
agents = {
    "resume": ResumeAnalysisAgent(),
    "formal_qa": FormalQAAgent(),
    "coding": CodingAgent(),
    "technical": TechnicalAgent(),
    "behavioral": BehavioralAgent(),
    "system_design": SystemDesignAgent()
}
log_success("All AI agents initialized")

# PDF extraction is handled by Express.js using pdf-parse
# Voice services (TTS/STT) are handled by browser APIs and Express.js

@app.get("/")
async def root():
    """API root endpoint - health check"""
    return {
        "service": "Xalora AI Interview System",
        "status": "running",
        "version": "2.0",
        "description": "Stateless AI service for interview question generation and evaluation",
        "endpoints": [
            "/api/analyze-resume",
            "/api/generate-question",
            "/api/evaluate-answer",
            "/api/generate-followup",
            "/api/generate-final-report",
            "/api/evaluate-coding"
        ]
    }

@app.post("/api/analyze-resume")
async def analyze_resume(
    resume_text: str = Form(...),
    job_description: str = Form(""),  # Optional, default to empty string
    company_type: str = Form("startup")  # Optional, default to startup
):
    """
    Stateless resume analysis endpoint
    Called by Express during session creation
    Returns AI analysis without storing any session data
    """
    try:
        log_request("/api/analyze-resume", {
            "resume_length": len(resume_text),
            "job_description_length": len(job_description) if job_description else 0,
            "company_type": company_type
        })
        
        log_ai("Analyzing resume with DeepSeek...")
        
        resume_agent = agents["resume"]
        analysis_result = await resume_agent.process_input({
            "resume_text": resume_text,
            "job_description": job_description,
            "company_type": company_type
        })
        
        log_success("Resume analysis complete")
        log_response("/api/analyze-resume", {
            "skills_found": len(analysis_result.get("analysis", {}).get("extracted_skills", [])),
            "projects_found": len(analysis_result.get("analysis", {}).get("projects", []))
        })
        
        return {
            "success": True,
            "analysis": analysis_result.get("analysis", {})
        }
        
    except Exception as e:
        log_error(f"Resume analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-question")
async def generate_question(
    round_type: str = Form(...),
    resume_text: str = Form(...),
    resume_analysis: str = Form("{}"),  # JSON string from Express - optional
    job_description: str = Form(""),  # Optional
    company_type: str = Form("startup"),  # Optional, default to startup
    candidate_info: str = Form("{}"),  # JSON string from Express - optional
    all_previous_qa: str = Form("[]"),  # JSON string - all Q&A history from MongoDB
    question_number: int = Form(...),
    max_questions: int = Form(...),
    coding_difficulty: str = Form(None)
):
    """
    Stateless question generation endpoint
    All context passed from Express (which reads from MongoDB)
    No session storage - pure AI processing
    """
    try:
        log_request("/api/generate-question", {
            "round_type": round_type,
            "question_number": question_number,
            "max_questions": max_questions,
            "company_type": company_type,
            "coding_difficulty": coding_difficulty
        })
        
        # Parse JSON strings from Express
        resume_analysis_dict = json.loads(resume_analysis)
        candidate_info_dict = json.loads(candidate_info)
        all_previous_qa_list = json.loads(all_previous_qa)
        
        log_info(f"Previous Q&A count: {len(all_previous_qa_list)}")
        
        # Extract previous answers for backward compatibility
        all_previous_answers = [qa.get("answer", "") for qa in all_previous_qa_list]
        
        # Build context for AI agent (same structure as before)
        context = {
            "session_data": {
                "candidate_info": candidate_info_dict,
                "resume_analysis": resume_analysis_dict,
                "resume_text": resume_text,
                "job_description": job_description,
                "company_type": company_type
            },
            "resume_analysis": resume_analysis_dict,
            "resume_text": resume_text,
            "job_description": job_description,
            "company_type": company_type,
            "all_previous_answers": all_previous_answers,
            "all_previous_qa": all_previous_qa_list,  # Full Q&A history
            "question_number": question_number,
            "max_questions": max_questions
        }
        
        log_ai(f"Generating {round_type} question {question_number}/{max_questions}...")
        
        # Handle coding round difficulty
        if round_type == "coding":
            context["action"] = "generate_problem"
            if coding_difficulty:
                context["difficulty"] = coding_difficulty
            else:
                # Fallback based on company type
                context["difficulty"] = "hard" if company_type == "product_based" else "moderate" if company_type == "service_based" else "easy"
            log_info(f"Coding difficulty: {context['difficulty']}")
        
        # Get appropriate agent
        agent = agents.get(round_type)
        if not agent:
            log_error(f"Invalid round type: {round_type}")
            raise HTTPException(status_code=400, detail=f"Invalid round type: {round_type}")
        
        # Generate question using AI
        question_result = await agent.process_input(context)
        
        question_text = question_result.get("question", "")
        log_success(f"Question generated: {question_text[:80]}...")
        log_response("/api/generate-question", {
            "question_number": question_number,
            "question_length": len(question_text)
        })
        
        # Return ONLY the question (Express will store in MongoDB)
        return {
            "success": True,
            "question": question_text,
            "question_data": question_result,
            "question_number": question_number,
            "max_questions": max_questions
        }
        
    except json.JSONDecodeError as e:
        log_error(f"JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON in request: {str(e)}")
    except Exception as e:
        log_error(f"Failed to generate question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# REMOVED: /api/submit-answer endpoint
# Express handles answer storage in MongoDB
# This Python service is now stateless - no data storage


# ============================================================
# NEW STATELESS ENDPOINTS FOR INTELLIGENT INTERVIEW FLOW
# ============================================================

@app.post("/api/evaluate-answer")
async def evaluate_answer(
    question: str = Form(...),
    answer: str = Form(...),
    round_type: str = Form(...),
    current_followup_count: int = Form(0),
    time_remaining: int = Form(300)
):
    """
    Stateless answer evaluation endpoint
    
    Called by Express after user submits answer
    Returns AI evaluation + decision on what to do next
    """
    try:
        log_request("/api/evaluate-answer", {
            "round_type": round_type,
            "answer_length": len(answer),
            "followup_count": current_followup_count,
            "time_remaining": time_remaining
        })
        
        log_info(f"Question: {question[:60]}...")
        log_info(f"Answer preview: {answer[:100]}...")
        
        log_ai(f"Evaluating {round_type} answer (followup #{current_followup_count})...")
        
        # Get appropriate agent for the round type
        agent = agents.get(round_type)
        if not agent:
            log_info(f"Using formal_qa agent as fallback for {round_type}")
            agent = agents.get("formal_qa")
        
        # Decide next action (includes evaluation)
        decision = await agent.decide_next_action(
            question=question,
            answer=answer,
            round_type=round_type,
            current_followup_count=current_followup_count,
            time_remaining=time_remaining
        )
        
        log_success(f"Evaluation complete: {decision['action']} ({decision['reason']})")
        log_response("/api/evaluate-answer", {
            "action": decision['action'],
            "score": decision.get('evaluation', {}).get('overall_quality', 'N/A'),
            "followup_type": decision.get('followup_type')
        })
        
        return {
            "success": True,
            "evaluation": decision.get("evaluation", {}),
            "decision": {
                "action": decision["action"],
                "reason": decision["reason"],
                "message": decision["message"],
                "feedback": decision["feedback"],
                "followup_type": decision.get("followup_type"),
                "followup_count": decision["followup_count"]
            }
        }
        
    except Exception as e:
        log_error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-followup")
async def generate_followup(
    question: str = Form(...),
    answer: str = Form(...),
    followup_type: str = Form(...),
    round_type: str = Form(...),
    resume_analysis: str = Form("{}"),
    all_previous_qa: str = Form("[]")
):
    """
    Stateless follow-up question generation
    
    Called by Express when decision.action == "followup"
    Generates contextual follow-up based on answer
    """
    try:
        log_request("/api/generate-followup", {
            "round_type": round_type,
            "followup_type": followup_type,
            "answer_length": len(answer)
        })
        
        log_ai(f"Generating {followup_type} follow-up for {round_type}...")
        log_info(f"Original question: {question[:50]}...")
        log_info(f"Candidate answer: {answer[:80]}...")
        
        # Parse JSON context
        resume_analysis_dict = json.loads(resume_analysis)
        all_previous_qa_list = json.loads(all_previous_qa)
        
        # Build context
        context = {
            "resume_analysis": resume_analysis_dict,
            "all_previous_qa": all_previous_qa_list
        }
        
        # Get agent
        agent = agents.get(round_type)
        if not agent:
            log_info(f"Using formal_qa agent as fallback")
            agent = agents.get("formal_qa")
        
        # Generate follow-up
        followup_question = await agent.generate_followup(
            original_question=question,
            candidate_answer=answer,
            followup_type=followup_type,
            round_type=round_type,
            context=context
        )
        
        log_success(f"Follow-up generated: {followup_question[:50]}...")
        
        return {
            "success": True,
            "followup_question": followup_question
        }
        
    except json.JSONDecodeError as e:
        log_error(f"JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        log_error(f"Follow-up generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-final-report")
async def generate_final_report(
    candidate_info: str = Form(...),
    resume_analysis: str = Form(...),
    all_rounds_qa: str = Form(...)
):
    """
    Stateless final report generation
    
    Called by Express when interview is complete
    Express sends ALL data from MongoDB for comprehensive analysis
    """
    try:
        log_request("/api/generate-final-report", {
            "candidate_info_length": len(candidate_info),
            "resume_analysis_length": len(resume_analysis),
            "all_rounds_qa_length": len(all_rounds_qa)
        })
        
        log_ai("Generating comprehensive final report...")
        
        # Parse JSON inputs
        candidate_info_dict = json.loads(candidate_info)
        resume_analysis_dict = json.loads(resume_analysis)
        all_rounds_qa_dict = json.loads(all_rounds_qa)
        
        log_info(f"Candidate: {candidate_info_dict.get('name', 'Unknown')}")
        log_info(f"Rounds to analyze: {list(all_rounds_qa_dict.keys())}")
        
        total_questions = sum(
            len(qa_list) if isinstance(qa_list, list) else 0 
            for qa_list in all_rounds_qa_dict.values()
        )
        log_info(f"Total Q&A pairs: {total_questions}")
        
        
        # Build report prompt
        system_prompt = """You are an expert interview evaluator generating a comprehensive final report.

Your report should include:
1. OVERALL ASSESSMENT: Overall impression and score (0-100)
2. ROUND-BY-ROUND ANALYSIS: Performance in each interview round
3. STRENGTHS: Key strengths demonstrated
4. AREAS FOR IMPROVEMENT: Specific areas to work on
5. SKILL ASSESSMENT: Technical and soft skills evaluation
6. RECOMMENDATIONS: Specific actionable advice
7. HIRING RECOMMENDATION: hire/maybe/no_hire with reasoning

Be specific, reference actual answers, and provide actionable feedback.

Return valid JSON only."""

        # Format all Q&A for the prompt
        qa_summary = ""
        for round_name, qa_list in all_rounds_qa_dict.items():
            qa_summary += f"\n\n=== {round_name.upper().replace('_', ' ')} ROUND ===\n"
            if isinstance(qa_list, list):
                for i, qa in enumerate(qa_list, 1):
                    qa_summary += f"\nQ{i}: {qa.get('question', 'N/A')}"
                    qa_summary += f"\nA{i}: {qa.get('answer', 'N/A')[:300]}..."
                    if qa.get('evaluation'):
                        eval_data = qa['evaluation']
                        qa_summary += f"\nScore: {eval_data.get('overall_quality', 'N/A')}"
        
        user_input = f"""
CANDIDATE INFORMATION:
- Name: {candidate_info_dict.get('name', 'Unknown')}
- Experience: {candidate_info_dict.get('experience', 'Not specified')}
- Target Role: Based on job description

RESUME ANALYSIS:
- Skills: {', '.join(resume_analysis_dict.get('extracted_skills', [])[:10])}
- Experience Level: {resume_analysis_dict.get('experience_level', 'Not specified')}
- Strengths: {', '.join(resume_analysis_dict.get('strengths', [])[:5])}

INTERVIEW TRANSCRIPT:
{qa_summary}

Generate comprehensive final report in this JSON format:
{{
    "overall_score": 0-100,
    "overall_feedback": "Overall assessment...",
    "round_analysis": [
        {{
            "round": "round_name",
            "score": 0-100,
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."],
            "key_observations": "..."
        }}
    ],
    "skill_assessment": [
        {{
            "skill": "skill_name",
            "level": "beginner|intermediate|advanced|expert",
            "evidence": "Based on their answer about..."
        }}
    ],
    "strengths": ["Overall strength 1", "..."],
    "improvements_needed": ["Area to improve 1", "..."],
    "recommendations": ["Specific recommendation 1", "..."],
    "hiring_recommendation": {{
        "decision": "strong_hire|hire|maybe|no_hire",
        "confidence": 0-100,
        "reasoning": "..."
    }}
}}"""

        # Use the resume agent for generating the report (it's designed for analysis)
        agent = agents.get("resume")
        
        response = await agent.generate_response(
            system_prompt=system_prompt,
            user_input=user_input,
            temperature=0.5
        )
        
        # Parse response
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        response = response.strip()
        
        report = json.loads(response)
        
        log_success(f"Final report generated: Score {report.get('overall_score', 'N/A')}/100")
        
        return {
            "success": True,
            "report": report
        }
        
    except json.JSONDecodeError as e:
        log_error(f"JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        log_error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate-coding")
async def evaluate_coding(
    code: str = Form(...),
    problem_data: str = Form(...),  # JSON string with problem and test cases
    test_cases: str = Form("{}")  # JSON string with test cases
):
    """
    Stateless code evaluation endpoint
    
    All data passed from Express (problem from MongoDB)
    Uses AI to evaluate code quality
    """
    try:
        log_ai("Evaluating code with AI...")
        
        # Parse JSON inputs
        problem_dict = json.loads(problem_data)
        test_cases_dict = json.loads(test_cases)
        
        # For now, use AI to evaluate the code quality
        agent = agents["coding"]
        evaluation = await agent.process_input({
            "action": "evaluate_code",
            "code": code,
            "problem_data": problem_dict,
            "test_cases": test_cases_dict
        })
        
        # Get AI evaluation score
        score = evaluation.get("scores", {}).get("correctness", 0)
        
        # Determine if passed based on AI evaluation
        all_passed = score >= 70
        
        log_success(f"Code evaluation: Score {score}/100, Passed: {all_passed}")
        
        return {
            "success": True,
            "all_passed": all_passed,
            "evaluation": evaluation,
            "score": score
        }
        
    except json.JSONDecodeError as e:
        log_error(f"JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        log_error(f"Code evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice services (TTS/STT) are now handled by:
# - Browser's Web Speech API for STT (client-side)
# - Express.js proxy to external TTS service if needed
# This keeps Python service stateless and focused on AI processing only

@app.post("/api/analyze-round")
async def analyze_round(
    round_type: str = Form(...),
    qa_history: str = Form(...),
    round_score: int = Form(...)
):
    """
    Analyze a single round's performance
    Generate strengths, weaknesses, and recommendations
    """
    try:
        log_request("/api/analyze-round", {"round_type": round_type, "score": round_score})
        
        qa_data = json.loads(qa_history)
        
        # Simple rule-based analysis (can be enhanced with AI)
        strengths = []
        weaknesses = []
        recommendations = []
        
        if round_score >= 80:
            strengths.append(f"Excellent performance in {round_type} round")
            strengths.append("Demonstrated strong understanding of concepts")
            recommendations.append("Continue practicing to maintain this level")
        elif round_score >= 60:
            strengths.append(f"Good performance in {round_type} round")
            weaknesses.append("Some areas need improvement")
            recommendations.append(f"Review {round_type} fundamentals")
        else:
            weaknesses.append(f"Needs significant improvement in {round_type}")
            recommendations.append(f"Focus on strengthening {round_type} skills")
            recommendations.append("Practice more problems in this area")
        
        # Add specific feedback based on round type
        if round_type == "coding":
            if round_score < 70:
                recommendations.append("Practice more DSA problems on LeetCode/HackerRank")
        elif round_type == "technical":
            if round_score < 70:
                recommendations.append("Review framework documentation and best practices")
        elif round_type == "system_design":
            if round_score < 70:
                recommendations.append("Study system design patterns and scalability concepts")
        
        log_success(f"Round analysis complete for {round_type}")
        
        return {
            "success": True,
            "analysis": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        log_error(f"Round analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-interview")
async def analyze_interview(
    rounds: str = Form(...),
    overall_score: int = Form(...),
    candidate_info: str = Form(...),
    position: str = Form("")
):
    """
    Generate overall interview analysis and hiring recommendation
    """
    try:
        log_request("/api/analyze-interview", {"overall_score": overall_score, "position": position})
        
        rounds_data = json.loads(rounds)
        candidate_data = json.loads(candidate_info)
        
        # Aggregate strengths and weaknesses from all rounds
        all_strengths = []
        all_weaknesses = []
        all_recommendations = []
        
        for round_data in rounds_data:
            if "roundAnalysis" in round_data:
                all_strengths.extend(round_data["roundAnalysis"].get("strengths", []))
                all_weaknesses.extend(round_data["roundAnalysis"].get("weaknesses", []))
                all_recommendations.extend(round_data["roundAnalysis"].get("recommendations", []))
        
        # Deduplicate
        all_strengths = list(set(all_strengths))
        all_weaknesses = list(set(all_weaknesses))
        all_recommendations = list(set(all_recommendations))
        
        # Add role-specific analysis based on position
        position_lower = position.lower()
        
        # Role-based strengths
        if overall_score >= 70:
            if "frontend" in position_lower or "ui" in position_lower:
                all_strengths.append("Strong grasp of frontend technologies")
                all_strengths.append("Good understanding of UI/UX principles")
            elif "backend" in position_lower:
                all_strengths.append("Solid backend development knowledge")
                all_strengths.append("Good understanding of APIs and databases")
            elif "fullstack" in position_lower or "full stack" in position_lower:
                all_strengths.append("Well-rounded full-stack capabilities")
                all_strengths.append("Balanced frontend and backend knowledge")
            elif "devops" in position_lower:
                all_strengths.append("Good understanding of DevOps practices")
            elif "data" in position_lower or "ml" in position_lower or "ai" in position_lower:
                all_strengths.append("Strong analytical and problem-solving skills")
            else:
                all_strengths.append("Demonstrated technical competence")
        
        # Role-based recommendations
        if "frontend" in position_lower or "ui" in position_lower:
            all_recommendations.append("Practice building responsive layouts and components")
            all_recommendations.append("Study modern CSS techniques and accessibility")
            if overall_score < 70:
                all_recommendations.append("Strengthen React/Vue fundamentals")
        elif "backend" in position_lower:
            all_recommendations.append("Practice designing RESTful APIs")
            all_recommendations.append("Study database optimization and scaling")
            if overall_score < 70:
                all_recommendations.append("Review Node.js/Express best practices")
        elif "fullstack" in position_lower or "full stack" in position_lower:
            all_recommendations.append("Practice end-to-end application development")
            all_recommendations.append("Study both frontend and backend integration")
        elif "devops" in position_lower:
            all_recommendations.append("Practice CI/CD pipeline setup")
            all_recommendations.append("Study containerization and orchestration")
        elif "data" in position_lower:
            all_recommendations.append("Practice data analysis and visualization")
            all_recommendations.append("Study statistical methods and ML algorithms")
        elif "ml" in position_lower or "ai" in position_lower:
            all_recommendations.append("Practice implementing ML models")
            all_recommendations.append("Study deep learning frameworks")
        
        # Performance-based weaknesses
        if overall_score < 50:
            all_weaknesses.append("Needs significant improvement in core concepts")
            all_weaknesses.append("Limited practical experience evident")
        elif overall_score < 70:
            all_weaknesses.append("Some gaps in fundamental knowledge")
        
        # Limit to top items
        all_strengths = all_strengths[:6]
        all_weaknesses = all_weaknesses[:6]
        all_recommendations = all_recommendations[:6]
        
        # Generate hiring recommendation
        if overall_score >= 85:
            decision = "Strong Hire"
            reason = f"Exceptional performance with {overall_score}/100 overall score. Candidate demonstrated strong technical skills and excellent communication abilities. Ready for {position} role."
        elif overall_score >= 70:
            decision = "Hire"
            reason = f"Good performance with {overall_score}/100 overall score. Candidate shows solid understanding and potential for growth in {position} role."
        elif overall_score >= 50:
            decision = "Maybe"
            reason = f"Average performance with {overall_score}/100 overall score. Candidate needs improvement in some areas but shows potential for {position} role with proper training."
        else:
            decision = "No Hire"
            reason = f"Below expectations with {overall_score}/100 overall score. Candidate needs significant improvement before being considered for {position} role."
        
        log_success(f"Overall analysis complete - Decision: {decision}")
        
        return {
            "success": True,
            "overall_analysis": {
                "strengths": all_strengths if all_strengths else ["Participated in interview", "Showed willingness to learn"],
                "weaknesses": all_weaknesses if all_weaknesses else ["Needs more practice and preparation"],
                "recommendations": all_recommendations if all_recommendations else ["Continue learning and practicing", "Focus on fundamentals"]
            },
            "hiring_recommendation": {
                "decision": decision,
                "reason": reason
            }
        }
        
    except Exception as e:
        log_error(f"Overall analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"{Fore.YELLOW}📍 Server: http://localhost:8000{Style.RESET_ALL}")
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
