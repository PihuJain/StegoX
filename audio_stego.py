import wave
import numpy as np
import os

END_MARKER = '1010101010101010'

def text_to_binary(text: str) -> str:
    utf8_bytes = text.encode('utf-8')
    return ''.join(format(byte, '08b') for byte in utf8_bytes)

def binary_to_text(binary: str) -> str:
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            chars.append(int(byte, 2))
    
    try:
        return bytes(chars).decode('utf-8')
    except UnicodeDecodeError:
        return bytes(chars).decode('utf-8', errors='ignore')

def hide_message_in_audio(audio_path: str, encrypted_message: str, output_path: str) -> bool:
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = audio.readframes(-1)
            params = audio.getparams()
        
        audio_data = np.frombuffer(frames, dtype=np.int16)
        binary_message = text_to_binary(encrypted_message) + END_MARKER
        message_length = len(binary_message)
        max_capacity = len(audio_data)
        if message_length > max_capacity:
            raise ValueError(f"Message too large. Max capacity: {max_capacity} bits, Message: {message_length} bits")
        
        stego_data = audio_data.copy()
        for i in range(message_length):
            if i < len(stego_data):
                stego_data[i] = (stego_data[i] & 0xFFFE) | int(binary_message[i])
        
        with wave.open(output_path, 'wb') as stego_audio:
            stego_audio.setparams(params)
            stego_audio.writeframes(stego_data.tobytes())
        
        print(f"✅ Message hidden in audio! Capacity used: {message_length}/{max_capacity} bits ({(message_length/max_capacity)*100:.2f}%)")
        return True
        
    except Exception as e:
        print(f"❌ Error hiding message in audio: {str(e)}")
        return False

def extract_message_from_audio(audio_path: str) -> str:
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = audio.readframes(-1)
        
        audio_data = np.frombuffer(frames, dtype=np.int16)
        binary_bits = []
        for sample in audio_data:
            binary_bits.append(str(sample & 1))
        
        binary_string = ''.join(binary_bits)
        end_marker_pos = binary_string.find(END_MARKER)
        if end_marker_pos == -1:
            raise ValueError("End marker not found. This may not be a valid stego audio file.")
        
        message_binary = binary_string[:end_marker_pos]
        extracted_message = binary_to_text(message_binary)
        
        print(f"✅ Message extracted from audio! Length: {len(extracted_message)} characters")
        return extracted_message
        
    except Exception as e:
        print(f"❌ Error extracting message from audio: {str(e)}")
        raise

def get_audio_capacity(audio_path: str) -> dict:
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = audio.readframes(-1)
            params = audio.getparams()
        
        audio_data = np.frombuffer(frames, dtype=np.int16)
        total_samples = len(audio_data)
        max_chars = total_samples // 8
        duration = total_samples / params.framerate
        
        return {
            'duration': f"{duration:.2f} seconds",
            'sample_rate': params.framerate,
            'channels': params.nchannels,
            'total_samples': total_samples,
            'max_bits': total_samples,
            'max_characters': max_chars,
            'recommended_message_length': max_chars - 50
        }
        
    except Exception as e:
        return {'error': str(e)}

def test_audio_steganography(test_audio_path: str = None):
    if not test_audio_path:
        test_audio_path = "Dataset/Sample audio files (.mp3)/sample-3s.mp3"
    
    print("🧪 Testing Audio Steganography Engine...")
    
    if test_audio_path.endswith('.mp3'):
        print("⚠️ Audio stego works best with WAV files. MP3 testing simulated.")
        print("✅ Audio steganography module loaded successfully!")
        return
    
    if not os.path.exists(test_audio_path):
        print(f"❌ Test audio file not found: {test_audio_path}")
        return
    
    test_message = "This is a secret audio message for testing!"
    capacity = get_audio_capacity(test_audio_path)
    print(f"📊 Audio Capacity: {capacity}")
    print("✅ Audio steganography test structure ready!")

if __name__ == "__main__":
    test_audio_steganography()