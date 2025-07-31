# StegoX - Secure Steganography Platform

A multi-modal steganography application that allows users to hide secret messages in images, audio files, and video files using advanced encryption and voice authentication.

## Features

- **Multi-Modal Support**: Hide messages in images (PNG/JPEG), audio files (WAV/MP3), and video files (MP4/AVI/MOV)
- **AES-256 Encryption**: Military-grade encryption for secure message protection
- **Voice Authentication**: Whisper AI-powered voice verification for enhanced security
- **LSB Steganography**: Least Significant Bit embedding for invisible data hiding
- **Auto-Key Generation**: Secure random password generation
- **Semantic Naming**: Automatic filename generation based on content
- **Cross-Platform**: Web application (Streamlit) and Android app support

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- Android Studio (for Android app development)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ChinmayaThakral/StegoX.git
cd StegoX
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Test the installation:
```bash
python -c "import streamlit, pycryptodome, PIL, numpy, whisper; print('All dependencies installed successfully!')"
```

## Usage

### Web Application

1. Start the Streamlit server:
```bash
streamlit run stegox_app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Choose your steganography mode:
   - **Hide Mode**: Upload media, enter message, set password, provide voice authentication
   - **Extract Mode**: Upload stego file, enter password, provide voice authentication

### Android Application

1. Open the `android-app` folder in Android Studio
2. Build and install the app on your device
3. Ensure the Streamlit server is running on your local network
4. Update the server URL in `WebModel.java` if needed

## Project Structure

```
StegoX/
├── stegox_app.py          # Main Streamlit web application
├── encryptor.py           # AES-256 encryption/decryption
├── stego_engine.py        # Image steganography implementation
├── audio_stego.py         # Audio steganography implementation
├── voice_auth.py          # Voice authentication using Whisper AI
├── utils.py               # Utility functions and helpers

├── requirements.txt       # Python dependencies
├── android-app/           # Android application
│   └── app/
│       └── src/main/
│           ├── java/com/pydroidx/stegox/
│           └── res/
└── Dataset/               # Sample media files for testing
    ├── Sample audio files (.mp3)/
    ├── Sample images (.png)/
    └── Sample video files (.mp4)/
```

## Security Features

- **AES-256 CBC Encryption**: Industry-standard encryption algorithm
- **LSB Steganography**: Invisible data hiding in media files
- **Voice Authentication**: Multi-factor authentication using voice recognition
- **Message Integrity**: Hash-based integrity verification
- **Semantic Security**: Automatic filename generation to avoid detection

## Technical Specifications

- **Framework**: Streamlit + Python 3.9+
- **Encryption**: PyCryptodome (AES-256)
- **Image Processing**: PIL + NumPy
- **Audio Processing**: Wave + NumPy + FFmpeg
- **Voice AI**: OpenAI Whisper (Base Model)
- **Android**: WebView-based hybrid app

## Use Cases

### Professional
- Secure multi-media communications
- Corporate document protection
- Legal evidence with audio/video proof

### Creative
- Digital art with hidden meanings
- Interactive media experiences
- Educational steganography demonstrations

### Research
- Multi-modal security studies
- AI-enhanced steganography research
- Cross-media data hiding experiments

## Development

### Adding New Media Types

1. Create a new steganography module (e.g., `video_stego.py`)
2. Implement `hide_message_in_*` and `extract_message_from_*` functions
3. Add capacity estimation in `utils.py`
4. Update the main application to include the new media type

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- PyDroidX 2025 Innovation Showcase
- OpenAI Whisper for voice recognition
- Streamlit for the web framework
- Android WebView for mobile support

## Support

For issues and questions, please open an issue on the GitHub repository.

---

**Note**: This project is for educational and research purposes. Ensure compliance with local laws and regulations when using steganography techniques. 