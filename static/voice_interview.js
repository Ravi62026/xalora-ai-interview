// Voice Interview System JavaScript
let sessionId = null;
let currentRound = null;
let questionCount = 0;
let maxQuestions = 0;
let interviewMode = null;
let currentQuestionData = null;
let selectedCodingDifficulty = 'medium';

// Voice recording variables
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentTranscript = '';
let audioEnabled = false;

// Timer variables
let questionTimer = null;
let questionTimeRemaining = 300; // 5 minutes in seconds
let questionStartTime = null;

// Initialize
document.getElementById('resumeFile').addEventListener('change', function(e) {
    document.getElementById('fileName').textContent = `Selected: ${e.target.files[0]?.name}`;
});

document.getElementById('candidateForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('age', document.getElementById('age').value);
    formData.append('gender', document.getElementById('gender').value);
    formData.append('experience', document.getElementById('experience').value);
    formData.append('job_description', document.getElementById('jobDescription').value);
    formData.append('company_type', document.getElementById('companyType').value);
    formData.append('interview_mode', document.getElementById('interviewMode').value);
    formData.append('resume_file', document.getElementById('resumeFile').files[0]);

    interviewMode = document.getElementById('interviewMode').value;

    try {
        const response = await fetch('/api/start-interview', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            sessionId = data.session_id;
            const analysis = data.resume_analysis;
            document.getElementById('analysisResult').innerHTML = `
                <h3>✅ Resume Analyzed!</h3>
                <p><strong>Skills:</strong> ${analysis.extracted_skills?.join(', ') || 'N/A'}</p>
            `;
            document.getElementById('analysisResult').style.display = 'block';
            
            const modeMsg = document.getElementById('modeMessage');
            if (interviewMode === 'full') {
                modeMsg.innerHTML = '<strong>📝 Full Interview Mode:</strong> Complete any rounds you want. Voice-enabled for all rounds except coding.';
            } else {
                modeMsg.innerHTML = '<strong>🎯 Practice Mode:</strong> Choose any round to practice. Voice-enabled for interactive rounds.';
            }
            
            showSection('section-rounds');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

function showCodingDifficulty() {
    document.getElementById('codingDifficultySection').style.display = 'block';
}

function hideCodingDifficulty() {
    document.getElementById('codingDifficultySection').style.display = 'none';
}

function startCodingRound() {
    selectedCodingDifficulty = document.getElementById('codingDifficulty').value;
    hideCodingDifficulty();
    selectRound('coding', 10);
}

async function selectRound(round, count) {
    currentRound = round;
    maxQuestions = count;
    questionCount = 0;
    showSection('section-interview');
    
    // Show/hide voice interface based on round
    const voiceContainer = document.getElementById('voiceContainer');
    const transcriptBox = document.getElementById('transcriptBox');
    
    if (round === 'coding') {
        // Coding round: text only
        voiceContainer.style.display = 'none';
        transcriptBox.innerHTML = `
            <strong>Your Code:</strong>
            <textarea id="codeInput" style="width: 100%; min-height: 200px; margin-top: 10px; padding: 10px; font-family: monospace;"></textarea>
        `;
    } else {
        // Voice-enabled rounds
        voiceContainer.style.display = 'block';
        transcriptBox.innerHTML = `
            <strong>Your Answer:</strong>
            <p id="transcriptText" style="margin-top: 10px; color: #666;">Your speech will appear here...</p>
        `;
        
        // Enable audio auto-play by creating a user interaction
        // This is required by browsers to allow auto-play
        const audioElement = document.getElementById('questionAudio');
        if (audioElement) {
            // Unmute and prepare for auto-play
            audioElement.muted = false;
            audioElement.volume = 1.0;
        }
    }
    
    await getNextQuestion();
}

async function skipRound() {
    if (confirm('Are you sure you want to skip this round?')) {
        showSection('section-rounds');
    }
}

async function getNextQuestion() {
    if (questionCount >= maxQuestions) {
        stopQuestionTimer();
        alert('Round complete! You can select another round or generate final report.');
        showSection('section-rounds');
        return;
    }

    try {
        console.log('Getting next question...');
        
        // Hide question text initially (will show after audio plays)
        const questionTextEl = document.getElementById('questionText');
        questionTextEl.textContent = '🔊 Loading audio...';
        questionTextEl.style.opacity = '0.5';
        
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('round_type', currentRound);
        formData.append('question_count', maxQuestions);
        
        if (currentRound === 'coding') {
            formData.append('coding_difficulty', selectedCodingDifficulty);
        }

        const response = await fetch('/api/get-question', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            questionCount = data.question_number;
            currentQuestionData = data.question_data;
            
            document.getElementById('qNum').textContent = questionCount;
            document.getElementById('qTotal').textContent = maxQuestions;
            
            const progress = (questionCount / maxQuestions) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            
            // Reset transcript
            currentTranscript = '';
            const transcriptText = document.getElementById('transcriptText');
            if (transcriptText) {
                transcriptText.textContent = 'Your speech will appear here...';
                transcriptText.style.color = '#666';
            }
            document.getElementById('submitBtn').disabled = true;
            
            // Convert question to speech for voice-enabled rounds
            if (currentRound !== 'coding') {
                console.log('Voice-enabled round, converting to speech...');
                // Play audio first, then show text
                await playQuestionAudio(data.question, currentRound);
                
                // Show question text after audio starts
                setTimeout(() => {
                    questionTextEl.textContent = data.question;
                    questionTextEl.style.opacity = '1';
                    
                    // Start 5-minute timer
                    startQuestionTimer();
                }, 1000);
            } else {
                console.log('Coding round, no voice');
                questionTextEl.textContent = data.question;
                questionTextEl.style.opacity = '1';
                const audioPlayer = document.getElementById('audioPlayer');
                if (audioPlayer) {
                    audioPlayer.classList.remove('active');
                }
                
                // Start 5-minute timer for coding too
                startQuestionTimer();
            }
        }
    } catch (error) {
        console.error('Error getting question:', error);
        alert('Error: ' + error.message);
    }
}

function startQuestionTimer() {
    // Clear any existing timer
    stopQuestionTimer();
    
    // Reset timer
    questionTimeRemaining = 300; // 5 minutes
    questionStartTime = Date.now();
    
    // Update timer display
    updateTimerDisplay();
    
    // Start countdown
    questionTimer = setInterval(() => {
        questionTimeRemaining--;
        updateTimerDisplay();
        
        // Auto-submit when time runs out
        if (questionTimeRemaining <= 0) {
            stopQuestionTimer();
            alert('⏰ Time is up! Moving to next question...');
            autoSubmitAnswer();
        }
    }, 1000);
}

function stopQuestionTimer() {
    if (questionTimer) {
        clearInterval(questionTimer);
        questionTimer = null;
    }
}

function updateTimerDisplay() {
    const minutes = Math.floor(questionTimeRemaining / 60);
    const seconds = questionTimeRemaining % 60;
    const timerText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    // Update timer in UI (we'll add this element)
    const timerEl = document.getElementById('questionTimer');
    if (timerEl) {
        timerEl.textContent = timerText;
        
        // Change color when time is running out
        if (questionTimeRemaining <= 60) {
            timerEl.style.color = '#f5576c';
        } else if (questionTimeRemaining <= 120) {
            timerEl.style.color = '#ff9800';
        } else {
            timerEl.style.color = '#667eea';
        }
    }
}

async function autoSubmitAnswer() {
    let answer = '';
    
    if (currentRound === 'coding') {
        const codeInput = document.getElementById('codeInput');
        answer = codeInput ? codeInput.value.trim() : '';
    } else {
        answer = currentTranscript.trim();
    }
    
    // Submit even if empty (time ran out)
    if (!answer) {
        answer = '[No answer provided - time expired]';
    }
    
    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('round_type', currentRound);
        formData.append('answer', answer);

        const response = await fetch('/api/submit-answer', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            currentTranscript = '';
            await getNextQuestion();
        }
    } catch (error) {
        console.error('Auto-submit error:', error);
        await getNextQuestion(); // Move on anyway
    }
}

async function playQuestionAudio(text, roundType) {
    try {
        console.log('🔊 Converting question to speech...');
        const formData = new FormData();
        formData.append('text', text);
        formData.append('round_type', roundType);
        
        const response = await fetch('/api/text-to-speech', { method: 'POST', body: formData });
        const data = await response.json();
        
        console.log('TTS Response:', data.success);
        
        if (data.success && data.audio_data) {
            console.log('✅ Audio data received, size:', data.audio_data.length);
            console.log('📋 MIME type:', data.mime_type || 'audio/wav');
            
            const audioPlayer = document.getElementById('audioPlayer');
            const audioElement = document.getElementById('questionAudio');
            
            if (!audioElement) {
                console.error('❌ Audio element not found!');
                return;
            }
            
            // Use data URL - simpler and more compatible than blob
            const mimeType = data.mime_type || 'audio/wav';
            const dataUrl = `data:${mimeType};base64,${data.audio_data}`;
            
            console.log('🎵 Using data URL with MIME:', mimeType);
            console.log('🎵 Data URL length:', dataUrl.length);
            
            // Set audio source
            audioElement.src = dataUrl;
            audioPlayer.classList.add('active');
            
            // Wait for audio to be ready with timeout
            await new Promise((resolve) => {
                const timeout = setTimeout(() => {
                    console.warn('⚠️ Audio load timeout');
                    resolve();
                }, 5000);
                
                audioElement.onloadeddata = () => {
                    clearTimeout(timeout);
                    console.log('✅ Audio loaded, duration:', audioElement.duration);
                    if (audioElement.duration && audioElement.duration > 0) {
                        console.log('✅ Audio is valid and playable');
                    } else {
                        console.warn('⚠️ Audio duration is 0 or NaN');
                    }
                    resolve();
                };
                
                audioElement.onerror = (e) => {
                    clearTimeout(timeout);
                    console.error('❌ Audio load error:', e);
                    console.error('   Error details:', audioElement.error);
                    resolve();
                };
            });
            
            // Try to play
            console.log('▶️ Attempting to play audio...');
            try {
                await audioElement.play();
                console.log('✅ Audio playing!');
                
                const voiceStatus = document.getElementById('voiceStatus');
                if (voiceStatus) {
                    voiceStatus.textContent = '🔊 Question is playing...';
                    voiceStatus.style.color = '#28a745';
                }
            } catch (playError) {
                console.warn('⚠️ Auto-play blocked:', playError.message);
                
                const voiceStatus = document.getElementById('voiceStatus');
                if (voiceStatus) {
                    voiceStatus.innerHTML = '▶️ <button onclick="document.getElementById(\'questionAudio\').play()" style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 14px;">▶️ Click to Play Audio</button>';
                }
            }
        } else {
            console.log('❌ TTS failed:', data.message || 'Unknown error');
            const voiceStatus = document.getElementById('voiceStatus');
            
            // Show friendly message if quota exceeded
            if (data.quota_exceeded) {
                if (voiceStatus) {
                    voiceStatus.innerHTML = '📖 <strong>TTS quota reached.</strong> Please read the question above and answer using the microphone below.';
                    voiceStatus.style.color = '#ff9800';
                    voiceStatus.style.fontSize = '16px';
                }
                // Hide audio player
                const audioPlayer = document.getElementById('audioPlayer');
                if (audioPlayer) {
                    audioPlayer.classList.remove('active');
                }
            } else {
                if (voiceStatus) {
                    voiceStatus.textContent = '❌ Voice not available for this round';
                    voiceStatus.style.color = '#dc3545';
                }
            }
        }
    } catch (error) {
        console.error('❌ TTS Error:', error);
    }
}

function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
}

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await transcribeAudio(audioBlob);
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        const voiceButton = document.getElementById('voiceButton');
        const voiceStatus = document.getElementById('voiceStatus');
        voiceButton.classList.add('recording');
        voiceButton.textContent = '⏹️';
        voiceStatus.textContent = 'Recording... Click to stop';
        voiceStatus.style.color = '#f5576c';
        
    } catch (error) {
        alert('Microphone access denied. Please allow microphone access to use voice input.');
        console.error('Recording error:', error);
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        const voiceButton = document.getElementById('voiceButton');
        const voiceStatus = document.getElementById('voiceStatus');
        voiceButton.classList.remove('recording');
        voiceButton.textContent = '🎤';
        voiceStatus.textContent = 'Processing your speech...';
        voiceStatus.style.color = '#667eea';
    }
}

async function transcribeAudio(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        
        const response = await fetch('/api/speech-to-text', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            currentTranscript = data.transcript;
            
            // Update UI
            const transcriptText = document.getElementById('transcriptText');
            transcriptText.textContent = currentTranscript;
            transcriptText.style.color = '#333';
            
            const voiceStatus = document.getElementById('voiceStatus');
            voiceStatus.textContent = 'Speech recognized! Review and submit';
            voiceStatus.style.color = '#28a745';
            
            // Enable submit button
            document.getElementById('submitBtn').disabled = false;
        } else {
            alert('Speech recognition failed. Please try again.');
            const voiceStatus = document.getElementById('voiceStatus');
            voiceStatus.textContent = 'Click the microphone to answer';
            voiceStatus.style.color = '#667eea';
        }
    } catch (error) {
        alert('Error transcribing audio: ' + error.message);
        console.error('Transcription error:', error);
    }
}

async function submitVoiceAnswer() {
    let answer = '';
    
    if (currentRound === 'coding') {
        // Get code from textarea
        const codeInput = document.getElementById('codeInput');
        answer = codeInput ? codeInput.value.trim() : '';
    } else {
        // Get transcript
        answer = currentTranscript.trim();
    }
    
    if (!answer) {
        alert('Please provide an answer');
        return;
    }

    try {
        // Stop timer
        stopQuestionTimer();
        
        // Store answer
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('round_type', currentRound);
        formData.append('answer', answer);

        const response = await fetch('/api/submit-answer', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            // Reset for next question
            currentTranscript = '';
            await getNextQuestion();
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function completeRound() {
    if (confirm('Complete this round and return to round selection?')) {
        showSection('section-rounds');
    }
}

async function generateFinalReport() {
    if (confirm('Generate final report for all completed rounds?')) {
        await generateReport();
    }
}

async function generateReport() {
    showSection('section-report');
    document.getElementById('reportContent').textContent = 'Generating comprehensive report for all completed rounds...';

    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);

        const response = await fetch('/api/final-report', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            const report = data.report;
            document.getElementById('reportContent').textContent = report.comprehensive_analysis;
        }
    } catch (error) {
        document.getElementById('reportContent').textContent = 'Error generating report: ' + error.message;
    }
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    
    // Show audio enable prompt for rounds section
    if (sectionId === 'section-rounds' && !audioEnabled) {
        const prompt = document.getElementById('audioEnablePrompt');
        if (prompt) {
            prompt.style.display = 'block';
        }
    }
}

function enableAudio() {
    // Create a silent audio element and play it to enable auto-play
    const audio = new Audio();
    audio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA';
    audio.play().then(() => {
        audioEnabled = true;
        const prompt = document.getElementById('audioEnablePrompt');
        if (prompt) {
            prompt.style.display = 'none';
        }
        alert('✅ Audio enabled! Questions will now play automatically.');
    }).catch(err => {
        console.error('Failed to enable audio:', err);
        alert('⚠️ Could not enable audio. You may need to click play manually.');
    });
}
