# services/storage.py
"""
Persistierung von Folien-Daten
"""
import json
from pathlib import Path
from typing import Dict, Optional
from models.slide import Slide
from core.config import config
from core.logger import logger

class StorageService:
    """Service für Laden/Speichern von Folien-Daten"""
    
    def __init__(self, content_dir: Path = None):
        self.content_dir = content_dir or config.CONTENT_DIR
        self.ensure_content_structure()
    
    def ensure_content_structure(self):
        """Erstelle Content-Ordnerstruktur"""
        if not self.content_dir.exists():
            self.content_dir.mkdir(parents=True)
            logger.info(f"Content-Verzeichnis erstellt: {self.content_dir}")
        
        # Erstelle Ordner für jede Folie
        for slide_id, slide_info in config.SLIDES.items():
            slide_dir = self.content_dir / f"page_{slide_id}_{slide_info['content_type']}"
            if not slide_dir.exists():
                slide_dir.mkdir()
                
                # Erstelle Standard-config.json
                default_config = {
                    "title": slide_info['name'],
                    "subtitle": f"Folie {slide_id} - {slide_info['name']}",
                    "background_image": "",
                    "video": "",
                    "text_content": f"Willkommen auf {slide_info['name']}\n\nHier können Sie Inhalte hinzufügen:\n• Bilder\n• Videos\n• Texte\n\nBearbeiten Sie die config.json in:\n{slide_dir}",
                    "images": [],
                    "layout": "text_only"
                }
                
                config_path = slide_dir / "config.json"
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Standard-Konfiguration erstellt: {config_path}")
    
    def load_slide(self, slide_id: int) -> Optional[Slide]:
        """Lade eine einzelne Folie"""
        if slide_id not in config.SLIDES:
            logger.warning(f"Unbekannte Folien-ID: {slide_id}")
            return None
        
        slide_info = config.SLIDES[slide_id]
        slide_dir = self.content_dir / f"page_{slide_id}_{slide_info['content_type']}"
        config_path = slide_dir / "config.json"
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Fallback-Daten
                data = {
                    "title": slide_info['name'],
                    "subtitle": f"Folie {slide_id}",
                    "text_content": f"Folie {slide_id} - Inhalt wird geladen...",
                    "layout": "text_only"
                }
            
            slide = Slide.from_dict(
                slide_id=slide_id,
                name=slide_info['name'],
                icon=slide_info['icon'],
                content_type=slide_info['content_type'],
                data=data
            )
            
            logger.debug(f"Folie {slide_id} geladen: {slide.title}")
            return slide
            
        except Exception as e:
            logger.error(f"Fehler beim Laden von Folie {slide_id}: {e}")
            return None
    
    def load_all_slides(self) -> Dict[int, Slide]:
        """Lade alle Folien"""
        slides = {}
        
        for slide_id in config.SLIDES.keys():
            slide = self.load_slide(slide_id)
            if slide:
                slides[slide_id] = slide
        
        logger.info(f"{len(slides)} Folien geladen")
        return slides
    
    def save_slide(self, slide: Slide) -> bool:
        """Speichere eine Folie"""
        try:
            slide_dir = slide.get_folder_path(self.content_dir)
            if not slide_dir.exists():
                slide_dir.mkdir(parents=True)
            
            config_path = slide.get_config_path(self.content_dir)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(slide.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Folie {slide.id} gespeichert: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern von Folie {slide.id}: {e}")
            return False
    
    def get_slide_files(self, slide_id: int) -> Dict[str, list]:
        """Liste alle Dateien in einem Folien-Ordner"""
        if slide_id not in config.SLIDES:
            return {"images": [], "videos": [], "other": []}
        
        slide_info = config.SLIDES[slide_id]
        slide_dir = self.content_dir / f"page_{slide_id}_{slide_info['content_type']}"
        
        if not slide_dir.exists():
            return {"images": [], "videos": [], "other": []}
        
        files = {"images": [], "videos": [], "other": []}
        
        for file_path in slide_dir.iterdir():
            if file_path.is_file() and file_path.name != "config.json":
                ext = file_path.suffix.lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    files["images"].append(file_path.name)
                elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    files["videos"].append(file_path.name)
                else:
                    files["other"].append(file_path.name)
        
        return files