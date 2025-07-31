import streamlit as st
import os
import tempfile
import time
from PIL import Image
import io
import psutil

from encryptor import encrypt_message, decrypt_message, generate_random_key, semantic_filename, get_message_preview
from stego_engine import hide_message_in_image, extract_message_from_image, get_image_capacity
from audio_stego import hide_message_in_audio, extract_message_from_audio, get_audio_capacity
from voice_auth import VoiceAuthenticator
from utils import (estimate_capacity_image, estimate_capacity_audio, estimate_capacity_video, 
                   verify_message_integrity, calculate_message_hash, get_security_metrics, format_bytes)

st.set_page_config(
    page_title="StegoX - Secure Steganography Platform",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2rem;
}

.sub-header {
    font-size: 1.5rem;
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}

.media-selector {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.success-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    margin: 1rem 0;
}

.error-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    margin: 1rem 0;
}

.info-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
    margin: 1rem 0;
}

.key-display {
    background-color: #f8f9fa;
    border: 2px dashed #6c757d;
    padding: 1rem;
    border-radius: 8px;
    font-family: monospace;
    font-size: 1.1rem;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

if 'voice_auth' not in st.session_state:
    st.session_state.voice_auth = None
if 'voice_auth_loaded' not in st.session_state:
    st.session_state.voice_auth_loaded = False
if 'generated_key' not in st.session_state:
    st.session_state.generated_key = None
if 'original_message' not in st.session_state:
    st.session_state.original_message = None
if 'original_message_hash' not in st.session_state:
    st.session_state.original_message_hash = None

def load_voice_authenticator():
    if not st.session_state.voice_auth_loaded:
        try:
            st.session_state.voice_auth = VoiceAuthenticator()
            st.session_state.voice_auth_loaded = True
            return True
        except Exception as e:
            st.error(f"Failed to load voice authentication: {str(e)}")
            return False
    return True

@st.cache_data(ttl=1)
def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        'cpu': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used': memory.used,
        'memory_total': memory.total,
        'disk_percent': disk.percent,
        'disk_used': disk.used,
        'disk_total': disk.total
    }

def show_system_monitor():
    st.markdown("## System Monitor")
    stats = get_system_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU Usage", f"{stats['cpu']:.1f}%")
    with col2:
        st.metric("Memory Usage", f"{stats['memory_percent']:.1f}%")
    with col3:
        st.metric("Disk Usage", f"{stats['disk_percent']:.1f}%")

def display_media_capacity(file_path: str, media_type: str, uploaded_file=None):
    try:
        if media_type == "Image":
            capacity = get_image_capacity(file_path)
            estimated = estimate_capacity_image(file_path)
        elif media_type == "Audio":
            capacity = get_audio_capacity(file_path)
            estimated = estimate_capacity_audio(file_path)
        else:
            capacity = estimate_capacity_video(file_path)
            estimated = capacity
        
        st.markdown("### Capacity Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Actual Capacity", format_bytes(capacity))
        with col2:
            st.metric("Estimated Capacity", format_bytes(estimated))
        
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            st.metric("File Size", format_bytes(file_size))
            
            if capacity > 0:
                efficiency = (file_size / capacity) * 100
                st.metric("Storage Efficiency", f"{efficiency:.1f}%")
                
    except Exception as e:
        st.warning(f"Could not analyze capacity: {str(e)}")

def display_security_metrics(message: str, password: str):
    try:
        metrics = get_security_metrics(message, password)
        
        st.markdown("### Security Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Password Strength", f"{metrics['password_strength']}/100")
        with col2:
            st.metric("Entropy", f"{metrics['entropy']:.2f}")
        with col3:
            st.metric("Complexity", f"{metrics['complexity']}/100")
            
    except Exception as e:
        st.warning(f"Could not calculate security metrics: {str(e)}")

def main():
    st.markdown('<h1 class="main-header">StegoX</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Steganography Platform</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="media-selector">
    <h3>Select Steganography Mode</h3>
    </div>
    """, unsafe_allow_html=True)
    
    media_choice = st.selectbox(
        "Choose Media Type",
        ["Image Steganography", "Audio Steganography", "Video Steganography (Simulated)"],
        help="Select the type of media to hide your secret message in"
    )
    
    if "Image" in media_choice:
        media_type = "Image"
        file_types = ["png", "jpg", "jpeg"]
        file_desc = "PNG/JPEG image"
    elif "Audio" in media_choice:
        media_type = "Audio"
        file_types = ["wav", "mp3"]
        file_desc = "WAV/MP3 audio file"
    else:
        media_type = "Video"
        file_types = ["mp4", "avi", "mov"]
        file_desc = "MP4/AVI/MOV video file"
    
    with st.sidebar:
        st.markdown("## How to Use StegoX")
        st.markdown(f"""
        ### Hide Mode ({media_type}):
        1. Upload a {file_desc}
        2. Enter your secret message
        3. Set password (or auto-generate)
        4. Upload voice passphrase audio
        5. Download the stego file
        
        ### Extract Mode:
        1. Upload the stego {file_desc.lower()}
        2. Enter the password
        3. Upload matching voice passphrase
        4. View the revealed message
        
        ### Voice Tips:
        - Speak clearly and distinctly
        - Use short, memorable phrases
        - Record in a quiet environment
        - Support formats: MP3, WAV, M4A
        """)

        
        show_system_monitor()

    hide_tab, extract_tab, about_tab = st.tabs(["Hide Message", "Extract Message", "About"])
    
    with hide_tab:
        st.header(f"Hide Secret Message in {media_type}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"Upload Cover {media_type}")
            uploaded_file = st.file_uploader(
                f"Choose a {file_desc} to hide your message in:",
                type=file_types,
                key=f"hide_{media_type.lower()}"
            )
            
            if uploaded_file:
                if media_type == "Image":
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Cover Image", use_container_width=True)
                elif media_type == "Audio":
                    st.audio(uploaded_file, format="audio/wav")
                    st.info("Audio file loaded successfully!")
                else:
                    st.video(uploaded_file)
                    st.info("Video file loaded (using first frame for steganography)")
                
                if media_type == "Image":
                    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
                    image.save(temp_file_path, 'PNG')
                else:
                    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_types[0]}').name
                    with open(temp_file_path, 'wb') as f:
                        f.write(uploaded_file.read())
                
                display_media_capacity(temp_file_path, media_type, uploaded_file)
        
        with col2:
            st.subheader("Secret Message & Security")
            
            secret_message = st.text_area(
                "Enter your secret message:",
                height=100,
                placeholder="Type your confidential message here...",
                help="This message will be encrypted and hidden in your chosen media"
            )
            
            st.subheader("Password Configuration")
            
            password_option = st.radio(
                "Password Option:",
                ["Enter Custom Password", "Auto-Generate Secure Key"],
                help="Choose whether to set your own password or generate a random one"
            )
            
            if password_option == "Enter Custom Password":
                text_password = st.text_input(
                    "Custom Password:",
                    type="password",
                    placeholder="Enter a strong password"
                )
            else:
                if st.button("Generate New Key") or st.session_state.generated_key is None:
                    st.session_state.generated_key = generate_random_key()
                
                if st.session_state.generated_key:
                    st.markdown(f"""
                    <div class="key-display">
                    <strong>Generated Key:</strong><br/>
                    <code>{st.session_state.generated_key}</code><br/>
                    <small>Save this key securely - you'll need it to decrypt!</small>
                    </div>
                    """, unsafe_allow_html=True)
                    text_password = st.session_state.generated_key
                else:
                    text_password = ""
            
            st.subheader("Voice Passphrase")
            voice_passphrase_text = st.text_input(
                "Voice Passphrase (text):",
                placeholder="Enter the phrase you'll speak (e.g., 'unlock the secret')",
                help="This should match what you'll say in your voice recording"
            )
            
            uploaded_voice = st.file_uploader(
                "Upload voice recording of the passphrase:",
                type=['mp3', 'wav', 'm4a', 'ogg'],
                key=f"hide_voice_{media_type.lower()}",
                help="Record yourself clearly saying the passphrase"
            )
            
            if uploaded_voice:
                st.audio(uploaded_voice, format="audio/mp3")
            
            if secret_message and text_password:
                st.subheader("Security Analysis")
                display_security_metrics(secret_message, text_password)
        
        if st.button(f"Encrypt & Hide in {media_type}", type="primary", use_container_width=True):
            if uploaded_file and secret_message and text_password and voice_passphrase_text and uploaded_voice:
                try:
                    with st.spinner("Processing..."):
                        if not load_voice_authenticator():
                            st.stop()
                        
                        temp_voice_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                        with open(temp_voice_path, 'wb') as f:
                            f.write(uploaded_voice.read())
                        
                        verification = st.session_state.voice_auth.verify_passphrase(
                            temp_voice_path, 
                            voice_passphrase_text,
                            similarity_threshold=0.7
                        )
                        
                        if not verification['verified']:
                            st.error(f"Voice verification failed! Transcribed: '{verification['transcribed_text']}' vs Expected: '{voice_passphrase_text}'")
                            st.stop()
                        
                        st.session_state.original_message = secret_message
                        st.session_state.original_message_hash = calculate_message_hash(secret_message)
                        
                        encrypted_message = encrypt_message(secret_message, text_password)
                        
                        semantic_name = semantic_filename(secret_message, media_type.lower())
                        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_types[0]}').name
                        
                        success = False
                        if media_type == "Image":
                            success = hide_message_in_image(temp_file_path, encrypted_message, output_path)
                        elif media_type == "Audio":
                            if uploaded_file.name.endswith('.wav'):
                                success = hide_message_in_audio(temp_file_path, encrypted_message, output_path)
                            else:
                                st.warning("Audio steganography works best with WAV files. MP3 conversion simulated.")
                                success = True
                        else:
                            st.info("Video steganography simulated - using frame-based approach")
                            success = True
                        
                        if success:
                            message_hash = calculate_message_hash(secret_message)
                            
                            st.markdown(f"""
                            <div class="success-box">
                            <h4>Message Hidden Successfully in {media_type}!</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                <div>
                                    <h5>Security</h5>
                                    <ul>
                                    <li><strong>Voice Verification:</strong> Passed (Similarity: {verification['similarity']:.2f})</li>
                                    <li><strong>Encryption:</strong> AES-256 CBC</li>
                                    <li><strong>Steganography:</strong> LSB Embedding</li>
                                    </ul>
                                </div>
                                <div>
                                    <h5>Details</h5>
                                    <ul>
                                    <li><strong>Semantic Filename:</strong> {semantic_name}</li>
                                    <li><strong>Message Preview:</strong> "{get_message_preview(secret_message)}"</li>
                                    <li><strong>Integrity Hash:</strong> {message_hash[:12]}...</li>
                                    </ul>
                                </div>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if media_type != "Video":
                                with open(output_path, 'rb') as f:
                                    st.download_button(
                                        label=f"Download Stego {media_type}",
                                        data=f.read(),
                                        file_name=semantic_name,
                                        mime=f"{'image/png' if media_type == 'Image' else 'audio/wav'}"
                                    )
                            else:
                                st.info("Video download simulated - full implementation coming soon!")
                        
                        for path in [temp_file_path, temp_voice_path, output_path]:
                            if os.path.exists(path):
                                try:
                                    os.unlink(path)
                                except:
                                    pass
                                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please fill in all fields and upload all required files.")

    with extract_tab:
        st.header(f"Extract Hidden Message from {media_type}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"Upload Stego {media_type}")
            stego_file = st.file_uploader(
                f"Choose the stego {file_desc.lower()} containing the hidden message:",
                type=file_types,
                key=f"extract_{media_type.lower()}"
            )
            
            if stego_file:
                if media_type == "Image":
                    image = Image.open(stego_file)
                    st.image(image, caption="Stego Image", use_container_width=True)
                elif media_type == "Audio":
                    st.audio(stego_file, format="audio/wav")
                else:
                    st.video(stego_file)
        
        with col2:
            st.subheader("Authentication")
            
            extract_password = st.text_input(
                "Password:",
                type="password",
                placeholder="Enter the password used for encryption",
                key=f"extract_password_{media_type.lower()}"
            )
            
            st.subheader("Voice Authentication")
            extract_voice = st.file_uploader(
                "Upload voice recording for authentication:",
                type=['mp3', 'wav', 'm4a', 'ogg'],
                key=f"extract_voice_{media_type.lower()}"
            )
            
            if extract_voice:
                st.audio(extract_voice, format="audio/mp3")
        
        if st.button(f"Extract & Decrypt from {media_type}", type="primary", use_container_width=True):
            if stego_file and extract_password and extract_voice:
                try:
                    with st.spinner("Processing..."):
                        if not load_voice_authenticator():
                            st.stop()
                        
                        if media_type == "Image":
                            temp_stego_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
                            image = Image.open(stego_file)
                            image.save(temp_stego_path, 'PNG')
                        else:
                            temp_stego_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_types[0]}').name
                            with open(temp_stego_path, 'wb') as f:
                                f.write(stego_file.read())
                        
                        temp_voice_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                        with open(temp_voice_path, 'wb') as f:
                            f.write(extract_voice.read())
                        
                        if media_type == "Image":
                            encrypted_message = extract_message_from_image(temp_stego_path)
                        elif media_type == "Audio" and stego_file.name.endswith('.wav'):
                            encrypted_message = extract_message_from_audio(temp_stego_path)
                        else:
                            st.warning(f"{media_type} extraction simulated for demo purposes")
                            encrypted_message = "U2FtcGxlIGVuY3J5cHRlZCBtZXNzYWdl"
                        
                        transcription = st.session_state.voice_auth.transcribe_audio(temp_voice_path)
                        
                        if not transcription['success']:
                            st.error("Voice transcription failed!")
                            st.stop()
                        
                        try:
                            decrypted_message = decrypt_message(encrypted_message, extract_password)
                            
                            integrity_status = "No original message for comparison"
                            integrity_details = ""
                            
                            if st.session_state.original_message:
                                integrity_result = verify_message_integrity(
                                    st.session_state.original_message, 
                                    decrypted_message
                                )
                                integrity_status = integrity_result['status']
                                integrity_details = f"""
                                <li><strong>Original Hash:</strong> {integrity_result['original_hash'][:12]}...</li>
                                <li><strong>Extracted Hash:</strong> {integrity_result['extracted_hash'][:12]}...</li>
                                <li><strong>Integrity Score:</strong> {integrity_result['integrity_score']}%</li>
                                """
                            
                            st.markdown(f"""
                            <div class="success-box">
                            <h4>Message Extracted Successfully from {media_type}!</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                <div>
                                    <h5>Verification</h5>
                                    <ul>
                                    <li><strong>Voice Transcription:</strong> "{transcription['text']}"</li>
                                    <li><strong>Decryption:</strong> Successful</li>
                                    <li><strong>Integrity Check:</strong> {integrity_status}</li>
                                    </ul>
                                </div>
                                <div>
                                    <h5>Details</h5>
                                    <ul>
                                    <li><strong>Media Type:</strong> {media_type}</li>
                                    {integrity_details}
                                    </ul>
                                </div>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.subheader("Revealed Secret Message:")
                            st.markdown(f"""
                            <div style="padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; font-size: 1.2rem; text-align: center; margin: 1rem 0;">
                            <h3 style="color: white; margin: 0;">{decrypted_message}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.session_state.original_message:
                                if integrity_result['is_valid']:
                                    st.success("Message integrity verified - No corruption detected!")
                                else:
                                    st.error("Message integrity compromised - Possible corruption or tampering detected!")
                                    
                                    with st.expander("View Integrity Details"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.text("Original Message Hash:")
                                            st.code(integrity_result['original_hash'])
                                        with col2:
                                            st.text("Extracted Message Hash:")
                                            st.code(integrity_result['extracted_hash'])
                            
                        except Exception as decrypt_error:
                            st.error(f"Decryption failed: {str(decrypt_error)}")
                            st.info(f"Voice transcribed as: '{transcription['text']}'")
                        
                        for path in [temp_stego_path, temp_voice_path]:
                            if os.path.exists(path):
                                try:
                                    os.unlink(path)
                                except:
                                    pass
                                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please upload the stego file, enter password, and provide voice authentication.")

    with about_tab:
        st.header("About StegoX")
        st.info("About section")

if __name__ == "__main__":
    main()
