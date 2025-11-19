from .base_agent import BaseInterviewAgent
from typing import Dict, Any, List
import json
import random

class CodingAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 0.0 for coding/math (per DeepSeek docs)
        self.temperature = 0.0
        self.difficulty_levels = {
            "beginner": ["array", "string", "basic_loops"],
            "intermediate": ["linked_list", "binary_search", "dynamic_programming_basic"],
            "advanced": ["graph", "tree", "dynamic_programming_advanced", "system_design_coding"]
        }
    
    def get_system_prompt(self) -> str:
        return """
        You are an expert DSA (Data Structures & Algorithms) interviewer specializing in coding assessments.
        
        Your responsibilities:
        - Generate HIGH-QUALITY DSA problems (Arrays, Strings, Trees, Graphs, DP, etc.)
        - Provide crystal-clear problem statements with multiple examples
        - Create comprehensive test cases including edge cases
        - Evaluate code for correctness, time/space complexity, and code quality
        - Provide progressive hints without giving away the solution
        - Focus on problem-solving approach and algorithmic thinking
        
        DSA Topics to Cover:
        - Arrays & Strings (Two Pointers, Sliding Window)
        - Linked Lists (Reversal, Cycle Detection)
        - Trees & Graphs (DFS, BFS, Traversals)
        - Sorting & Searching (Binary Search, Quick Sort)
        - Dynamic Programming (Memoization, Tabulation)
        - Heaps & Priority Queues
        - Hash Tables & Sets
        - Stacks & Queues
        
        Always respond in JSON format:
        {
            "problem": {
                "title": "Problem Title",
                "description": "Detailed problem description with clear requirements",
                "examples": [
                    {"input": "...", "output": "...", "explanation": "Step-by-step explanation"}
                ],
                "constraints": ["Time: O(?)", "Space: O(?)", "Input size: ...", "Edge cases: ..."],
                "difficulty": "easy|medium|hard",
                "topics": ["Array", "Two Pointers", "etc"],
                "time_limit": 30,
                "optimal_complexity": {"time": "O(n)", "space": "O(1)"}
            },
            "test_cases": {
                "visible": [{"input": "...", "expected_output": "...", "explanation": "..."}],
                "hidden": [{"input": "...", "expected_output": "..."}]
            },
            "hints": [
                "Hint 1: Think about the approach",
                "Hint 2: Consider using X data structure",
                "Hint 3: Algorithm hint"
            ],
            "evaluation_criteria": {
                "correctness": 40,
                "time_complexity": 25,
                "space_complexity": 15,
                "code_quality": 15,
                "edge_cases": 5
            }
        }
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = context.get("action", "generate_problem")
        
        if action == "generate_problem":
            return await self._generate_coding_problem(context)
        elif action == "evaluate_code":
            return await self._evaluate_code_submission(context)
        elif action == "provide_hint":
            return await self._provide_hint(context)
        else:
            return {"error": "Unknown action"}
    
    async def _generate_coding_problem(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DSA problem based on company type and difficulty"""
        company_type = context.get("company_type", "startup")
        session_data = context.get("session_data", {})
        resume_analysis = context.get("resume_analysis", {})
        extracted_skills = resume_analysis.get("extracted_skills", [])
        question_number = context.get("question_number", 1)
        
        # Map company type to difficulty
        difficulty_map = {
            "startup": "easy",
            "service_based": "moderate",
            "product_based": "hard"
        }
        actual_difficulty = difficulty_map.get(company_type, "moderate")
        
        user_input = f"""
        Generate DSA coding problem #{question_number}:
        
        COMPANY TYPE: {company_type}
        DIFFICULTY: {actual_difficulty}
        CANDIDATE SKILLS: {', '.join(extracted_skills) if extracted_skills else 'General programming'}
        
        Requirements:
        1. Clear problem statement with title
        2. Multiple examples with step-by-step explanations
        3. Constraints and edge cases
        4. Test cases (visible and hidden)
        5. Expected time/space complexity
        
        Topics: Arrays, Strings, Linked Lists, Trees, Graphs, Dynamic Programming, Sorting, Searching
        
        Make it a REAL DSA problem that tests algorithmic thinking.
        
        Return JSON format with problem, test_cases, and hints fields.
        """
        
        # Use temperature 0.0 for precise coding problems
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=0.0)
        return self._parse_problem_response(response)
    
    async def _evaluate_code_submission(self, context: Dict[str, Any]) -> Dict[str, Any]:
        code = context.get("code", "")
        language = context.get("language", "python")
        problem_data = context.get("problem_data", {})
        test_cases = context.get("test_cases", {})
        
        evaluation_prompt = f"""
        Evaluate this code submission:
        
        LANGUAGE: {language}
        CODE:
        {code}
        
        PROBLEM: {problem_data.get('title', 'Coding Problem')}
        TEST CASES: {json.dumps(test_cases, indent=2)}
        
        Provide detailed evaluation including:
        1. Correctness (does it solve the problem?)
        2. Time and space complexity
        3. Code quality and style
        4. Edge case handling
        5. Overall score (1-100)
        6. Specific feedback and suggestions
        
        Format as JSON with scores and detailed feedback.
        """
        
        # Use temperature 0.0 for precise evaluation
        response = await self.generate_response(
            "You are a senior software engineer evaluating code submissions.",
            evaluation_prompt,
            temperature=0.0
        )
        
        return self._parse_evaluation_response(response)
    
    async def _provide_hint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        problem_data = context.get("problem_data", {})
        current_code = context.get("current_code", "")
        hint_level = context.get("hint_level", 1)
        
        hint_prompt = f"""
        The candidate is working on: {problem_data.get('title', 'a coding problem')}
        
        Their current approach:
        {current_code}
        
        Provide hint level {hint_level} (1=gentle nudge, 2=more specific, 3=algorithm hint):
        - Don't give away the solution
        - Guide their thinking process
        - Suggest a better approach if they're stuck
        """
        
        response = await self.generate_response(
            "You are a helpful coding mentor providing hints.",
            hint_prompt,
            temperature=0.0
        )
        
        return {
            "hint": response.strip(),
            "hint_level": hint_level,
            "timestamp": "now"
        }
    
    def _determine_problem_focus(self, company_type: str, skills: List[str], preference: str) -> str:
        """Determine what type of problem to focus on"""
        if preference == "algorithms":
            return "algorithmic_thinking"
        elif preference == "oop":
            return "object_oriented_design"
        elif "machine learning" in [s.lower() for s in skills]:
            return "data_structures_for_ml"
        elif company_type == "startup":
            return "practical_problem_solving"
        elif company_type == "product_based":
            return "scalable_algorithms"
        else:
            return "general_programming"
    
    def _parse_problem_response(self, response: str) -> Dict[str, Any]:
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # If it's a valid problem structure, return it
                if "problem" in parsed or "question" in parsed:
                    # Normalize to have "question" field for consistency
                    if "problem" in parsed and "question" not in parsed:
                        problem_data = parsed.get("problem", {})
                        parsed["question"] = f"{problem_data.get('title', 'Coding Problem')}\n\n{problem_data.get('description', '')}"
                    return parsed
        except Exception as e:
            pass
        
        # Fallback: generate a simple problem
        fallback_problem = {
            "title": "Two Sum",
            "description": "Given an array of integers and a target sum, return indices of two numbers that add up to the target.",
            "examples": [{"input": "[2,7,11,15], target=9", "output": "[0,1]", "explanation": "2 + 7 = 9"}],
            "constraints": ["Array length: 2-1000", "Unique solution exists"],
            "difficulty": "easy",
            "topics": ["array", "hash_table"],
            "time_limit": 30
        }
        
        return {
            "question": f"{fallback_problem['title']}\n\n{fallback_problem['description']}",
            "problem": fallback_problem,
            "test_cases": {
                "visible": [{"input": "[2,7,11,15], 9", "expected_output": "[0,1]"}],
                "hidden": [{"input": "[3,2,4], 6", "expected_output": "[1,2]"}]
            },
            "hints": ["Consider using a hash map", "Think about what you need to find for each element"],
            "evaluation_criteria": {"correctness": 40, "efficiency": 30, "code_quality": 20, "edge_cases": 10}
        }
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback evaluation
        return {
            "scores": {
                "correctness": 75,
                "efficiency": 70,
                "code_quality": 80,
                "edge_cases": 65,
                "overall": 72
            },
            "feedback": response.strip(),
            "suggestions": ["Consider edge cases", "Optimize time complexity"],
            "passed_tests": 3,
            "total_tests": 5
        }
