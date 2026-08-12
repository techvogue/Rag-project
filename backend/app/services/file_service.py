import pypdf
import docx2txt
import os
from moviepy import VideoFileClip
import tempfile

async def extract_text_from_document(file_path: str) -> str:
    """
    Extracts text from a document file.
    Supported formats: PDF, DOCX, TXT
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        elif ext == '.docx':
            return docx2txt.process(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text: {str(e)}")


async def extract_audio_from_video(video_file_path: str) -> str:
    """
    Extracts audio from a video file.

    Args:
        video_file_path (str): Path to the video file.

    Returns:
        str: Path to the temporary audio file extracted from the video.
    """
    try:
        # Load the video file
        video = VideoFileClip(video_file_path)
        
        # Extract audio from video
        audio = video.audio
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            audio.write_audiofile(temp_audio_file.name)
            return temp_audio_file.name
    except Exception as e:
        raise RuntimeError(f"Failed to extract audio from video: {str(e)}")
