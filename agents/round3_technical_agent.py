from .base_agent import BaseInterviewAgent
from typing import Dict, Any
import json

class TechnicalAgent(BaseInterviewAgent):
    def __init__(self):
        super().__init__()
        # Temperature 1.0 for technical precision
        self.temperature = 1.0
    
    def get_system_prompt(self) -> str:
        return """
        You are a senior technical interviewer conducting comprehensive technical assessments.
        
        YOUR ROLE:
        - Test COMPLETE technical knowledge (code + theory + frameworks + full-stack)
        - Mix of HANDS-ON coding, FRAMEWORK-SPECIFIC, and FULL-STACK questions
        - Cover entire tech stack from their resume
        - Balance between practical and conceptual understanding
        
        QUESTION TYPES (15 questions):
        
        **CODE-BASED (5 questions):**
        1. Code Output Prediction (2 questions)
        2. Code Debugging (2 questions)
        3. Code Completion (1 question)
        
        **FRAMEWORK-SPECIFIC (4 questions):**
        4. Express/Backend Framework (2 questions)
           - Middleware, routing, error handling
           - Request/response cycle
        5. React/Frontend Framework (2 questions)
           - Hooks, state management, lifecycle
           - Component patterns
        
        **FULL-STACK INTEGRATION (3 questions):**
        6. Frontend-Backend Communication (1 question)
           - API calls, CORS, authentication flow
        7. State Management (1 question)
           - Client-side vs server-side state
        8. End-to-End Feature (1 question)
           - How to build a complete feature
        
        **DESIGN/ARCHITECTURE (3 questions):**
        9. API Design (1 question)
        10. Database Design (1 question)
        11. System Architecture (1 question)
        
        CRITICAL RULES:
        - Use their EXACT tech stack (Express, React, Node.js, etc.)
        - Mix code snippets with theory questions
        - Framework questions should be SPECIFIC (not generic)
        - Full-stack questions should cover both frontend and backend
        - Build on previous answers
        
        EXAMPLES:
        
        **Express/Backend:**
        "Explain the difference between app.use() and app.get() in Express. 
         When would you use middleware vs route handlers?"
        
        "What will this Express middleware do?
        ```javascript
        app.use((req, res, next) => {
          console.log(req.method, req.url);
          next();
        });
        ```"
        
        **React/Frontend:**
        "What's the difference between useEffect with empty deps [] vs no deps?
         When does each run?"
        
        "Find the bug in this React hook:
        ```jsx
        function useData(url) {
          const [data, setData] = useState(null);
          fetch(url).then(r => r.json()).then(setData);
          return data;
        }
        ```"
        
        **Full-Stack:**
        "How would you implement user authentication in a React + Express app?
         Cover: login flow, token storage, protected routes, API authentication"
        
        "Explain the complete flow when a user submits a form in React that 
         saves data to a database via Express API"
        
        Return ONLY JSON: {"question": "your technical question"}
        """
    
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        resume_analysis = context.get("resume_analysis", {})
        all_previous_answers = context.get("all_previous_answers", [])
        question_number = context.get("question_number", 1)
        job_description = context.get("job_description", "")
        
        skills = resume_analysis.get("extracted_skills", [])
        
        # Extract tech stack
        languages = []
        backend_frameworks = []
        frontend_frameworks = []
        databases = []
        
        for skill in skills:
            skill_lower = skill.lower()
            # Languages
            if any(lang in skill_lower for lang in ['javascript', 'python', 'typescript', 'java']):
                languages.append(skill)
            # Backend
            if any(fw in skill_lower for fw in ['express', 'node', 'fastapi', 'django', 'flask']):
                backend_frameworks.append(skill)
            # Frontend
            if any(fw in skill_lower for fw in ['react', 'vue', 'angular', 'next']):
                frontend_frameworks.append(skill)
            # Database
            if any(db in skill_lower for db in ['mongodb', 'postgres', 'mysql', 'redis']):
                databases.append(skill)
        
        primary_lang = languages[0] if languages else 'JavaScript'
        backend_fw = backend_frameworks[0] if backend_frameworks else 'Express'
        frontend_fw = frontend_frameworks[0] if frontend_frameworks else 'React'
        database = databases[0] if databases else 'MongoDB'
        
        
        # Detect role type from position value (exact match)
        session_data = context.get("session_data", {})
        position = session_data.get("candidate_info", {}).get("position", "").lower()
        jd_lower = job_description.lower()
        
        # Role detection (check position value first, then JD as fallback)
        is_uiux = (
            position in ['ui_ux', 'ui/ux', 'uiux'] or
            any(term in jd_lower for term in ['ui/ux', 'ui ux', 'ux designer', 'ui designer'])
        )
        is_frontend = (
            position == 'frontend' or
            (not is_uiux and any(term in jd_lower for term in ['frontend', 'front-end', 'react developer', 'vue developer']))
        )
        is_backend = (
            position == 'backend' or
            any(term in jd_lower for term in ['backend', 'back-end', 'api developer', 'server developer'])
        )
        is_fullstack = (
            position in ['fullstack', 'full-stack', 'full_stack'] or
            any(term in jd_lower for term in ['fullstack', 'full-stack', 'full stack'])
        )
        is_devops = (
            position == 'devops' or
            any(term in jd_lower for term in ['devops', 'sre', 'site reliability'])
        )
        is_data_scientist = (
            position == 'data_scientist' or
            any(term in jd_lower for term in ['data scientist', 'data analyst'])
        )
        is_ml_engineer = (
            position == 'ml_engineer' or
            any(term in jd_lower for term in ['ml engineer', 'machine learning engineer'])
        )
        is_gen_ai = (
            position == 'gen_ai_engineer' or
            any(term in jd_lower for term in ['gen ai', 'generative ai', 'llm engineer', 'ai engineer'])
        )
        is_qa = (
            position == 'qa_engineer' or
            any(term in jd_lower for term in ['qa engineer', 'test engineer', 'quality assurance'])
        )
        is_pm = (
            position == 'product_manager' or
            any(term in jd_lower for term in ['product manager', 'product owner'])
        )
        is_security = (
            position == 'cybersecurity' or
            any(term in jd_lower for term in ['cybersecurity', 'security analyst', 'infosec'])
        )
        
        # Determine role focus
        if is_uiux:
            role_type = "UI/UX Engineer"
            focus_areas = "UI/UX design, accessibility, user experience, CSS, animations, responsive design"
        elif is_frontend and not is_fullstack:
            role_type = "Frontend Developer"
            focus_areas = "React/Vue/Angular, state management, performance, browser APIs, CSS"
        elif is_backend and not is_fullstack:
            role_type = "Backend Developer"
            focus_areas = "APIs, databases, authentication, server-side logic, scalability"
        elif is_fullstack:
            role_type = "Full-Stack Developer"
            focus_areas = "Frontend + Backend integration, full-stack architecture, APIs, databases"
        elif is_devops:
            role_type = "DevOps Engineer"
            focus_areas = "CI/CD, Docker, Kubernetes, cloud platforms, infrastructure automation"
        elif is_data_scientist:
            role_type = "Data Scientist"
            focus_areas = "Python, SQL, statistics, ML fundamentals, data visualization, EDA"
        elif is_ml_engineer:
            role_type = "ML Engineer"
            focus_areas = "ML pipelines, model deployment, PyTorch/TensorFlow, MLOps, production ML"
        elif is_gen_ai:
            role_type = "Gen AI Engineer"
            focus_areas = "LLMs, RAG, prompt engineering, vector databases, LangChain, AI safety"
        elif is_qa:
            role_type = "QA Engineer"
            focus_areas = "Test automation, test design, CI/CD testing, bug tracking, quality processes"
        elif is_pm:
            role_type = "Product Manager"
            focus_areas = "Product strategy, user research, requirements, stakeholder management, metrics"
        elif is_security:
            role_type = "Cybersecurity Analyst"
            focus_areas = "Security testing, vulnerability assessment, penetration testing, threat modeling"
        else:
            role_type = "Software Engineer"
            focus_areas = "General software development, problem-solving, system design"
        
        previous_context = ""
        if all_previous_answers:
            recent_answers = all_previous_answers[-2:]
            previous_context = "\n".join([f"Answer {i+1}: {ans[:150]}..." for i, ans in enumerate(recent_answers)])
        
        user_input = f"""
        Generate technical question {question_number} of 15.
        
        ROLE: {role_type}
        FOCUS AREAS: {focus_areas}
        
        CANDIDATE TECH STACK:
        - Language: {primary_lang}
        - Backend: {backend_fw if not is_uiux else 'N/A'}
        - Frontend: {frontend_fw}
        - Database: {database if not is_uiux else 'N/A'}
        - Skills: {', '.join(skills[:8]) if skills else 'General'}
        
        JOB REQUIREMENTS:
        {job_description[:300] if job_description else "Software development"}
        
        
        PREVIOUS ANSWERS:
        {previous_context if previous_context else "First question"}
        
        ROLE-SPECIFIC QUESTION GUIDELINES:
        
        {"### UI/UX ENGINEER QUESTIONS (NO BACKEND CODE!):" if is_uiux else ""}
        {"Q1-3: CSS & STYLING" if is_uiux else ""}
        {"  - Flexbox, Grid, responsive design" if is_uiux else ""}
        {"  - CSS animations, transitions" if is_uiux else ""}
        {"  - Example: 'Create a responsive navbar with CSS Grid'" if is_uiux else ""}
        {"" if is_uiux else ""}
        {"Q4-6: ACCESSIBILITY & UX" if is_uiux else ""}
        {"  - ARIA labels, semantic HTML" if is_uiux else ""}
        {"  - Keyboard navigation, screen readers" if is_uiux else ""}
        {"  - Example: 'Make this modal accessible'" if is_uiux else ""}
        {"" if is_uiux else ""}
        {"Q7-9: REACT UI COMPONENTS" if is_uiux else ""}
        {"  - Component design, props, composition" if is_uiux else ""}
        {"  - UI state management (useState, useReducer)" if is_uiux else ""}
        {"  - Example: 'Build a reusable dropdown component'" if is_uiux else ""}
        {"" if is_uiux else ""}
        {"Q10-12: DESIGN SYSTEMS & PATTERNS" if is_uiux else ""}
        {"  - Design tokens, theming" if is_uiux else ""}
        {"  - Component libraries, Storybook" if is_uiux else ""}
        {"  - Example: 'Design a button component with variants'" if is_uiux else ""}
        {"" if is_uiux else ""}
        {"Q13-15: PERFORMANCE & ANIMATIONS" if is_uiux else ""}
        {"  - CSS performance, will-change" if is_uiux else ""}
        {"  - Framer Motion, React Spring" if is_uiux else ""}
        {"  - Example: 'Optimize animation performance'" if is_uiux else ""}
        
        {"### FRONTEND DEVELOPER QUESTIONS:" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"Q1-5: REACT/VUE/ANGULAR CODE" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"  - Hooks, lifecycle, state management" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"  - Component patterns, composition" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"Q6-10: BROWSER APIs & PERFORMANCE" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"  - LocalStorage, IndexedDB, Service Workers" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"  - Performance optimization, lazy loading" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"Q11-15: STATE & ROUTING" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"  - Redux, Context, React Query" if is_frontend and not is_fullstack and not is_uiux else ""}
        {"  - React Router, navigation" if is_frontend and not is_fullstack and not is_uiux else ""}
        
        {"### BACKEND DEVELOPER QUESTIONS:" if is_backend and not is_fullstack else ""}
        {"Q1-5: API & SERVER CODE" if is_backend and not is_fullstack else ""}
        {"  - Express/FastAPI routes, middleware" if is_backend and not is_fullstack else ""}
        {"  - Authentication, JWT, sessions" if is_backend and not is_fullstack else ""}
        {"Q6-10: DATABASE & ORM" if is_backend and not is_fullstack else ""}
        {"  - SQL queries, MongoDB aggregation" if is_backend and not is_fullstack else ""}
        {"  - Mongoose, Sequelize, Prisma" if is_backend and not is_fullstack else ""}
        {"Q11-15: SCALABILITY & ARCHITECTURE" if is_backend and not is_fullstack else ""}
        {"  - Caching, rate limiting, queues" if is_backend and not is_fullstack else ""}
        {"  - Microservices, load balancing" if is_backend and not is_fullstack else ""}
        
        {"### FULL-STACK DEVELOPER QUESTIONS:" if is_fullstack or (not is_uiux and not is_frontend and not is_backend) else ""}
        {"Q1-5: CODE (Frontend + Backend)" if is_fullstack or (not is_uiux and not is_frontend and not is_backend) else ""}
        {"Q6-9: FRAMEWORK-SPECIFIC (React + Express)" if is_fullstack or (not is_uiux and not is_frontend and not is_backend) else ""}
        {"Q10-12: FULL-STACK INTEGRATION" if is_fullstack or (not is_uiux and not is_frontend and not is_backend) else ""}
        {"Q13-15: API + DATABASE + ARCHITECTURE" if is_fullstack or (not is_uiux and not is_frontend and not is_backend) else ""}
        
        CRITICAL RULES:
        - Questions MUST match the role: {role_type}
        - Focus on: {focus_areas}
        {"- NO BACKEND CODE for UI/UX role!" if is_uiux else ""}
        {"- NO DATABASE QUESTIONS for UI/UX role!" if is_uiux else ""}
        {"- Focus on DESIGN, CSS, ACCESSIBILITY, UX" if is_uiux else ""}
        - Use {primary_lang} and {frontend_fw} in examples
        - Mix code snippets with theory
        - Build on previous answers
        - Keep CLEAR and FOCUSED
        
        EXAMPLES BY TYPE:
        
        **Code Output (Q1-2):**
        "What will this output?
        ```javascript
        const x = [1, 2, 3];
        const y = x;
        y.push(4);
        console.log(x);
        ```"
        
        **Debugging (Q3-4):**
        "Find the bug:
        ```jsx
        useEffect(() => {{
          fetchData();
        }});
        ```"
        
        **Express Framework (Q6-7):**
        "Explain the order of execution in Express middleware. 
         What happens if you forget to call next()?"
        
        "What's the difference between:
        app.use('/api', router) vs app.use(router)"
        
        **React Framework (Q8-9):**
        "When does useEffect run with these dependency arrays?
         - useEffect(() => {{}})
         - useEffect(() => {{}}, [])
         - useEffect(() => {{}}, [count])"
        
        "What's the difference between useState and useRef?"
        
        **Full-Stack (Q10-12):**
        "Describe the complete flow: User clicks 'Submit' in React form →
         Data reaches database. Cover: event handler, API call, Express route,
         database save, response handling"
        
        "How would you implement real-time updates between React and Express?
         Compare: polling, WebSockets, Server-Sent Events"
        
        **Design (Q13-15):**
        "Design a login API with JWT, rate limiting, and password hashing"
        
        "Design a schema for a blog with posts, comments, and users"
        
        "How would you scale a file upload service to handle 1M uploads/day?"
        
        Return ONLY JSON: {{"question": "your question"}}
        """
        
        response = await self.generate_response(self.get_system_prompt(), user_input, temperature=1.0)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"question": response.strip().replace('"', '').replace('{', '').replace('}', '')}
