import logging
from typing import Optional, Dict, List, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

from app.config.settings import OPENAI_API_KEY, GPT_MODEL, LANGUAGE_TARGET


class TranslationError(Exception):
    """Raised when translation fails"""
    pass


class TranslationService:
    """Handles subtitle translation and optimization for dubbing using GPT"""

    def __init__(self):
        if not OPENAI_API_KEY:
            raise TranslationError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def translate_text(
        self,
        text: str,
        source_language: str = "English",
        target_language: str = "Brazilian Portuguese"
    ) -> str:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_language: Source language name
            target_language: Target language name
            
        Returns:
            Translated text
        """
        try:
            logger.info(f"Translating text to {target_language}")
            
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a professional translator specializing in video dubbing.
Your task is to translate {source_language} text to {target_language} for dubbing purposes.

IMPORTANT RULES:
1. Translate naturally and fluently, not literally
2. Adapt phrases for natural speech patterns
3. Keep sentences short and easy to pronounce
4. Maintain the original meaning and intent
5. Use colloquial language when appropriate
6. Ensure the translation flows naturally when spoken
7. Avoid complex vocabulary that's hard to pronounce
8. Keep approximate timing (translated text shouldn't be drastically longer)
9. Use natural dialogue appropriate for Brazilian Portuguese speakers
10. Return ONLY the translated text, nothing else"""
                    },
                    {
                        "role": "user",
                        "content": f"Translate this {source_language} text for dubbing:\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_text = response.choices[0].message.content.strip()
            logger.info("Translation completed successfully")
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise TranslationError(f"Failed to translate text: {str(e)}")

    def optimize_for_dubbing(
        self,
        segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Optimize translated segments for dubbing synchronization
        
        Args:
            segments: List of segments with timing and translations
            
        Returns:
            List of optimized segments
        """
        try:
            logger.info("Optimizing segments for dubbing")
            
            optimized = []
            
            for segment in segments:
                original_text = segment.get('original_text', '')
                translated_text = segment.get('translated_text', '')
                duration = segment.get('end', 0) - segment.get('start', 0)
                
                # Calculate words per minute for pacing
                word_count = len(translated_text.split())
                wpm = (word_count / duration * 60) if duration > 0 else 0
                
                # Warn if text is too fast for natural speech
                if wpm > 160:
                    logger.warning(f"Segment pacing is fast ({wpm:.0f} wpm). May need adjustment.")
                
                optimized_segment = {
                    "start": segment.get('start', 0),
                    "end": segment.get('end', 0),
                    "duration": duration,
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "word_count": word_count,
                    "estimated_wpm": wpm,
                    "id": segment.get('id', 0)
                }
                
                optimized.append(optimized_segment)
            
            logger.info(f"Optimized {len(optimized)} segments for dubbing")
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing segments: {str(e)}")
            raise TranslationError(f"Failed to optimize segments: {str(e)}")

    def translate_segments(
        self,
        segments: List[Dict[str, Any]],
        source_language: str = "English",
        target_language: str = "Brazilian Portuguese"
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple segments with timing information
        
        Args:
            segments: List of segments with text and timing
            source_language: Source language name
            target_language: Target language name
            
        Returns:
            List of segments with translations
        """
        try:
            logger.info(f"Translating {len(segments)} segments")
            
            translated_segments = []
            
            for i, segment in enumerate(segments):
                original_text = segment.get('text', '')
                
                if not original_text.strip():
                    translated_segments.append({
                        **segment,
                        'translated_text': '',
                        'original_text': original_text
                    })
                    continue
                
                # Translate individual segment
                translated_text = self.translate_text(
                    original_text,
                    source_language,
                    target_language
                )
                
                translated_segments.append({
                    **segment,
                    'translated_text': translated_text,
                    'original_text': original_text
                })
                
                logger.debug(f"Translated segment {i+1}/{len(segments)}")
            
            logger.info(f"All segments translated successfully")
            return translated_segments
            
        except Exception as e:
            logger.error(f"Error translating segments: {str(e)}")
            raise TranslationError(f"Failed to translate segments: {str(e)}")
