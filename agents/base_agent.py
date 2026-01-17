from openai import AsyncOpenAI
import google.generativeai as genai
import os
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import numpy as np

class BaseInterviewAgent(ABC):
    def __init__(self):
        api_key = "sk-e9b92c79e0aa47a097aadf070f50a1c8"
        
        # Fallback for testing if .env not loaded properly
        if not api_key or api_key == "your_deepseek_api_key_here":
            api_key = "sk-e9b92c79e0aa47a097aadf070f50a1c8"
        
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        # Remove quotes if present
        api_key = api_key.strip('"').strip("'")
        
        # Use OpenAI client with DeepSeek base URL (v1 endpoint)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.model = "deepseek-chat"
        # Default temperature - will be overridden by each agent
        self.temperature = 1.0
        
        # Gemini for embeddings
        gemini_key = "AIzaSyDB4-R5RuEb6t91WgsaLdQ1ssXtDHwczeI"
        if not gemini_key:
            gemini_key = "AIzaSyDB4-R5RuEb6t91WgsaLdQ1ssXtDHwczeI"
        
        genai.configure(api_key=gemini_key.strip('"').strip("'"))
        self.embedding_model = "models/embedding-001"
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return response"""
        pass
    
    async def generate_response(self, system_prompt: str, user_input: str, temperature: float = None) -> str:
        """Generate response using the LLM with optional temperature override"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Use provided temperature or fall back to agent's default
        temp = temperature if temperature is not None else self.temperature
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temp
        )
        
        return response.choices[0].message.content
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for given texts using Gemini"""
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        return embeddings
    
    def create_embedding(self, text: str) -> List[float]:
        """Create single embedding using Gemini"""
        result = genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    def similarity_search(self, query: str, documents: List[str]) -> List[tuple]:
        """Find most similar documents to query using Gemini embeddings"""
        query_embedding = self.create_embedding(query)
        doc_embeddings = self.create_embeddings(documents)
        
        similarities = []
        for i, doc_embedding in enumerate(doc_embeddings):
            # Cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, similarity, documents[i]))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)
    
    # ============================================================
    # NEW METHODS FOR INTELLIGENT INTERVIEW FLOW
    # These enable: Answer Evaluation, Follow-ups, Interruptions
    # ============================================================
    
    async def evaluate_answer_quality(
        self, 
        question: str, 
        answer: str, 
        round_type: str = "general",
        current_followup_count: int = 0
    ) -> Dict[str, Any]:
        """
        AI-powered answer evaluation
        
        PURPOSE: Score answer quality on multiple dimensions
        IMPACT: Enables real-time feedback instead of silent listening
        
        Returns:
            - clarity (0-100): How clear and understandable is the answer?
            - completeness (0-100): Does it fully address the question?
            - relevance (0-100): Is it on-topic or going off-track?
            - depth (0-100): Technical depth and detail level
            - coherence (0-100): Is it well-structured or rambling?
            - overall_quality: "excellent" | "good" | "fair" | "poor" | "incomplete"
            - needs_followup: boolean
            - followup_type: "elaboration" | "clarification" | "redirect" | "none"
            - is_rambling: boolean
            - is_off_track: boolean
            - feedback: Human-friendly feedback message
        """
        system_prompt = """You are an expert interviewer evaluating candidate answers.

EVALUATION CRITERIA (BE LENIENT - This is for practice/testing):
1. CLARITY (0-100): Is the answer clear, well-articulated, and easy to understand?
2. COMPLETENESS (0-100): Does it fully address all aspects of the question?
3. RELEVANCE (0-100): Is it directly related to the question asked?
4. DEPTH (0-100): Does it show appropriate technical knowledge and detail?
5. COHERENCE (0-100): Is it logically structured, not rambling or scattered?

SCORING GUIDELINES (LENIENT MODE):
- Give benefit of doubt - if answer makes sense, score 60+
- Only score < 40 if answer is VERY poor (completely off-topic, nonsense, or 1-2 words)
- Most reasonable answers should get 60-80 range
- Reserve 80+ for truly excellent, detailed answers
- Reserve < 40 for truly terrible answers

DECISION RULES:
- If current_followup_count >= 2: Set needs_followup = false (max limit reached)
- If current_followup_count == 1: Only set needs_followup = true if score < 30 (very strict)
- If answer is completely off-topic (relevance < 30): Set is_off_track = true
- If answer is very scattered/incoherent (coherence < 30): Set is_rambling = true

FEEDBACK GUIDELINES:
- For excellent answers (80+): "Great answer! 👏" or "Excellent explanation!"
- For good answers (60-79): "Good point! 👍" or "Nice insight!"
- For fair answers (40-59): "Okay, I see." or "Interesting perspective."
- For poor/incomplete (< 40): "I see..." or "Let me ask more specifically..."

Return ONLY valid JSON, no markdown, no explanation."""

        user_input = f"""
Question asked: {question}

Candidate's answer: {answer}

Round type: {round_type}
Current follow-up count: {current_followup_count}
Max follow-ups allowed: 2

Evaluate and return JSON:
{{
    "clarity": <0-100>,
    "completeness": <0-100>,
    "relevance": <0-100>,
    "depth": <0-100>,
    "coherence": <0-100>,
    "overall_quality": "excellent|good|fair|poor|incomplete",
    "needs_followup": true/false,
    "followup_type": "elaboration|clarification|redirect|none",
    "is_rambling": true/false,
    "is_off_track": true/false,
    "feedback": "your feedback message",
    "reason": "brief explanation of your evaluation"
}}"""

        try:
            response = await self.generate_response(system_prompt, user_input, temperature=0.3)
            
            # Parse JSON from response
            import json
            # Clean response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            evaluation = json.loads(response)
            
            # Enforce hard limit: No more than 2 follow-ups per question
            if current_followup_count >= 2:
                evaluation["needs_followup"] = False
                evaluation["followup_type"] = "none"
                evaluation["reason"] = "Maximum follow-ups reached (2/2). Moving to next question."
            
            return evaluation
            
        except Exception as e:
            # Return safe default on error
            return {
                "clarity": 50,
                "completeness": 50,
                "relevance": 50,
                "depth": 50,
                "coherence": 50,
                "overall_quality": "fair",
                "needs_followup": False,
                "followup_type": "none",
                "is_rambling": False,
                "is_off_track": False,
                "feedback": "Thank you for your answer.",
                "reason": f"Evaluation error: {str(e)}"
            }
    
    async def decide_next_action(
        self,
        question: str,
        answer: str,
        round_type: str = "general",
        current_followup_count: int = 0,
        time_remaining: int = 300
    ) -> Dict[str, Any]:
        """
        Decide what to do next based on answer evaluation
        
        PURPOSE: Create dynamic interview flow instead of linear Q&A
        IMPACT: Makes interview feel conversational and adaptive
        
        Returns:
            - action: "next_question" | "followup" | "interrupt"
            - reason: Why this action was chosen
            - message: What to say to candidate
            - feedback: Visual feedback to show
            - followup_type: (if action is followup) "elaboration" | "clarification" | "redirect"
            - followup_count: Updated count
        """
        # First, evaluate the answer
        evaluation = await self.evaluate_answer_quality(
            question, 
            answer, 
            round_type,
            current_followup_count
        )
        
        # RULE 1: Hard limit - 2 follow-ups max per question
        if current_followup_count >= 2:
            return {
                "action": "next_question",
                "reason": "followup_limit_reached",
                "message": "Thank you. Let's move to the next question.",
                "feedback": "👍 Good discussion!",
                "evaluation": evaluation,
                "followup_count": current_followup_count
            }
        
        # RULE 2: Check for interruption conditions
        if evaluation.get("is_rambling", False) and evaluation.get("coherence", 100) < 40:
            return {
                "action": "interrupt",
                "reason": "rambling",
                "message": "I see. Let me ask more specifically...",
                "feedback": "⏸️",
                "evaluation": evaluation,
                "followup_count": current_followup_count
            }
        
        # RULE 3: Check for off-track (very lenient now)
        if evaluation.get("is_off_track", False) and evaluation.get("relevance", 100) < 30:
            return {
                "action": "followup",
                "reason": "off_track",
                "message": "That's interesting, but let me refocus...",
                "feedback": "🔄",
                "followup_type": "redirect",
                "evaluation": evaluation,
                "followup_count": current_followup_count + 1
            }
        
        # RULE 4: Check for incomplete answer (first follow-up)
        # DISABLED FOR TESTING - Only follow-up on poor answers now
        # if current_followup_count == 0 and evaluation.get("needs_followup", False):
        #     return {
        #         "action": "followup",
        #         "reason": "incomplete",
        #         "message": "Can you elaborate on that?",
        #         "feedback": "🤔",
        #         "followup_type": evaluation.get("followup_type", "elaboration"),
        #         "evaluation": evaluation,
        #         "followup_count": 1
        #     }
        
        # RULE 4.5: Only follow-up if answer is VERY POOR (completeness < 30)
        if current_followup_count == 0 and evaluation.get("completeness", 100) < 30:
            return {
                "action": "followup",
                "reason": "poor_answer",
                "message": "Can you elaborate on that?",
                "feedback": "🤔",
                "followup_type": "elaboration",
                "evaluation": evaluation,
                "followup_count": 1
            }
        
        # RULE 5: Second follow-up - only if EXTREMELY incomplete (< 25)
        if current_followup_count == 1 and evaluation.get("completeness", 100) < 25:
            return {
                "action": "followup",
                "reason": "still_incomplete",
                "message": "One more thing - can you clarify that?",
                "feedback": "❓",
                "followup_type": "clarification",
                "evaluation": evaluation,
                "followup_count": 2
            }
        
        # RULE 6: Time constraint check
        if time_remaining < 30 and evaluation.get("completeness", 100) < 60:
            return {
                "action": "next_question",
                "reason": "time_constraint",
                "message": "We're running short on time. Let's continue...",
                "feedback": "⏱️",
                "evaluation": evaluation,
                "followup_count": current_followup_count
            }
        
        # DEFAULT: Good answer, move to next question
        quality = evaluation.get("overall_quality", "fair")
        feedback_map = {
            "excellent": "✨ Excellent!",
            "good": "👍 Good answer!",
            "fair": "👌 Okay",
            "poor": "📝 Noted",
            "incomplete": "📋 Noted"
        }
        
        return {
            "action": "next_question",
            "reason": f"{quality}_answer",
            "message": evaluation.get("feedback", "Moving on..."),
            "feedback": feedback_map.get(quality, "👍"),
            "evaluation": evaluation,
            "followup_count": current_followup_count
        }
    
    async def generate_followup(
        self,
        original_question: str,
        candidate_answer: str,
        followup_type: str,
        round_type: str = "general",
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate contextual follow-up question
        
        PURPOSE: Create adaptive, context-aware follow-up questions
        IMPACT: Makes interview feel like a real conversation, not a form
        
        Args:
            original_question: The question that was asked
            candidate_answer: What the candidate said
            followup_type: "elaboration" | "clarification" | "redirect"
            round_type: Type of interview round
            context: Additional context (resume, previous Q&A)
        
        Returns:
            Follow-up question string
        """
        context = context or {}
        
        type_instructions = {
            "elaboration": "Ask them to expand on a specific point they mentioned. Go deeper into details.",
            "clarification": "Ask them to explain something that was unclear or vague. Be specific about what needs clarification.",
            "redirect": "Gently bring them back to the original topic. Reference what they said but steer toward the question."
        }
        
        system_prompt = f"""You are an expert interviewer conducting a {round_type} interview round.

Your task: Generate a follow-up question based on the candidate's answer.

Follow-up type: {followup_type}
Instructions: {type_instructions.get(followup_type, type_instructions['elaboration'])}

RULES:
1. Keep the question SHORT and FOCUSED (1-2 sentences max)
2. Reference something specific from their answer
3. Don't repeat the original question
4. Be conversational, not interrogative
5. Match the tone of the round type

Return ONLY the follow-up question, nothing else."""

        # Build context string
        context_str = ""
        if context.get("resume_analysis"):
            skills = context["resume_analysis"].get("extracted_skills", [])[:3]
            context_str += f"\nCandidate's key skills: {', '.join(skills)}"
        
        user_input = f"""Original question: {original_question}

Candidate's answer: {candidate_answer}

Follow-up type needed: {followup_type}
{context_str}

Generate a short, focused follow-up question:"""

        try:
            followup = await self.generate_response(system_prompt, user_input, temperature=0.7)
            
            # Clean up the response
            followup = followup.strip().strip('"').strip("'")
            
            # Remove any prefixes like "Follow-up:" or "Question:"
            for prefix in ["Follow-up:", "Question:", "Follow up:"]:
                if followup.lower().startswith(prefix.lower()):
                    followup = followup[len(prefix):].strip()
            
            return followup
            
        except Exception as e:
            # Fallback follow-up questions
            fallbacks = {
                "elaboration": "Could you tell me more about that?",
                "clarification": "Could you explain that in a different way?",
                "redirect": "Going back to my original question, what are your thoughts?"
            }
            return fallbacks.get(followup_type, "Could you elaborate on that?")
    
    async def should_interrupt(
        self,
        answer: str,
        time_remaining: int = 300,
        max_answer_length: int = 500
    ) -> Dict[str, Any]:
        """
        Check if the interview should interrupt the candidate
        
        PURPOSE: Handle edge cases like endless rambling or time running out
        IMPACT: Prevents frustrating experience for both candidate and system
        
        Returns:
            - should_interrupt: boolean
            - reason: "rambling" | "time_running_out" | "off_topic" | "none"
            - message: Polite interruption message
        """
        word_count = len(answer.split())
        
        # Check 1: Time running out
        if time_remaining < 30:
            return {
                "should_interrupt": True,
                "reason": "time_running_out",
                "message": "I need to stop you there as we're running short on time. Let me ask the next question."
            }
        
        # Check 2: Answer is extremely long (likely rambling)
        if word_count > max_answer_length:
            return {
                "should_interrupt": True,
                "reason": "rambling",
                "message": "I appreciate the detail. Let me ask a more specific question..."
            }
        
        # Default: No interruption needed
        return {
            "should_interrupt": False,
            "reason": "none",
            "message": ""
        }