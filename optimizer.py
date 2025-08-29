import sys
import asyncio
import aiohttp
import json
import os
import keyring
from typing import List, Dict
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                              QHBoxLayout, QWidget, QTextEdit, QPushButton, 
                              QLabel, QProgressBar, QSplitter, QLineEdit,
                              QMessageBox, QScrollArea)
from PySide6.QtCore import QThread, Signal, Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QPixmap, QPainter, QPen, QFontDatabase
from PySide6.QtSvg import QSvgRenderer
import requests
from bs4 import BeautifulSoup
import re

class SearchResult:
    def __init__(self, title: str, description: str, url: str = ""):
        self.title = title
        self.description = description
        self.url = url

class SEOWorkerThread(QThread):
    progress_updated = Signal(str)
    finished = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, text: str, claude_api_key: str):
        super().__init__()
        self.text = text
        self.claude_api_key = claude_api_key
        self.search_results: List[SearchResult] = []
    
    def run(self):
        try:
            # Step 1: Extract search terms using Claude
            self.progress_updated.emit("Extracting search terms using Claude...")
            search_terms = self.extract_search_terms(self.text)
            
            # Step 2: Perform Google searches
            self.progress_updated.emit("Performing Google searches...")
            self.perform_searches(search_terms)
            
            # Step 3: SEO optimize using Claude
            self.progress_updated.emit("Optimizing content with Claude...")
            optimized_text = self.seo_optimize_text(self.text, self.search_results)
            
            self.finished.emit(optimized_text)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def extract_search_terms(self, text: str) -> List[str]:
        """Use Claude API to extract relevant search terms from text"""
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.claude_api_key,
            'anthropic-version': '2023-06-01'
        }
        
        prompt = f"""
        Analyze the following text and extract 5-10 relevant search terms that would help with SEO optimization. 
        Focus on key topics, important keywords, and phrases that people might search for.
        Return only the search terms, one per line, without numbering or explanation.
        
        Text: {text}
        """
        
        data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 1000,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        response = requests.post('https://api.anthropic.com/v1/messages', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            content = result['content'][0]['text']
            search_terms = [term.strip() for term in content.split('\n') if term.strip()]
            return search_terms[:10]  # Limit to 10 terms
        else:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")
    
    def perform_searches(self, search_terms: List[str]):
        """Perform Google searches and extract titles/descriptions"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for term in search_terms:
            try:
                self.progress_updated.emit(f"Searching for: {term}")
                
                # Use DuckDuckGo as it's more scraping-friendly than Google
                search_url = f"https://duckduckgo.com/html/?q={term.replace(' ', '+')}"
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract search results
                    results = soup.find_all('div', class_='result')[:5]  # First 5 results
                    
                    for result in results:
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem and snippet_elem:
                            title = title_elem.get_text(strip=True)
                            description = snippet_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            
                            self.search_results.append(SearchResult(title, description, url))
                
            except Exception as e:
                self.progress_updated.emit(f"Search error for '{term}': {str(e)}")
                continue
    
    def seo_optimize_text(self, original_text: str, search_results: List[SearchResult]) -> str:
        """Use Claude to optimize text based on search results"""
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.claude_api_key,
            'anthropic-version': '2023-06-01'
        }
        
        # Prepare search results context
        search_context = "\n".join([
            f"Title: {result.title}\nDescription: {result.description}\n"
            for result in search_results[:20]  # Limit context size
        ])
        
        prompt = f"""
        Please optimize the following text for SEO based on the search results provided. 
        Use the titles and descriptions as reference to understand what content performs well for related topics.
        
        Improve the text by:
        1. Adding relevant keywords naturally
        2. Improving readability and structure
        3. Making it more engaging
        4. Ensuring it addresses topics that appear frequently in the search results
        
        Keep the core message and style intact while making it more SEO-friendly. Keep the word count almost same plus or minus a few words. Create a few variations of the SEO optimised text.
        
        Original Text:
        {original_text}
        
        Search Results for Reference:
        {search_context}
        
        Output just the optimised texts, do not output anything else.
        """
        
        data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 2000,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        response = requests.post('https://api.anthropic.com/v1/messages', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")

class SEOOptimizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEO Optimizer with Claude API")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load custom fonts
        self.load_custom_fonts()
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Compact header with logo and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(2)  # Reduced spacing between logo and text
        
        # Create SVG logo using QLabel with rendered SVG
        logo_label = QLabel()
        logo_label.setFixedSize(30, 30)
        logo_label.setCursor(Qt.PointingHandCursor)
        logo_label.mousePressEvent = lambda event: QDesktopServices.openUrl(QUrl("https://day-dream.studio"))
        
        # Load and render SVG
        svg_pixmap = self.load_svg_as_pixmap("assets/logo.svg", 30, 30)
        if svg_pixmap:
            logo_label.setPixmap(svg_pixmap)
        else:
            # Fallback to programmatic logo if SVG fails
            logo_label.setPixmap(self.create_logo(40))
        
        header_layout.addWidget(logo_label)
        
        # Title with tighter spacing
        title_label = QLabel("SEO Optimiser from day-dream")
        title_label.setObjectName("title")
        title_label.setFont(QFont(self.get_font_family(), 24))
        title_label.setContentsMargins(0, 0, 0, 0)  # Remove margins
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()  # Push everything to the left
        
        # Wrap header in a widget with fixed height
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setFixedHeight(50)  # Fixed height to prevent expansion
        layout.addWidget(header_widget)
        
        # API Key input with save functionality
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("Claude API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your Claude API key")
        api_layout.addWidget(self.api_key_input)
        
        # Save/Load API key buttons
        self.save_key_btn = QPushButton("Save Key")
        self.save_key_btn.setMaximumWidth(100)
        self.save_key_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(self.save_key_btn)
        
        self.load_key_btn = QPushButton("Load Key")
        self.load_key_btn.setMaximumWidth(100)
        self.load_key_btn.clicked.connect(self.load_api_key)
        api_layout.addWidget(self.load_key_btn)
        
        layout.addLayout(api_layout)
        
        # Load API key on startup
        self.load_api_key(show_message=False)
        
        # Create splitter for input/output
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Input
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        input_layout.addWidget(QLabel("Original Text:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your text here to optimize for SEO...")
        input_layout.addWidget(self.input_text)
        
        # Process button
        self.process_btn = QPushButton("Optimize for SEO")
        self.process_btn.clicked.connect(self.start_processing)
        input_layout.addWidget(self.process_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        input_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        input_layout.addWidget(self.status_label)
        
        splitter.addWidget(input_widget)
        
        # Right side - Output
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        output_layout.addWidget(QLabel("Optimized Text:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        
        splitter.addWidget(output_widget)
        
        # Set splitter proportions
        splitter.setSizes([600, 600])
        layout.addWidget(splitter)
        
        # Style the interface with dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel[objectName="title"] {
                color: #FFFFFF;
                font-weight: bold;
                margin-left: 15px;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
                font-family: '""" + self.get_font_family() + """';
                color: #ffffff;
                selection-background-color: #4A9EFF;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                border: 1px solid #66B3FF;
                background-color: #333333;
            }
            QPushButton {
                background-color: #4A9EFF;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-family: '""" + self.get_font_family() + """';
                border-radius: 6px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #66B3FF;
            }
            QPushButton:pressed {
                background-color: #3385FF;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton[objectName="small_button"] {
                max-width: 100px;
                padding: 8px 16px;
                font-size: 12px;
                min-height: 16px;
            }
            QLabel {
                color: #ffffff;
                font-weight: 500;
                font-size: 13px;
                font-family: '""" + self.get_font_family() + """';
            }
            QLineEdit {
                background-color: #2d2d2d;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-family: '""" + self.get_font_family() + """';
                color: #ffffff;
                selection-background-color: #4A9EFF;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #66B3FF;
                background-color: #333333;
            }
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #4A9EFF;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4A9EFF;
                border-radius: 3px;
            }
            QSplitter::handle {
                background-color: transparent;
                width: 0px;
            }
            QSplitter::handle:hover {
                background-color: transparent;
            }
            QMessageBox {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QSvgWidget {
                background: transparent;
            }
            QSvgWidget:hover {
                opacity: 0.8;
            }
            QMessageBox QPushButton {
                background-color: #4A9EFF;
                min-width: 80px;
            }
        """)
    
        # Set object names for styling
        self.save_key_btn.setObjectName("small_button")
        self.load_key_btn.setObjectName("small_button")
    
    def load_svg_as_pixmap(self, svg_path: str, width: int, height: int) -> QPixmap:
        """Load SVG file and render it as a QPixmap"""
        try:
            if not os.path.exists(svg_path):
                print(f"SVG file not found: {svg_path}")
                return None
            
            renderer = QSvgRenderer(svg_path)
            if not renderer.isValid():
                print(f"Invalid SVG file: {svg_path}")
                return None
            
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return pixmap
            
        except Exception as e:
            print(f"Error loading SVG: {e}")
            return None
    
    def load_custom_fonts(self):
        """Load custom fonts from files or use system fonts"""
        # Load Manrope-Regular font
        font_id = QFontDatabase.addApplicationFont("assets/Manrope-Regular.ttf")
        if font_id != -1:
            self.custom_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Successfully loaded custom font: {self.custom_font_family}")
        else:
            print("Failed to load custom font, using system font fallback")
            self.custom_font_family = self.get_best_available_font()
    
    def get_best_available_font(self):
        """Get the best available font from a list of preferences"""
        preferred_fonts = [
            "Inter",           # Modern, clean
            "SF Pro Display",  # macOS
            "Segoe UI",        # Windows
            "Ubuntu",          # Linux
            "Roboto",          # Cross-platform
            "Arial",           # Universal fallback
        ]
        
        available_fonts = QFontDatabase.families()
        
        for font in preferred_fonts:
            if font in available_fonts:
                return font
        
        return "Arial"  # Ultimate fallback
    
    def get_font_family(self):
        """Get the current font family"""
        return getattr(self, 'custom_font_family', 'Inter')
    
    def create_logo(self, size=40):
        """Create a simple logo with 'DD' text in a blue circle"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw blue circle
        painter.setBrush(Qt.blue)
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawEllipse(2, 2, size-4, size-4)
        
        # Draw "DD" text with custom font
        painter.setPen(Qt.white)
        font_size = max(size // 3, 12)
        painter.setFont(QFont(self.get_font_family(), font_size, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "DD")
        
        painter.end()
        return pixmap
    
    def save_api_key(self):
        """Save API key securely using keyring"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key before saving.")
            return
        
        try:
            # Save to system keyring
            keyring.set_password("seo_optimizer", "claude_api_key", api_key)
            QMessageBox.information(self, "Success", "API key saved securely!")
            
            # Update button text temporarily
            original_text = self.save_key_btn.text()
            self.save_key_btn.setText("Saved ✓")
            self.save_key_btn.setEnabled(False)
            
            # Reset button after 2 seconds
            def reset_button():
                self.save_key_btn.setText(original_text)
                self.save_key_btn.setEnabled(True)
            
            # Use QTimer for the reset
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, reset_button)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API key:\n{str(e)}")
    
    def load_api_key(self, show_message=True):
        """Load API key securely from keyring"""
        try:
            # Load from system keyring
            api_key = keyring.get_password("seo_optimizer", "claude_api_key")
            
            if api_key:
                self.api_key_input.setText(api_key)
                if show_message:
                    QMessageBox.information(self, "Success", "API key loaded successfully!")
                
                # Update button text temporarily
                original_text = self.load_key_btn.text()
                self.load_key_btn.setText("Loaded ✓")
                self.load_key_btn.setEnabled(False)
                
                # Reset button after 2 seconds
                def reset_button():
                    self.load_key_btn.setText(original_text)
                    self.load_key_btn.setEnabled(True)
                
                from PySide6.QtCore import QTimer
                QTimer.singleShot(2000, reset_button)
                
            else:
                if show_message:
                    QMessageBox.information(self, "Info", "No saved API key found.")
                    
        except Exception as e:
            if show_message:
                QMessageBox.critical(self, "Error", f"Failed to load API key:\n{str(e)}")
    
    def start_processing(self):
        text = self.input_text.toPlainText().strip()
        api_key = self.api_key_input.text().strip()
        
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter text to optimize.")
            return
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter your Claude API key.")
            return
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.output_text.clear()
        
        # Start worker thread
        self.worker = SEOWorkerThread(text, api_key)
        self.worker.progress_updated.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error_occurred.connect(self.processing_error)
        self.worker.start()
    
    def update_status(self, message: str):
        self.status_label.setText(message)
    
    def processing_finished(self, optimized_text: str):
        self.output_text.setPlainText(optimized_text)
        self.status_label.setText("Optimization completed successfully!")
        self.reset_ui()
    
    def processing_error(self, error_message: str):
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_message}")
        self.status_label.setText("Error occurred during processing.")
        self.reset_ui()
    
    def reset_ui(self):
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("SEO Optimizer")
    app.setApplicationVersion("1.0")
    
    window = SEOOptimizerApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()