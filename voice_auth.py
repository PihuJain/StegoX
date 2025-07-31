import whisper
import os
import tempfile
from pydub import AudioSegment
import re
import string

class VoiceAuthenticator:
    
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            print(f"🔄 Loading Whisper model ({self.model_size})...")
            self.model = whisper.load_model(self.model_size)
            print(f"✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {str(e)}")
            raise
    
    def normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def convert_audio_to_wav(self, audio_path: str) -> str:
        try:
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            audio.export(temp_wav.name, format='wav')
            return temp_wav.name
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")
    
    def transcribe_audio(self, audio_path: str) -> dict:
        if not self.model:
            raise Exception("Whisper model not loaded")
        
        temp_wav_path = None
        try:
            if not audio_path.lower().endswith('.wav'):
                temp_wav_path = self.convert_audio_to_wav(audio_path)
                process_path = temp_wav_path
            else:
                process_path = audio_path
            
            print("🎤 Transcribing audio...")
            result = self.model.transcribe(process_path, language='en')
            transcribed_text = result["text"].strip()
            detected_language = result.get("language", "unknown")
            avg_confidence = 0.0
            if "segments" in result and result["segments"]:
                confidences = [seg.get("avg_logprob", 0) for seg in result["segments"]]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            print(f"✅ Transcription completed: '{transcribed_text}'")
            return {
                'text': transcribed_text,
                'normalized_text': self.normalize_text(transcribed_text),
                'language': detected_language,
                'confidence': avg_confidence,
                'success': True
            }
        except Exception as e:
            print(f"❌ Transcription failed: {str(e)}")
            return {
                'text': '',
                'normalized_text': '',
                'language': 'unknown',
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
        finally:
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except:
                    pass
    
    def verify_passphrase(self, audio_path: str, expected_passphrase: str, similarity_threshold: float = 0.8) -> dict:
        transcription_result = self.transcribe_audio(audio_path)
        
        if not transcription_result['success']:
            return {
                'verified': False,
                'confidence': 0.0,
                'transcribed_text': '',
                'expected_text': expected_passphrase,
                'error': transcription_result.get('error', 'Transcription failed')
            }
        
        transcribed_normalized = transcription_result['normalized_text']
        expected_normalized = self.normalize_text(expected_passphrase)
        similarity = self._calculate_similarity(transcribed_normalized, expected_normalized)
        verified = similarity >= similarity_threshold
        
        result = {
            'verified': verified,
            'similarity': similarity,
            'confidence': transcription_result['confidence'],
            'transcribed_text': transcription_result['text'],
            'transcribed_normalized': transcribed_normalized,
            'expected_text': expected_passphrase,
            'expected_normalized': expected_normalized,
            'threshold': similarity_threshold,
            'language': transcription_result['language']
        }
        
        if verified:
            print(f"✅ Voice authentication successful! Similarity: {similarity:.2f}")
        else:
            print(f"❌ Voice authentication failed. Similarity: {similarity:.2f} (threshold: {similarity_threshold})")
        
        return result
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        if text1 == text2:
            return 1.0
        words1 = set(text1.split())
        words2 = set(text2.split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

def test_voice_auth(audio_file_path: str = None):
    print("🧪 Testing Voice Authentication System...")
    
    if not audio_file_path:
        audio_file_path = "Dataset/Sample audio files (.mp3)/sample-3s.mp3"
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Test audio file not found: {audio_file_path}")
        return
    
    try:
        auth = VoiceAuthenticator(model_size="base")
        result = auth.transcribe_audio(audio_file_path)
        print(f"📝 Transcription Result: {result}")
        if result['success'] and result['text']:
            verification = auth.verify_passphrase(
                audio_file_path, 
                result['text'], 
                similarity_threshold=0.7
            )
            print(f"🔐 Verification Result: {verification}")
        print("✅ Voice authentication test completed!")
    except Exception as e:
        print(f"❌ Voice authentication test failed: {str(e)}")

if __name__ == "__main__":
    test_voice_auth()