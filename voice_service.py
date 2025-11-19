"""
Voice Service for Gemini TTS and STT
Handles text-to-speech and speech-to-text using Gemini 2.5
"""
import os
import wave
import base64
from typing import Dict, Any
import tempfile
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-genai not installed. Voice features will be disabled.")

load_dotenv()

class VoiceService:
    def __init__(self):
        """Initialize Gemini client for voice services"""
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai package not installed. Install with: pip install google-genai")
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        gemini_key = gemini_key.strip('"').strip("'")
        
        # Use new google-genai API
        self.client = genai.Client(api_key=gemini_key)
        self.client_type = "new"
        
        # Voice configurations for different rounds
        self.voice_configs = {
            "formal_qa": {
                "voice": "Kore",  # Firm, professional
                "style": "warm and friendly HR professional"
            },
            "coding": None,  # Coding round is text-only
            "technical": {
                "voice": "Iapetus",  # Clear, informative
                "style": "knowledgeable technical expert"
            },
            "behavioral": {
                "voice": "Aoede",  # Breezy, conversational
                "style": "empathetic and understanding"
            },
            "system_design": {
                "voice": "Charon",  # Informative, analytical
                "style": "thoughtful system architect"
            }
        }
    
    def text_to_speech(self, text: str, round_type: str = "formal_qa") -> Dict[str, Any]:
        """
        Convert text to speech using Gemini TTS
        
        Args:
            text: Text to convert to speech
            round_type: Type of interview round (determines voice)
        
        Returns:
            Dict with audio data and metadata
        """
        try:
            # Get voice config for this round
            voice_config = self.voice_configs.get(round_type)
            
            if not voice_config:
                # Coding round or unknown - return text only
                return {
                    "success": False,
                    "text": text,
                    "audio_data": None,
                    "message": "Voice not available for this round"
                }
            
            # Create prompt with style guidance
            prompt = f"Say in a {voice_config['style']} tone: {text}"
            
            # Use new google-genai API
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_config['voice']
                            )
                        )
                    )
                )
            )
            
            # Extract audio data
            inline_data = response.candidates[0].content.parts[0].inline_data
            audio_data = inline_data.data
            mime_type = inline_data.mime_type if hasattr(inline_data, 'mime_type') else 'audio/wav'
            
            print(f"📊 TTS Audio Info:")
            print(f"   Size: {len(audio_data)} bytes")
            print(f"   MIME type: {mime_type}")
            
            # Convert PCM to WAV if needed
            if 'pcm' in mime_type.lower() or 'L16' in mime_type:
                print("🔄 Converting PCM to WAV...")
                audio_data = self._pcm_to_wav(audio_data, sample_rate=24000, channels=1, sample_width=2)
                mime_type = 'audio/wav'
                print(f"✅ Converted to WAV: {len(audio_data)} bytes")
            
            # Convert to base64 for web transmission
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                "success": True,
                "text": text,
                "audio_data": audio_base64,
                "mime_type": mime_type,
                "voice": voice_config['voice'],
                "round_type": round_type
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"TTS Error: {e}")
            
            # Check if it's a quota error
            if '429' in error_msg or 'quota' in error_msg.lower() or 'RESOURCE_EXHAUSTED' in error_msg:
                print("⚠️ TTS quota exceeded - continuing without audio")
                return {
                    "success": False,
                    "text": text,
                    "audio_data": None,
                    "error": "TTS quota exceeded. Please read the question.",
                    "quota_exceeded": True
                }
            
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "text": text,
                "audio_data": None,
                "error": str(e)
            }
    
    def speech_to_text(self, audio_data: bytes, mime_type: str = "audio/webm") -> Dict[str, Any]:
        """
        Convert speech to text using Gemini - NEW API
        
        Args:
            audio_data: Audio bytes
            mime_type: MIME type of audio
        
        Returns:
            Dict with transcribed text
        """
        temp_audio_path = None
        try:
            print(f"📤 Processing audio ({len(audio_data)} bytes)...")
            
            # Use NEW google-genai API (same as TTS)
            from google import genai
            from google.genai import types
            
            gemini_key = os.getenv("GEMINI_API_KEY").strip('"').strip("'")
            client = genai.Client(api_key=gemini_key)
            
            print("🤖 Generating transcript with gemini-2.5-flash...")
            
            # Try with proper prompt
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=audio_data,
                        mime_type=mime_type,
                    ),
                    'Please transcribe the audio above. Provide only the spoken text.'
                ]
            )
            
            # Extract text from response
            transcript = None
            
            # Method 1: Direct text attribute
            if hasattr(response, 'text') and response.text:
                transcript = response.text
                print(f"✅ Got transcript from response.text")
            
            # Method 2: From candidates
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    content = candidate.content
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                transcript = part.text
                                print(f"✅ Got transcript from parts")
                                break
            
            if not transcript:
                # Check if audio was rejected
                print(f"❌ No transcript in response")
                print(f"   Finish reason: {response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                print(f"   Content: {response.candidates[0].content if response.candidates else 'N/A'}")
                
                # Return a helpful error
                return {
                    "success": False,
                    "transcript": "",
                    "error": "Could not transcribe audio. The audio may be too short, unclear, or in an unsupported format."
                }
            
            transcript = transcript.strip()
            print(f"✅ Transcript ({len(transcript)} chars): {transcript[:100]}")
            
            return {
                "success": True,
                "transcript": transcript,
                "original_mime_type": mime_type
            }
            
        except Exception as e:
            print(f"❌ STT Error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "transcript": "",
                "error": str(e)
            }
    
    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
        """Convert raw PCM audio to WAV format"""
        import io
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        
        # Get WAV data
        wav_buffer.seek(0)
        return wav_buffer.read()
    
    def save_audio_file(self, audio_data: bytes, filename: str):
        """Save audio data to WAV file"""
        try:
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(24000)  # 24kHz
                wf.writeframes(audio_data)
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def get_voice_for_round(self, round_type: str) -> str:
        """Get voice name for a specific round"""
        config = self.voice_configs.get(round_type)
        return config['voice'] if config else "Kore"
