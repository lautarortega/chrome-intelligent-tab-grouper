import ollama
import logging
from typing import List
from app.schemas.tabs import Tab
from app.core.config import settings

logger = logging.getLogger(__name__)

class TitleGeneratorService:
    def __init__(self, model_name: str = settings.OLLAMA_MODEL):
        self.model_name = model_name

    def generate_title(self, tabs: List[Tab]) -> str:
        titles = [tab.title for tab in tabs]
        urls = [tab.url for tab in tabs]
        
        prompt = f"""
        Generate a title for a group of tabs with the following titles: {titles} and urls: {urls}
        Only return the title. Make sure it is short and concise. Not more than 3 words, best if 2 or 1 word.
        """
        try:
            logger.info(f"Requesting title for {len(tabs)} tabs using model {self.model_name}")
            response = ollama.generate(model=self.model_name, prompt=prompt)
            title = response['response'].strip()
            logger.info(f"Generated title: {title}")
            return title
        except Exception as e:
            logger.error(f"Error generating title with Ollama: {str(e)}")
            # Fallback or log error
            return "New Group"
