"""
Continuity Detector - Detects continuity questions across languages
"""

import re
from typing import Dict, List, Optional, Pattern


class ContinuityDetector:
    """
    Detects continuity questions like "where did we leave off?" in multiple languages.
    """
    
    def __init__(self):
        """Initialize the continuity detector with patterns for different languages."""
        self.patterns: Dict[str, List[Pattern]] = {
            "pt": [
                re.compile(r"onde\s+paramos", re.IGNORECASE),
                re.compile(r"em\s+que\s+(estamos|estávamos)\s+trabalhando", re.IGNORECASE),
                re.compile(r"o\s+que\s+(estamos|estávamos)\s+fazendo", re.IGNORECASE),
                re.compile(r"qual\s+(era|é)\s+o\s+contexto", re.IGNORECASE),
                re.compile(r"continuar\s+(de\s+)?onde\s+paramos", re.IGNORECASE),
                re.compile(r"retomar\s+(de\s+)?onde\s+paramos", re.IGNORECASE),
                re.compile(r"me\s+lembre\s+onde\s+paramos", re.IGNORECASE),
                re.compile(r"me\s+lembre\s+o\s+que\s+estávamos\s+fazendo", re.IGNORECASE),
                re.compile(r"qual\s+era\s+o\s+projeto", re.IGNORECASE),
                re.compile(r"em\s+que\s+ponto\s+estamos", re.IGNORECASE)
            ],
            "en": [
                re.compile(r"where\s+(did\s+we\s+)?left\s+off", re.IGNORECASE),
                re.compile(r"what\s+(were|are)\s+we\s+working\s+on", re.IGNORECASE),
                re.compile(r"what\s+(were|are)\s+we\s+doing", re.IGNORECASE),
                re.compile(r"what('s|\s+is)\s+the\s+context", re.IGNORECASE),
                re.compile(r"continue\s+(from\s+)?where\s+we\s+(left\s+off|were)", re.IGNORECASE),
                re.compile(r"resume\s+(from\s+)?where\s+we\s+(left\s+off|were)", re.IGNORECASE),
                re.compile(r"remind\s+me\s+where\s+we\s+(left\s+off|were)", re.IGNORECASE),
                re.compile(r"remind\s+me\s+what\s+we\s+were\s+doing", re.IGNORECASE),
                re.compile(r"what\s+(was|is)\s+the\s+project", re.IGNORECASE),
                re.compile(r"what\s+point\s+are\s+we\s+at", re.IGNORECASE)
            ],
            "es": [
                re.compile(r"dónde\s+(nos\s+)?quedamos", re.IGNORECASE),
                re.compile(r"en\s+qué\s+estábamos\s+trabajando", re.IGNORECASE),
                re.compile(r"qué\s+estábamos\s+haciendo", re.IGNORECASE),
                re.compile(r"cuál\s+es\s+el\s+contexto", re.IGNORECASE),
                re.compile(r"continuar\s+desde\s+donde\s+quedamos", re.IGNORECASE)
            ],
            "fr": [
                re.compile(r"où\s+(en\s+)?étions-nous", re.IGNORECASE),
                re.compile(r"sur\s+quoi\s+travaillions-nous", re.IGNORECASE),
                re.compile(r"que\s+faisions-nous", re.IGNORECASE),
                re.compile(r"quel\s+est\s+le\s+contexte", re.IGNORECASE),
                re.compile(r"continuer\s+d'où\s+nous\s+étions", re.IGNORECASE)
            ]
        }
    
    def is_continuity_question(self, text: str, languages: Optional[List[str]] = None) -> bool:
        """
        Check if the given text is a continuity question.
        
        Args:
            text: The text to check
            languages: Optional list of language codes to check. If None, all languages are checked.
            
        Returns:
            True if the text is a continuity question, False otherwise
        """
        if not text:
            return False
            
        # If no languages specified, check all languages
        languages = languages or list(self.patterns.keys())
        
        # Check each language's patterns
        for lang in languages:
            if lang not in self.patterns:
                continue
                
            for pattern in self.patterns[lang]:
                if pattern.search(text):
                    return True
        
        return False
    
    def add_pattern(self, language: str, pattern: str) -> None:
        """
        Add a new pattern for detecting continuity questions.
        
        Args:
            language: Language code (e.g., "pt", "en")
            pattern: Regex pattern string
        """
        if language not in self.patterns:
            self.patterns[language] = []
            
        self.patterns[language].append(re.compile(pattern, re.IGNORECASE))
    
    def get_matching_pattern(self, text: str) -> Optional[str]:
        """
        Get the first matching pattern for a text.
        
        Args:
            text: The text to check
            
        Returns:
            The matching pattern string or None if no match
        """
        for lang in self.patterns:
            for pattern in self.patterns[lang]:
                match = pattern.search(text)
                if match:
                    return match.group(0)
        
        return None
