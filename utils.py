import hashlib
import wave
from PIL import Image
import numpy as np
import os

def estimate_capacity_image(image: Image.Image) -> dict:
    width, height = image.size
    channels = len(image.getbands())
    total_bits = width * height * channels
    usable_bits = total_bits - 50
    usable_bytes = usable_bits // 8
    usable_chars = usable_bytes
    usage_examples = {}
    for length in [100, 500, 1000, 5000]:
        if length <= usable_chars:
            percentage = (length * 8) / total_bits * 100
            usage_examples[f"{length}_chars"] = f"{percentage:.2f}%"
    return {
        "dimensions": f"{width}x{height}",
        "channels": channels,
        "total_pixels": width * height,
        "total_bits": total_bits,
        "usable_bytes": usable_bytes,
        "usable_chars": usable_chars,
        "usage_examples": usage_examples,
        "efficiency_rating": "High" if usable_chars > 10000 else "Medium" if usable_chars > 1000 else "Low"
    }

def estimate_capacity_audio(audio_path: str) -> dict:
    try:
        if audio_path.endswith('.wav'):
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.getnframes()
                sample_rate = audio.getframerate()
                channels = audio.getnchannels()
                duration = frames / sample_rate
                total_bits = frames * channels
                usable_bits = total_bits - 50
                usable_bytes = usable_bits // 8
                return {
                    "duration": f"{duration:.2f} seconds",
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "total_samples": frames,
                    "usable_bytes": usable_bytes,
                    "usable_chars": usable_bytes,
                    "bitrate_capacity": f"{usable_bytes/duration:.0f} bytes/second",
                    "efficiency_rating": "High" if usable_bytes > 50000 else "Medium" if usable_bytes > 5000 else "Low"
                }
        else:
            file_size = os.path.getsize(audio_path)
            estimated_samples = file_size * 8
            usable_bytes = estimated_samples // 8
            return {
                "format": "MP3 (estimated)",
                "file_size": f"{file_size/1024:.1f} KB",
                "estimated_capacity": f"{usable_bytes:,} bytes",
                "note": "Convert to WAV for actual steganography",
                "efficiency_rating": "Estimated"
            }
    except Exception as e:
        return {"error": f"Cannot analyze audio: {str(e)}"}

def estimate_capacity_video(video_path: str) -> dict:
    try:
        file_size = os.path.getsize(video_path)
        estimated_frames = file_size // 10000
        estimated_capacity = estimated_frames * 1000
        return {
            "format": "MP4/AVI (simulated)",
            "file_size": f"{file_size/1024/1024:.1f} MB",
            "estimated_frames": estimated_frames,
            "estimated_capacity": f"{estimated_capacity:,} bytes",
            "note": "Video steganography uses frame-based approach",
            "efficiency_rating": "High (Simulated)"
        }
    except Exception as e:
        return {"error": f"Cannot analyze video: {str(e)}"}

def calculate_message_hash(message: str) -> str:
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

def verify_message_integrity(original: str, extracted: str) -> dict:
    original_hash = calculate_message_hash(original)
    extracted_hash = calculate_message_hash(extracted)
    is_valid = original_hash == extracted_hash
    return {
        "is_valid": is_valid,
        "original_hash": original_hash,
        "extracted_hash": extracted_hash,
        "hash_match": is_valid,
        "integrity_score": 100 if is_valid else 0,
        "status": "✅ VERIFIED" if is_valid else "❌ CORRUPTED"
    }

def get_security_metrics(message: str, password: str) -> dict:
    message_entropy = len(set(message.lower())) / len(message) if message else 0
    password_strength = 0
    if len(password) >= 8:
        password_strength += 25
    if any(c.isupper() for c in password):
        password_strength += 25
    if any(c.islower() for c in password):
        password_strength += 25
    if any(c.isdigit() for c in password):
        password_strength += 25
    security_score = (password_strength + message_entropy * 100) / 2
    if security_score >= 80:
        security_rating = "🛡️ EXCELLENT"
    elif security_score >= 60:
        security_rating = "🔒 GOOD"
    elif security_score >= 40:
        security_rating = "⚠️ MODERATE"
    else:
        security_rating = "🚨 WEAK"
    return {
        "message_entropy": f"{message_entropy:.2f}",
        "password_strength": f"{password_strength}%",
        "security_score": f"{security_score:.0f}%",
        "security_rating": security_rating,
        "recommendations": get_security_recommendations(password_strength, message_entropy)
    }

def get_security_recommendations(password_strength: int, message_entropy: float) -> list:
    recommendations = []
    if password_strength < 75:
        recommendations.append("🔑 Use a stronger password with mixed case, numbers, and symbols")
    if message_entropy < 0.3:
        recommendations.append("📝 Consider using a more varied message with different characters")
    if not recommendations:
        recommendations.append("✅ Excellent security configuration!")
    return recommendations

def format_bytes(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} bytes"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val/1024:.1f} KB"
    else:
        return f"{bytes_val/1024/1024:.1f} MB"

def test_utilities():
    print("🧪 Testing StegoX Utilities...")
    test_message = "Hello World!"
    hash_result = calculate_message_hash(test_message)
    print(f"📝 Message: {test_message}")
    print(f"🔐 SHA-256: {hash_result[:16]}...")
    integrity = verify_message_integrity(test_message, test_message)
    print(f"✅ Integrity Check: {integrity['status']}")
    security = get_security_metrics(test_message, "TestPass123!")
    print(f"🛡️ Security Rating: {security['security_rating']}")
    print("✅ All utilities tested successfully!")

if __name__ == "__main__":
    test_utilities()