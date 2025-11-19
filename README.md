# 🎙️ Xalora AI Voice Interview System

An intelligent AI-powered interview system with voice capabilities, adaptive questioning, and comprehensive candidate evaluation.

## ✨ Features

### 🎯 Core Features
- **Resume-Based Adaptive Questioning**: Every question is tailored based on candidate's resume and previous answers
- **Voice-Enabled Interviews**: Text-to-Speech for questions and Speech-to-Text for answers
- **5-Minute Timer**: Auto-advance to next question when time expires
- **Audio-First Experience**: Questions play as audio before displaying text
- **Multiple Interview Rounds**: 
  - Resume Analysis
  - Formal Q&A (20 questions)
  - Coding/DSA (10 problems)
  - Technical Deep Dive (50 questions)
  - Behavioral Assessment (20 questions)
  - System Design (20 questions)
- **Comprehensive Final Report**: Detailed analysis with strengths, weaknesses, and recommendations
- **Flexible Modes**: Full interview or practice specific rounds

### 🎙️ Voice Features
- **Text-to-Speech (TTS)**: Gemini 2.5 Flash with 4 distinct voices
- **Speech-to-Text (STT)**: Real-time transcription using Gemini
- **Auto-Play**: Questions play automatically (with fallback manual play)
- **Voice Variety**: Different voices for different interview rounds

### ⏱️ Timer Features
- **5-Minute Countdown**: Per question timer with visual display
- **Color-Coded Warnings**: Blue → Orange → Red as time runs out
- **Auto-Submit**: Automatically moves to next question when time expires
- **No Pressure**: System handles timeout gracefully

### 🤖 AI-Powered
- **DeepSeek R1**: Advanced reasoning for question generation and evaluation
- **Gemini 2.5 Flash**: Voice synthesis and speech recognition
- **Context-Aware**: Each question considers resume and all previous answers
- **Adaptive Difficulty**: Adjusts based on company type (Startup/Service/Product)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- DeepSeek API Key
- Gemini API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/xalora-ai-interview.git
cd xalora-ai-interview
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Keys**

Create a `.env` file in the root directory:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:8000
```

## 📖 Usage Guide

### Step 1: Candidate Information
- Fill in personal details (name, age, gender, experience)
- Upload resume (PDF format)
- Provide job description
- Select company type (affects DSA difficulty)
- Choose interview mode (Full or Practice)

### Step 2: Enable Audio
- Click "Enable Audio 🔊" button
- This allows automatic playback of questions

### Step 3: Select Round
Choose from available rounds:
- **Formal Q&A** 🎙️ - Professional interview questions
- **Coding** 💻 - DSA problems (text-only)
- **Technical** 🎙️ - Deep technical questions
- **Behavioral** 🎙️ - Situational and behavioral questions
- **System Design** 🎙️ - Architecture and design questions

### Step 4: Answer Questions
1. **Listen** to the question (audio plays first)
2. **Read** the text (appears after audio)
3. **Watch** the timer (5 minutes countdown)
4. **Record** your answer using the microphone
5. **Review** the transcript
6. **Submit** or wait for auto-submit

### Step 5: Generate Report
- Complete desired rounds
- Click "Generate Final Report"
- View comprehensive analysis

## 🎨 User Interface

### Question Display
```
┌─────────────────────────────────────────┐
│ Question 1 / 20          ⏱️ 5:00       │
├─────────────────────────────────────────┤
│                                         │
│  [Question text appears here]           │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔊 Listen to the question:              │
│ [Audio Player Controls]                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        Click microphone to answer       │
│              🎤                          │
│        Speak your answer clearly        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Your Answer:                            │
│ [Transcript appears here...]            │
└─────────────────────────────────────────┘
```

### Timer Behavior
- **5:00 - 2:01**: 🔵 Blue (plenty of time)
- **2:00 - 1:01**: 🟠 Orange (warning)
- **1:00 - 0:00**: 🔴 Red (urgent)
- **0:00**: Auto-submits and moves to next question

## 🏗️ Architecture

### Project Structure
```
xalora-ai-interview/
├── app.py                      # Main FastAPI application
├── voice_service.py            # Voice TTS/STT service
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not in repo)
├── .gitignore                  # Git ignore rules
├── run.bat                     # Windows run script
├── test_system.py              # System test script
│
├── agents/                     # AI interview agents
│   ├── base_agent.py          # Base agent class
│   ├── round0_resume_agent.py # Resume analysis
│   ├── round1_formal_qa_agent.py
│   ├── round2_coding_agent.py
│   ├── round3_technical_agent.py
│   ├── round4_behavioral_agent.py
│   └── round5_system_design_agent.py
│
├── static/                     # Frontend files
│   ├── voice_interface.html   # Main UI
│   ├── voice_interview.js     # JavaScript logic
│   └── index.html             # Text-only interface
│
├── database/                   # Session storage
├── cache/                      # Response cache
└── voices/                     # Voice samples (optional)
```

### Technology Stack

**Backend:**
- FastAPI - Web framework
- Python 3.8+ - Programming language
- DeepSeek R1 - Question generation & evaluation
- Gemini 2.5 Flash - Voice synthesis & recognition

**Frontend:**
- HTML5 - Structure
- CSS3 - Styling
- Vanilla JavaScript - Interactivity
- Web Audio API - Audio playback
- MediaRecorder API - Voice recording

**AI Services:**
- DeepSeek API - Advanced reasoning
- Gemini API - Voice capabilities

## 🔧 Configuration

### Voice Configuration
Edit `voice_service.py` to customize voices:
```python
self.voice_configs = {
    "formal_qa": {"voice": "Kore", "style": "professional"},
    "technical": {"voice": "Iapetus", "style": "expert"},
    "behavioral": {"voice": "Aoede", "style": "empathetic"},
    "system_design": {"voice": "Charon", "style": "analytical"}
}
```

### Timer Configuration
Edit `static/voice_interview.js` to adjust timer:
```javascript
let questionTimeRemaining = 300; // 5 minutes in seconds
```

### Company Types & DSA Difficulty
- **Startup**: Easy DSA (Arrays, Strings, Basic Loops)
- **Service Based**: Medium DSA (Trees, Graphs, Basic DP)
- **Product Based**: Hard DSA (Advanced DP, Complex Algorithms)

## 📊 Interview Rounds

### 1. Resume Analysis (Round 0)
- Extracts skills, experience, and key information
- Analyzes strengths and areas for improvement
- Sets context for all subsequent questions

### 2. Formal Q&A (Round 1)
- 20 professional interview questions
- Voice-enabled
- Based on resume and job description
- Covers background, experience, and motivation

### 3. Coding/DSA (Round 2)
- 10 coding problems
- Text-only (code editor)
- Difficulty based on company type
- Pass/Fail evaluation with detailed feedback

### 4. Technical Deep Dive (Round 3)
- 50 technical questions
- Voice-enabled
- Covers technologies from resume
- In-depth technical knowledge assessment

### 5. Behavioral Assessment (Round 4)
- 20 behavioral questions
- Voice-enabled
- STAR method encouraged
- Evaluates soft skills and cultural fit

### 6. System Design (Round 5)
- 20 system design questions
- Voice-enabled
- Architecture and scalability focus
- Real-world problem-solving

## 🎯 Evaluation Criteria

### Question Generation
- Resume-based context
- Previous answer analysis
- Progressive difficulty
- Job description alignment

### Final Report Includes
- **Overall Performance**: Comprehensive summary
- **Round-by-Round Analysis**: Detailed breakdown
- **Strengths**: Key positive points
- **Areas for Improvement**: Constructive feedback
- **Technical Skills**: Assessment of technical knowledge
- **Communication**: Clarity and articulation
- **Problem-Solving**: Analytical thinking
- **Recommendations**: Next steps and suggestions

## 🐛 Troubleshooting

### Audio Not Playing
1. Click "Enable Audio 🔊" button first
2. Check browser audio permissions
3. Try manual play button
4. Use Chrome/Edge for best compatibility

### Microphone Not Working
1. Allow microphone permission in browser
2. Check system microphone settings
3. Try different browser
4. Verify microphone is not used by another app

### Timer Not Showing
1. Refresh the page
2. Check browser console (F12) for errors
3. Ensure JavaScript is enabled

### API Errors
1. Verify API keys in `.env` file
2. Check API key validity
3. Ensure sufficient API credits
4. Check internet connection

### Resume Upload Issues
1. Ensure PDF format
2. Check file size (< 10MB recommended)
3. Verify PDF is not password-protected
4. Try different PDF

## 🔒 Security & Privacy

- API keys stored in `.env` (not committed to repo)
- Session data stored locally
- No data sent to external servers (except AI APIs)
- Resume data processed in-memory
- Interview reports saved locally

## 📝 API Endpoints

### Main Endpoints
- `GET /` - Voice interface
- `GET /text` - Text-only interface
- `POST /api/start-interview` - Initialize interview session
- `POST /api/get-question` - Get next question
- `POST /api/submit-answer` - Submit answer
- `POST /api/text-to-speech` - Generate audio for question
- `POST /api/speech-to-text` - Transcribe audio answer
- `POST /api/final-report` - Generate comprehensive report

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (with Uvicorn)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- DeepSeek for advanced AI reasoning
- Google Gemini for voice capabilities
- FastAPI for the excellent web framework
- All contributors and testers

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🎉 Features Roadmap

- [ ] Multi-language support
- [ ] Video interview capability
- [ ] Real-time feedback during answers
- [ ] Interview analytics dashboard
- [ ] Custom question banks
- [ ] Interview scheduling
- [ ] Candidate comparison reports
- [ ] Mobile app version

---

**Made with ❤️ for better interviews**

**Version**: 1.0.0  
**Last Updated**: November 2025
