#!/usr/bin/env python3
"""
Creator Tab für Dynamic Messe Stand V4
Content-Erstellung und -Bearbeitung
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.theme import theme_manager
from core.logger import logger
from models.content import content_manager

class CreatorTab:
    """Creator-Tab für Content-Management"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.visible = False
        self.current_edit_slide = 1
        
        self.create_creator_content()
    
    def create_creator_content(self):
        """Erstellt den PowerPoint-ähnlichen Creator-Tab"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Haupt-Container
        self.container = tk.Frame(self.parent, bg=colors['background_primary'])
        
        # Hauptarbeitsbereich (ohne Ribbon)
        main_workspace = tk.Frame(self.container, bg=colors['background_primary'])
        main_workspace.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Layout: Slide-Panel (links) + Editor (Mitte) + Toolbar+Eigenschaften (rechts)
        main_workspace.grid_columnconfigure(1, weight=3)  # Editor bekommt meisten Platz
        main_workspace.grid_rowconfigure(0, weight=1)
        
        # Slide-Thumbnail Panel (links)
        self.create_slide_panel(main_workspace)
        
        # Haupt-Editor (Mitte)
        self.create_main_editor(main_workspace)
        
        # Toolbar + Eigenschaften-Panel (rechts)
        self.create_sidebar_panel(main_workspace)
        
        # Status-Leiste (unten)
        self.create_status_bar()
    
    def create_ribbon_toolbar(self):
        """Erstellt die PowerPoint-ähnliche Ribbon-Toolbar"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Ribbon-Container - kompakter für 24" Screen
        ribbon_frame = tk.Frame(
            self.container,
            bg=colors['background_secondary'],
            relief='flat',
            bd=0,
            height=90
        )
        ribbon_frame.pack(fill='x', padx=10, pady=(10, 8))
        ribbon_frame.pack_propagate(False)
        
        # Titel-Bereich - kompakter für 24" Screen
        title_frame = tk.Frame(ribbon_frame, bg=colors['background_secondary'])
        title_frame.pack(side='left', fill='y', padx=(15, 25))
        
        title_label = tk.Label(
            title_frame,
            text="✎ BumbleB Story Editor",
            font=fonts['title'],
            fg=colors['accent_primary'],
            bg=colors['background_secondary']
        )
        title_label.pack(anchor='w', pady=(15, 2))
        
        subtitle_label = tk.Label(
            title_frame,
            text="PowerPoint-Style Editor",
            font=fonts['caption'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        )
        subtitle_label.pack(anchor='w')
        
        # Separator
        separator = tk.Frame(ribbon_frame, bg=colors['border_medium'], width=1)
        separator.pack(side='left', fill='y', padx=10, pady=10)
        
        # Aktionen-Gruppe
        actions_frame = tk.Frame(ribbon_frame, bg=colors['background_secondary'])
        actions_frame.pack(side='left', fill='y', padx=10)
        
        # Speichern-Button (prominent) - kompakter für 24" Screen
        save_btn = tk.Button(
            actions_frame,
            text="◉\nSpeichern",
            font=fonts['button'],
            bg=colors['accent_primary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.save_current_slide,
            width=10,
            height=2
        )
        save_btn.pack(side='left', padx=(0, 10), pady=10)
        
        # Vorschau-Button - kompakter für 24" Screen
        preview_btn = tk.Button(
            actions_frame,
            text="◎\nVorschau",
            font=fonts['button'],
            bg=colors['accent_secondary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.preview_slide,
            width=10,
            height=2
        )
        preview_btn.pack(side='left', padx=8, pady=10)
        
        # Separator
        separator2 = tk.Frame(ribbon_frame, bg=colors['border_medium'], width=1)
        separator2.pack(side='left', fill='y', padx=10, pady=10)
        
        # Slide-Navigation
        nav_frame = tk.Frame(ribbon_frame, bg=colors['background_secondary'])
        nav_frame.pack(side='left', fill='y', padx=10)
        
        nav_label = tk.Label(
            nav_frame,
            text="Navigation:",
            font=fonts['label'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        )
        nav_label.pack(anchor='w', pady=(18, 3))
        
        nav_buttons = tk.Frame(nav_frame, bg=colors['background_secondary'])
        nav_buttons.pack(pady=(5, 0))
        
        prev_btn = tk.Button(
            nav_buttons,
            text="◀",
            font=fonts['button'],
            bg=colors['background_tertiary'],
            fg=colors['text_primary'],
            relief='flat',
            bd=0,
            padx=8,
            pady=5,
            cursor='hand2',
            command=self.previous_slide,
            width=3
        )
        prev_btn.pack(side='left', padx=(0, 8))
        
        self.slide_counter = tk.Label(
            nav_buttons,
            text="1/10",
            font=fonts['body'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        self.slide_counter.pack(side='left', padx=8)
        
        next_btn = tk.Button(
            nav_buttons,
            text="▶",
            font=fonts['button'],
            bg=colors['background_tertiary'],
            fg=colors['text_primary'],
            relief='flat',
            bd=0,
            padx=8,
            pady=5,
            cursor='hand2',
            command=self.next_slide,
            width=3
        )
        next_btn.pack(side='left', padx=(8, 0))
    
    def create_slide_panel(self, parent):
        """Erstellt das Slide-Thumbnail Panel (wie PowerPoint)"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Slide-Panel Frame - kompakter für 24" Screen
        panel_frame = tk.Frame(
            parent,
            bg=colors['background_secondary'],
            relief='flat',
            bd=0,
            width=250
        )
        panel_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        panel_frame.grid_propagate(False)
        
        # Panel-Header - größer für 24" Screen
        header_frame = tk.Frame(panel_frame, bg=colors['background_secondary'])
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        header_label = tk.Label(
            header_frame,
            text="▤ BumbleB Folien",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        header_label.pack(anchor='w')
        
        info_label = tk.Label(
            header_frame,
            text="10 Folien verfügbar",
            font=fonts['body'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        )
        info_label.pack(anchor='w', pady=(5, 0))
        
        # Scrollable Thumbnail-Liste
        canvas = tk.Canvas(
            panel_frame,
            bg=colors['background_secondary'],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(panel_frame, orient="vertical", command=canvas.yview)
        self.thumbnail_frame = tk.Frame(canvas, bg=colors['background_secondary'])
        
        self.thumbnail_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.thumbnail_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=(0, 15))
        scrollbar.pack(side="right", fill="y", pady=(0, 15))
        
        # Thumbnails erstellen
        self.create_slide_thumbnails()
    
    def create_slide_thumbnails(self):
        """Erstellt PowerPoint-ähnliche Slide-Thumbnails"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        from models.content import content_manager
        slides = content_manager.get_all_slides()
        
        self.thumbnail_buttons = {}
        
        for i, (slide_id, slide) in enumerate(slides.items()):
            # Thumbnail-Container - größer für 24" Screen
            thumb_container = tk.Frame(
                self.thumbnail_frame,
                bg=colors['background_secondary']
            )
            thumb_container.pack(fill='x', padx=8, pady=5)
            
            # Thumbnail-Button (wie PowerPoint) - größer
            is_active = slide_id == self.current_edit_slide
            bg_color = colors['accent_primary'] if is_active else colors['background_tertiary']
            
            thumb_btn = tk.Button(
                thumb_container,
                text=f"{slide_id}\n{slide.title[:20]}...",
                font=fonts['body'],
                bg=bg_color,
                fg='white' if is_active else colors['text_primary'],
                relief='flat',
                bd=0,
                width=25,
                height=4,
                cursor='hand2',
                command=lambda sid=slide_id: self.load_slide_to_editor(sid),
                justify='left'
            )
            thumb_btn.pack(fill='x', ipady=5)
            
            self.thumbnail_buttons[slide_id] = thumb_btn
    
    def create_main_editor(self, parent):
        """Erstellt den Haupt-Editor (PowerPoint-ähnlich)"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Editor-Frame
        editor_frame = tk.Frame(
            parent,
            bg=colors['background_secondary'],
            relief='flat',
            bd=0
        )
        editor_frame.grid(row=0, column=1, sticky='nsew', padx=10)
        
        # Editor-Header - größer für 24" Screen
        header_frame = tk.Frame(editor_frame, bg=colors['background_secondary'])
        header_frame.pack(fill='x', padx=20, pady=(20, 15))
        
        # Slide-Info - größer
        self.slide_info_label = tk.Label(
            header_frame,
            text="Folie 1: BumbleB - Das automatisierte Shuttle",
            font=fonts['display'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        self.slide_info_label.pack(anchor='w', pady=(0, 10))
        
        # Editor-Tabs (wie PowerPoint) - größer für 24" Screen
        tab_frame = tk.Frame(header_frame, bg=colors['background_secondary'])
        tab_frame.pack(anchor='w', pady=(15, 0))
        
        self.editor_tabs = {}
        tab_names = [('content', 'Inhalt'), ('design', 'Design'), ('layout', 'Layout')]
        
        for tab_id, tab_name in tab_names:
            tab_btn = tk.Button(
                tab_frame,
                text=tab_name,
                font=fonts['large_button'],
                bg=colors['accent_primary'] if tab_id == 'content' else colors['background_tertiary'],
                fg='white' if tab_id == 'content' else colors['text_primary'],
                relief='flat',
                bd=0,
                padx=25,
                pady=12,
                cursor='hand2',
                command=lambda tid=tab_id: self.switch_editor_tab(tid),
                width=12,
                height=2
            )
            tab_btn.pack(side='left', padx=(0, 10))
            self.editor_tabs[tab_id] = tab_btn
        
        # Editor-Content-Bereich - größer für 24" Screen
        self.editor_content = tk.Frame(editor_frame, bg=colors['background_secondary'])
        self.editor_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Standard: Content-Tab anzeigen
        self.current_editor_tab = 'content'
        self.create_content_editor()
    
    def create_content_editor(self):
        """Erstellt den Content-Editor"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Clear existing content
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        # Titel-Editor - größer für 24" Screen
        title_frame = tk.Frame(self.editor_content, bg=colors['background_secondary'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="▣ Folie-Titel:",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.title_entry = tk.Entry(
            title_frame,
            font=fonts['subtitle'],
            bg=colors['background_tertiary'],
            fg=colors['text_primary'],
            relief='flat',
            bd=0,
            insertbackground=colors['text_primary']
        )
        self.title_entry.pack(fill='x', ipady=12)
        
        # Content-Editor
        content_frame = tk.Frame(self.editor_content, bg=colors['background_secondary'])
        content_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        tk.Label(
            content_frame,
            text="▢ Folie-Inhalt:",
            font=fonts['subtitle'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        ).pack(anchor='w', pady=(0, 5))
        
        # Text-Editor mit Toolbar - größer für 24" Screen
        text_toolbar = tk.Frame(content_frame, bg=colors['background_tertiary'], height=50)
        text_toolbar.pack(fill='x', pady=(0, 10))
        text_toolbar.pack_propagate(False)
        
        # Formatierungs-Buttons - größer
        format_buttons = [
            ('B', 'Bold', self.format_bold),
            ('I', 'Italic', self.format_italic),
            ('•', 'Bullet', self.format_bullet)
        ]
        
        for text, tooltip, command in format_buttons:
            btn = tk.Button(
                text_toolbar,
                text=text,
                font=fonts['large_button'],
                bg=colors['background_hover'],
                fg=colors['text_primary'],
                relief='flat',
                bd=0,
                padx=15,
                pady=8,
                cursor='hand2',
                command=command,
                width=4,
                height=2
            )
            btn.pack(side='left', padx=5, pady=8)
        
        # Text-Editor
        text_frame = tk.Frame(content_frame, bg=colors['background_secondary'])
        text_frame.pack(fill='both', expand=True)
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side='right', fill='y')
        
        self.content_text = tk.Text(
            text_frame,
            font=fonts['body'],
            bg=colors['background_tertiary'],
            fg=colors['text_primary'],
            wrap='word',
            relief='flat',
            bd=0,
            insertbackground=colors['text_primary'],
            yscrollcommand=text_scrollbar.set
        )
        self.content_text.pack(side='left', fill='both', expand=True)
        text_scrollbar.config(command=self.content_text.yview)
    
    def create_sidebar_panel(self, parent):
        """Erstellt die kombinierte Toolbar + Eigenschaften Seitenleiste (rechts)"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Sidebar Frame - breiter für Toolbar + Eigenschaften
        sidebar_frame = tk.Frame(
            parent,
            bg=colors['background_secondary'],
            relief='flat',
            bd=0,
            width=320
        )
        sidebar_frame.grid(row=0, column=2, sticky='nsew', padx=(8, 0))
        sidebar_frame.grid_propagate(False)
        
        # Toolbar-Sektion (oben)
        self.create_sidebar_toolbar(sidebar_frame)
        
        # Separator
        separator = tk.Frame(sidebar_frame, bg=colors['border_medium'], height=1)
        separator.pack(fill='x', padx=15, pady=10)
        
        # Eigenschaften-Sektion (unten)
        self.create_properties_section(sidebar_frame)
    
    def create_sidebar_toolbar(self, parent):
        """Erstellt die Toolbar in der Seitenleiste"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Toolbar-Header
        toolbar_header = tk.Frame(parent, bg=colors['background_secondary'])
        toolbar_header.pack(fill='x', padx=15, pady=(15, 10))
        
        header_label = tk.Label(
            toolbar_header,
            text="✎ BumbleB Story Editor",
            font=fonts['title'],
            fg=colors['accent_primary'],
            bg=colors['background_secondary']
        )
        header_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            toolbar_header,
            text="Editor-Werkzeuge",
            font=fonts['caption'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        )
        subtitle_label.pack(anchor='w', pady=(2, 0))
        
        # Aktionen-Gruppe
        actions_section = tk.Frame(parent, bg=colors['background_secondary'])
        actions_section.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(
            actions_section,
            text="Aktionen:",
            font=fonts['subtitle'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        # Apple Silicon Style Speichern-Button
        save_btn = tk.Button(
            actions_section,
            text="◉ Speichern",
            font=fonts['button'],
            bg=colors['accent_primary'],
            fg=colors['text_on_accent'],
            relief='flat',
            bd=0,
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.save_current_slide,
            activebackground=colors['background_hover']
        )
        save_btn.pack(fill='x', pady=(0, 8))
        
        # Vorschau-Button
        preview_btn = tk.Button(
            actions_section,
            text="◎ Vorschau",
            font=fonts['button'],
            bg=colors['accent_secondary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.preview_slide
        )
        preview_btn.pack(fill='x', pady=(0, 10))
        
        # Navigation-Gruppe
        nav_section = tk.Frame(parent, bg=colors['background_secondary'])
        nav_section.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(
            nav_section,
            text="Navigation:",
            font=fonts['subtitle'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        # Navigation-Buttons
        nav_buttons = tk.Frame(nav_section, bg=colors['background_secondary'])
        nav_buttons.pack(fill='x')
        
        prev_btn = tk.Button(
            nav_buttons,
            text="◀ Zurück",
            font=fonts['button'],
            bg=colors['background_tertiary'],
            fg=colors['text_primary'],
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=self.previous_slide
        )
        prev_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        next_btn = tk.Button(
            nav_buttons,
            text="▶ Weiter",
            font=fonts['button'],
            bg=colors['background_tertiary'],
            fg=colors['text_primary'],
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=self.next_slide
        )
        next_btn.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Slide-Zähler
        self.slide_counter = tk.Label(
            nav_section,
            text="1/10",
            font=fonts['body'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        self.slide_counter.pack(pady=(8, 0))
    
    def create_properties_section(self, parent):
        """Erstellt die Eigenschaften-Sektion in der Seitenleiste"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Properties-Header
        props_header = tk.Frame(parent, bg=colors['background_secondary'])
        props_header.pack(fill='x', padx=15, pady=(10, 10))
        
        header_label = tk.Label(
            props_header,
            text="⚙ Eigenschaften",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        header_label.pack(anchor='w')
        
        # Layout-Auswahl - größer für 24" Screen
        layout_frame = tk.Frame(parent, bg=colors['background_secondary'])
        layout_frame.pack(fill='x', padx=15, pady=15)
        
        tk.Label(
            layout_frame,
            text="Layout:",
            font=fonts['subtitle'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.layout_var = tk.StringVar(value="text")
        layout_combo = ttk.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["text", "image_text", "video_text", "fullscreen_image", "fullscreen_video"],
            state="readonly",
            font=fonts['body'],
            height=8
        )
        layout_combo.pack(fill='x', ipady=5)
        
        # Farb-Einstellungen - größer für 24" Screen
        color_frame = tk.Frame(parent, bg=colors['background_secondary'])
        color_frame.pack(fill='x', padx=15, pady=15)
        
        tk.Label(
            color_frame,
            text="Farben:",
            font=fonts['subtitle'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        ).pack(anchor='w', pady=(0, 10))
        
        # Hintergrundfarbe - größer
        bg_color_frame = tk.Frame(color_frame, bg=colors['background_secondary'])
        bg_color_frame.pack(fill='x', pady=5)
        
        tk.Label(
            bg_color_frame,
            text="Hintergrund:",
            font=fonts['body'],
            fg=colors['text_tertiary'],
            bg=colors['background_secondary']
        ).pack(side='left')
        
        self.bg_color_btn = tk.Button(
            bg_color_frame,
            text="⬜",
            font=fonts['subtitle'],
            bg='white',
            relief='flat',
            bd=2,
            width=5,
            height=2,
            cursor='hand2',
            command=self.choose_bg_color
        )
        self.bg_color_btn.pack(side='right')
        
        # Textfarbe - größer
        text_color_frame = tk.Frame(color_frame, bg=colors['background_secondary'])
        text_color_frame.pack(fill='x', pady=5)
        
        tk.Label(
            text_color_frame,
            text="Text:",
            font=fonts['body'],
            fg=colors['text_tertiary'],
            bg=colors['background_secondary']
        ).pack(side='left')
        
        self.text_color_btn = tk.Button(
            text_color_frame,
            text="⬛",
            font=fonts['subtitle'],
            bg='black',
            fg='white',
            relief='flat',
            bd=2,
            width=5,
            height=2,
            cursor='hand2',
            command=self.choose_text_color
        )
        self.text_color_btn.pack(side='right')
    
    def create_status_bar(self):
        """Erstellt die Status-Leiste (unten) - größer für 24" Screen"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        status_frame = tk.Frame(
            self.container,
            bg=colors['background_tertiary'],
            height=40
        )
        status_frame.pack(fill='x', padx=15, pady=(0, 15))
        status_frame.pack_propagate(False)
        
        # Status-Text - größer
        self.status_label = tk.Label(
            status_frame,
            text="Bereit - Folie 1 von 10 ausgewählt",
            font=fonts['body'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        )
        self.status_label.pack(side='left', padx=15, pady=10)
        
        # Zoom-Level (rechts) - größer
        zoom_label = tk.Label(
            status_frame,
            text="100%",
            font=fonts['body'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        )
        zoom_label.pack(side='right', padx=15, pady=10)
    
    def create_editor(self, parent):
        """Erstellt den Editor-Bereich"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Editor Frame
        editor_frame = ttk.Frame(parent, style='Card.TFrame')
        editor_frame.grid(row=0, column=1, sticky='nsew')
        
        # Titel
        editor_title = tk.Label(
            editor_frame,
            text="📝 Editor",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        editor_title.pack(pady=(15, 10))
        
        # Editor-Container
        editor_container = tk.Frame(editor_frame, bg=colors['background_tertiary'])
        editor_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Slide-Info
        info_frame = tk.Frame(editor_container, bg=colors['background_tertiary'])
        info_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            info_frame,
            text="Slide ID:",
            font=fonts['label'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        ).pack(side='left')
        
        self.slide_id_label = tk.Label(
            info_frame,
            text="1",
            font=fonts['body'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        self.slide_id_label.pack(side='left', padx=(5, 0))
        
        # Titel-Editor
        tk.Label(
            editor_container,
            text="Titel:",
            font=fonts['label'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        ).pack(anchor='w', pady=(10, 5))
        
        self.title_entry = tk.Entry(
            editor_container,
            font=fonts['body'],
            bg=colors['background_secondary'],
            fg=colors['text_primary']
        )
        self.title_entry.pack(fill='x', pady=(0, 10))
        
        # Content-Editor
        tk.Label(
            editor_container,
            text="Inhalt:",
            font=fonts['label'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        ).pack(anchor='w', pady=(0, 5))
        
        # Text-Editor mit Scrollbar
        text_frame = tk.Frame(editor_container, bg=colors['background_tertiary'])
        text_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side='right', fill='y')
        
        self.content_text = tk.Text(
            text_frame,
            font=fonts['body'],
            bg=colors['background_secondary'],
            fg=colors['text_primary'],
            wrap='word',
            yscrollcommand=text_scrollbar.set
        )
        self.content_text.pack(side='left', fill='both', expand=True)
        
        text_scrollbar.config(command=self.content_text.yview)
        
        # Layout-Auswahl
        layout_frame = tk.Frame(editor_container, bg=colors['background_tertiary'])
        layout_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            layout_frame,
            text="Layout:",
            font=fonts['label'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        ).pack(side='left')
        
        self.layout_var = tk.StringVar(value="text")
        layout_combo = ttk.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["text", "image_text", "video_text", "fullscreen_image", "fullscreen_video"],
            state="readonly"
        )
        layout_combo.pack(side='left', padx=(10, 0))
        
        # Speichern Button
        save_btn = tk.Button(
            editor_container,
            text="💾 Speichern",
            font=fonts['button'],
            bg=colors['accent_primary'],
            fg='white',
            padx=20,
            pady=10,
            command=self.save_current_slide
        )
        save_btn.pack(pady=(10, 0))
        
        # Erste Slide laden
        self.load_slide_to_editor(1)
    
    def refresh_slide_list(self):
        """Aktualisiert die Slide-Thumbnails"""
        # Thumbnails neu erstellen falls nötig
        if hasattr(self, 'thumbnail_frame'):
            # Clear existing thumbnails
            for widget in self.thumbnail_frame.winfo_children():
                widget.destroy()
            
            # Recreate thumbnails
            self.create_slide_thumbnails()
    
    def on_slide_select(self, event):
        """Behandelt Slide-Auswahl"""
        selection = self.slide_listbox.curselection()
        if selection:
            # Slide-ID aus der Auswahl extrahieren
            selected_text = self.slide_listbox.get(selection[0])
            slide_id = int(selected_text.split(':')[0].replace('Slide ', ''))
            self.load_slide_to_editor(slide_id)
    
    def load_slide_to_editor(self, slide_id):
        """Lädt eine Slide in den PowerPoint-ähnlichen Editor"""
        from models.content import content_manager
        slide = content_manager.get_slide(slide_id)
        
        if slide:
            self.current_edit_slide = slide_id
            
            # Felder füllen (falls vorhanden)
            if hasattr(self, 'title_entry'):
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, slide.title)
            
            if hasattr(self, 'content_text'):
                self.content_text.delete('1.0', tk.END)
                self.content_text.insert('1.0', slide.content)
            
            if hasattr(self, 'layout_var'):
                self.layout_var.set(slide.layout)
            
            # UI-Updates
            self.update_thumbnail_selection()
            self.update_slide_counter()
            
            logger.debug(f"Slide {slide_id} in PowerPoint-Editor geladen")
        else:
            # Neue Slide erstellen
            content_manager.create_slide(slide_id)
            self.load_slide_to_editor(slide_id)
    
    def save_current_slide(self):
        """Speichert die aktuelle Slide"""
        slide = content_manager.get_slide(self.current_edit_slide)
        
        if slide:
            # Daten aus Editor lesen
            new_title = self.title_entry.get()
            new_content = self.content_text.get('1.0', tk.END).strip()
            new_layout = self.layout_var.get()
            
            # Slide aktualisieren
            slide.update(
                title=new_title,
                content=new_content,
                layout=new_layout
            )
            
            # Config-Data aktualisieren
            slide.config_data.update({
                'title': new_title,
                'content': new_content,
                'layout': new_layout
            })
            
            # Speichern
            if content_manager.save_slide(self.current_edit_slide):
                messagebox.showinfo("Erfolg", f"Slide {self.current_edit_slide} gespeichert!")
                self.refresh_slide_list()
            else:
                messagebox.showerror("Fehler", "Slide konnte nicht gespeichert werden!")
    
    # PowerPoint-ähnliche Funktionen
    
    def switch_editor_tab(self, tab_id):
        """Wechselt zwischen Editor-Tabs"""
        colors = theme_manager.get_colors()
        
        # Alle Tabs deaktivieren
        for tid, btn in self.editor_tabs.items():
            if tid == tab_id:
                btn.configure(bg=colors['accent_primary'], fg='white')
            else:
                btn.configure(bg=colors['background_tertiary'], fg=colors['text_primary'])
        
        self.current_editor_tab = tab_id
        
        # Content basierend auf Tab laden
        if tab_id == 'content':
            self.create_content_editor()
        elif tab_id == 'design':
            self.create_design_editor()
        elif tab_id == 'layout':
            self.create_layout_editor()
    
    def create_design_editor(self):
        """Erstellt den Design-Editor"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Clear existing content
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        design_label = tk.Label(
            self.editor_content,
            text="🎨 Design-Optionen",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        design_label.pack(pady=20)
        
        info_label = tk.Label(
            self.editor_content,
            text="Design-Funktionen werden in einer zukünftigen Version verfügbar sein.",
            font=fonts['body'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        )
        info_label.pack()
    
    def create_layout_editor(self):
        """Erstellt den Layout-Editor"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Clear existing content
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        layout_label = tk.Label(
            self.editor_content,
            text="📐 Layout-Optionen",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        layout_label.pack(pady=20)
        
        info_label = tk.Label(
            self.editor_content,
            text="Layout-Funktionen werden in einer zukünftigen Version verfügbar sein.",
            font=fonts['body'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary']
        )
        info_label.pack()
    
    def previous_slide(self):
        """Geht zur vorherigen Slide"""
        if self.current_edit_slide > 1:
            self.load_slide_to_editor(self.current_edit_slide - 1)
    
    def next_slide(self):
        """Geht zur nächsten Slide"""
        if self.current_edit_slide < 10:
            self.load_slide_to_editor(self.current_edit_slide + 1)
    
    def preview_slide(self):
        """Zeigt Slide-Vorschau"""
        from tkinter import messagebox
        slide = content_manager.get_slide(self.current_edit_slide)
        if slide:
            preview_text = f"Vorschau - Folie {self.current_edit_slide}\n\n"
            preview_text += f"Titel: {slide.title}\n\n"
            preview_text += f"Inhalt:\n{slide.content}"
            messagebox.showinfo("Slide-Vorschau", preview_text)
    
    def format_bold(self):
        """Formatiert Text fett"""
        try:
            current_tags = self.content_text.tag_names("sel.first")
            if "bold" in current_tags:
                self.content_text.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.content_text.tag_add("bold", "sel.first", "sel.last")
                self.content_text.tag_config("bold", font=self.main_window.fonts['body'] + ('bold',))
        except:
            pass
    
    def format_italic(self):
        """Formatiert Text kursiv"""
        try:
            current_tags = self.content_text.tag_names("sel.first")
            if "italic" in current_tags:
                self.content_text.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.content_text.tag_add("italic", "sel.first", "sel.last")
                self.content_text.tag_config("italic", font=self.main_window.fonts['body'] + ('italic',))
        except:
            pass
    
    def format_bullet(self):
        """Fügt Bullet-Point hinzu"""
        try:
            cursor_pos = self.content_text.index(tk.INSERT)
            line_start = cursor_pos.split('.')[0] + '.0'
            line_content = self.content_text.get(line_start, line_start + ' lineend')
            
            if not line_content.strip().startswith('•'):
                self.content_text.insert(line_start, '• ')
        except:
            pass
    
    def choose_bg_color(self):
        """Öffnet Farbauswahl für Hintergrund"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Hintergrundfarbe wählen")
        if color[1]:
            self.bg_color_btn.configure(bg=color[1])
    
    def choose_text_color(self):
        """Öffnet Farbauswahl für Text"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Textfarbe wählen")
        if color[1]:
            self.text_color_btn.configure(bg=color[1])
    
    def update_thumbnail_selection(self):
        """Aktualisiert die Thumbnail-Auswahl"""
        colors = theme_manager.get_colors()
        
        for slide_id, btn in self.thumbnail_buttons.items():
            if slide_id == self.current_edit_slide:
                btn.configure(bg=colors['accent_primary'], fg='white')
            else:
                btn.configure(bg=colors['background_tertiary'], fg=colors['text_primary'])
    
    def update_slide_counter(self):
        """Aktualisiert den Slide-Zähler"""
        self.slide_counter.configure(text=f"{self.current_edit_slide}/10")
        self.slide_info_label.configure(
            text=f"Folie {self.current_edit_slide}: {content_manager.get_slide(self.current_edit_slide).title if content_manager.get_slide(self.current_edit_slide) else 'Unbekannt'}"
        )
        self.status_label.configure(
            text=f"Bereit - Folie {self.current_edit_slide} von 10 ausgewählt"
        )
    
    def show(self):
        """Zeigt den Tab"""
        if not self.visible:
            self.container.pack(fill='both', expand=True)
            self.visible = True
            self.refresh_slide_list()
            logger.debug("Creator-Tab angezeigt")
    
    def hide(self):
        """Versteckt den Tab"""
        if self.visible:
            self.container.pack_forget()
            self.visible = False
            logger.debug("Creator-Tab versteckt")