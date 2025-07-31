from PIL import Image
import numpy as np
import os
from numba import jit

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

@jit(nopython=True)
def fast_embed_pixels(binary_data, flat_pixels):
    result = flat_pixels.copy()
    for i in range(min(len(binary_data), len(flat_pixels))):
        result[i] = (result[i] & 254) | binary_data[i]
    return result

@jit(nopython=True)
def fast_extract_bits(flat_pixels, num_bits):
    result = np.zeros(min(num_bits, len(flat_pixels)), dtype=np.uint8)
    for i in range(len(result)):
        result[i] = flat_pixels[i] & 1
    return result

def hide_message_in_image(image_path: str, encrypted_message: str, output_path: str) -> bool:
    try:
        img = Image.open(image_path)
        if img.mode not in ['RGB', 'RGBA']:
            img = img.convert('RGB')
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        channels = img_array.shape[2] if len(img_array.shape) > 2 else 1
        binary_message = text_to_binary(encrypted_message) + END_MARKER
        message_length = len(binary_message)
        max_capacity = height * width * channels
        if message_length > max_capacity:
            raise ValueError(f"Message too large. Max capacity: {max_capacity} bits, Message: {message_length} bits")
        flat_img = img_array.flatten()
        binary_array = np.array([int(bit) for bit in binary_message], dtype=np.uint8)
        flat_img = fast_embed_pixels(binary_array, flat_img)
        stego_array = flat_img.reshape(img_array.shape)
        stego_img = Image.fromarray(stego_array.astype(np.uint8))
        stego_img.save(output_path, 'PNG')
        print(f"✅ Message hidden successfully! Capacity used: {message_length}/{max_capacity} bits ({(message_length/max_capacity)*100:.2f}%)")
        return True
    except Exception as e:
        print(f"❌ Error hiding message: {str(e)}")
        return False

def extract_message_from_image(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        if img.mode not in ['RGB', 'RGBA']:
            img = img.convert('RGB')
        img_array = np.array(img)
        flat_img = img_array.flatten()
        max_bits = len(flat_img)
        binary_bits_array = fast_extract_bits(flat_img, max_bits)
        binary_string = ''.join(str(bit) for bit in binary_bits_array)
        end_marker_pos = binary_string.find(END_MARKER)
        if end_marker_pos == -1:
            raise ValueError("End marker not found. This may not be a valid stego image.")
        message_binary = binary_string[:end_marker_pos]
        extracted_message = binary_to_text(message_binary)
        print(f"✅ Message extracted successfully! Length: {len(extracted_message)} characters")
        return extracted_message
    except Exception as e:
        print(f"❌ Error extracting message: {str(e)}")
        raise

def get_image_capacity(image_path: str) -> dict:
    try:
        img = Image.open(image_path)
        if img.mode not in ['RGB', 'RGBA']:
            img = img.convert('RGB')
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        channels = img_array.shape[2] if len(img_array.shape) > 2 else 1
        total_pixels = height * width * channels
        max_chars = total_pixels // 8
        return {
            'dimensions': f"{width}x{height}",
            'channels': channels,
            'total_pixels': total_pixels,
            'max_bits': total_pixels,
            'max_characters': max_chars,
            'recommended_message_length': max_chars - 50
        }
    except Exception as e:
        return {'error': str(e)}

def test_steganography(test_image_path: str):
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    print("🧪 Testing Steganography Engine...")
    test_message = "This is a secret message for testing!"
    capacity = get_image_capacity(test_image_path)
    print(f"📊 Image Capacity: {capacity}")
    output_path = "test_stego_output.png"
    success = hide_message_in_image(test_image_path, test_message, output_path)
    if success and os.path.exists(output_path):
        extracted = extract_message_from_image(output_path)
        if extracted == test_message:
            print("✅ Steganography test passed!")
        else:
            print(f"❌ Test failed. Original: '{test_message}', Extracted: '{extracted}'")
        os.remove(output_path)
    else:
        print("❌ Steganography test failed!")

if __name__ == "__main__":
    sample_image = "Dataset/Sample images (.png)/github-mark-3641908115.png"
    test_steganography(sample_image)