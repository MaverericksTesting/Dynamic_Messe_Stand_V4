# models/slide.py
"""
Datenmodelle für Folien/Slides
"""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class Slide:
    """Datenmodell für eine Präsentations-Folie"""
    id: int
    name: str
    icon: str
    content_type: str
    title: str = ""
    subtitle: str = ""
    text_content: str = ""
    background_image: str = ""
    video: str = ""
    images: List[str] = field(default_factory=list)
    layout: str = "text_only"  # text_only, image_text, video_text, fullscreen_image, fullscreen_video
    
    @property
    def folder_name(self) -> str:
        """Ordnername für diese Folie"""
        return f"page_{self.id}_{self.content_type}"
    
    def get_folder_path(self, base_dir: Path) -> Path:
        """Vollständiger Pfad zum Folien-Ordner"""
        return base_dir / self.folder_name
    
    def get_config_path(self, base_dir: Path) -> Path:
        """Pfad zur config.json Datei"""
        return self.get_folder_path(base_dir) / "config.json"
    
    def to_dict(self) -> dict:
        """Konvertiere zu Dictionary für JSON-Serialisierung"""
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "background_image": self.background_image,
            "video": self.video,
            "text_content": self.text_content,
            "images": self.images,
            "layout": self.layout
        }
    
    @classmethod
    def from_dict(cls, slide_id: int, name: str, icon: str, content_type: str, data: dict) -> 'Slide':
        """Erstelle Slide aus Dictionary"""
        return cls(
            id=slide_id,
            name=name,
            icon=icon,
            content_type=content_type,
            title=data.get("title", ""),
            subtitle=data.get("subtitle", ""),
            text_content=data.get("text_content", ""),
            background_image=data.get("background_image", ""),
            video=data.get("video", ""),
            images=data.get("images", []),
            layout=data.get("layout", "text_only")
        )