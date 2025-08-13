#!/usr/bin/env python3
"""
Content Models für Dynamic Messe Stand V4
Slide und Präsentations-Management
"""

import json
import os
from datetime import datetime
from core.logger import logger
from core.config import config

class Slide:
    """Repräsentiert eine einzelne Slide"""
    
    def __init__(self, slide_id, title="", content="", layout="text", config_data=None):
        self.slide_id = slide_id
        self.title = title
        self.content = content
        self.layout = layout
        self.config_data = config_data or {}
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.signal_id = f"page_{slide_id}"
    
    def to_dict(self):
        """Konvertiert Slide zu Dictionary"""
        return {
            'slide_id': self.slide_id,
            'title': self.title,
            'content': self.content,
            'layout': self.layout,
            'config_data': self.config_data,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'signal_id': self.signal_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Erstellt Slide aus Dictionary"""
        slide = cls(
            slide_id=data['slide_id'],
            title=data.get('title', ''),
            content=data.get('content', ''),
            layout=data.get('layout', 'text'),
            config_data=data.get('config_data', {})
        )
        
        if 'created_at' in data:
            slide.created_at = datetime.fromisoformat(data['created_at'])
        if 'modified_at' in data:
            slide.modified_at = datetime.fromisoformat(data['modified_at'])
        
        return slide
    
    def update(self, **kwargs):
        """Aktualisiert Slide-Eigenschaften"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.modified_at = datetime.now()

class ContentManager:
    """Verwaltet alle Slides und Content"""
    
    def __init__(self):
        self.slides = {}
        self.current_slide = 1
        self.content_dir = config.content_dir
        self.ensure_content_directory()
        self.load_all_slides()
    
    def ensure_content_directory(self):
        """Stellt sicher, dass das Content-Verzeichnis existiert"""
        if not os.path.exists(self.content_dir):
            os.makedirs(self.content_dir)
            logger.info(f"Content-Verzeichnis erstellt: {self.content_dir}")
    
    def load_all_slides(self):
        """Lädt alle Slides aus dem Content-Verzeichnis"""
        try:
            # Suche nach page_* Ordnern
            for item in os.listdir(self.content_dir):
                item_path = os.path.join(self.content_dir, item)
                if os.path.isdir(item_path) and item.startswith('page_'):
                    try:
                        slide_id = int(item.split('_')[1])
                        self.load_slide(slide_id)
                    except (ValueError, IndexError):
                        logger.warning(f"Ungültiger Slide-Ordner: {item}")
            
            logger.info(f"{len(self.slides)} Slides geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Slides: {e}")
    
    def load_slide(self, slide_id):
        """Lädt eine spezifische Slide"""
        slide_dir = os.path.join(self.content_dir, f"page_{slide_id}")
        config_file = os.path.join(slide_dir, "config.json")
        
        if not os.path.exists(config_file):
            # Erstelle Standard-Slide
            self.create_default_slide(slide_id)
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            slide = Slide(
                slide_id=slide_id,
                title=config_data.get('title', f'Slide {slide_id}'),
                content=config_data.get('content', ''),
                layout=config_data.get('layout', 'text'),
                config_data=config_data
            )
            
            self.slides[slide_id] = slide
            logger.debug(f"Slide {slide_id} geladen")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden von Slide {slide_id}: {e}")
            self.create_default_slide(slide_id)
    
    def create_default_slide(self, slide_id):
        """Erstellt eine Standard-Slide"""
        slide_dir = os.path.join(self.content_dir, f"page_{slide_id}")
        if not os.path.exists(slide_dir):
            os.makedirs(slide_dir)
        
        default_config = {
            "title": f"Slide {slide_id}",
            "content": f"Inhalt für Slide {slide_id}",
            "layout": "text",
            "background_color": "#FFFFFF",
            "text_color": "#000000"
        }
        
        config_file = os.path.join(slide_dir, "config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        slide = Slide(
            slide_id=slide_id,
            title=default_config['title'],
            content=default_config['content'],
            layout=default_config['layout'],
            config_data=default_config
        )
        
        self.slides[slide_id] = slide
        logger.info(f"Standard-Slide {slide_id} erstellt")
    
    def save_slide(self, slide_id):
        """Speichert eine Slide"""
        if slide_id not in self.slides:
            logger.error(f"Slide {slide_id} nicht gefunden")
            return False
        
        slide = self.slides[slide_id]
        slide_dir = os.path.join(self.content_dir, f"page_{slide_id}")
        
        if not os.path.exists(slide_dir):
            os.makedirs(slide_dir)
        
        config_file = os.path.join(slide_dir, "config.json")
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(slide.config_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Slide {slide_id} gespeichert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern von Slide {slide_id}: {e}")
            return False
    
    def get_slide(self, slide_id):
        """Gibt eine spezifische Slide zurück"""
        return self.slides.get(slide_id)
    
    def get_all_slides(self):
        """Gibt alle Slides zurück"""
        return dict(sorted(self.slides.items()))
    
    def create_slide(self, slide_id, title="", content="", layout="text"):
        """Erstellt eine neue Slide"""
        if slide_id in self.slides:
            logger.warning(f"Slide {slide_id} existiert bereits")
            return False
        
        config_data = {
            "title": title or f"Slide {slide_id}",
            "content": content,
            "layout": layout,
            "background_color": "#FFFFFF",
            "text_color": "#000000"
        }
        
        slide = Slide(
            slide_id=slide_id,
            title=config_data['title'],
            content=content,
            layout=layout,
            config_data=config_data
        )
        
        self.slides[slide_id] = slide
        self.save_slide(slide_id)
        logger.info(f"Neue Slide {slide_id} erstellt")
        return True
    
    def delete_slide(self, slide_id):
        """Löscht eine Slide"""
        if slide_id not in self.slides:
            return False
        
        # Lösche aus Memory
        del self.slides[slide_id]
        
        # Lösche Verzeichnis
        slide_dir = os.path.join(self.content_dir, f"page_{slide_id}")
        if os.path.exists(slide_dir):
            import shutil
            shutil.rmtree(slide_dir)
        
        logger.info(f"Slide {slide_id} gelöscht")
        return True
    
    def get_slide_count(self):
        """Gibt die Anzahl der Slides zurück"""
        return len(self.slides)
    
    def set_current_slide(self, slide_id):
        """Setzt die aktuelle Slide"""
        if slide_id in self.slides:
            self.current_slide = slide_id
            logger.debug(f"Aktuelle Slide: {slide_id}")
            return True
        return False

# Globale Content-Manager Instanz
content_manager = ContentManager()