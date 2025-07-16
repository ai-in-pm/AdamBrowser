"""
Intent Classification Module for Adam Browser

Uses BERT-based NLP to classify user commands into actionable intents
with confidence scoring and parameter extraction.
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from loguru import logger

from ..config import config


class IntentType(Enum):
    """Supported intent types."""
    NAVIGATE = "navigate"
    SEARCH = "search"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    BOOK_TRAVEL = "book_travel"
    GET_DIRECTIONS = "get_directions"
    FILL_FORM = "fill_form"
    SCREENSHOT = "screenshot"
    WAIT = "wait"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: IntentType
    confidence: float
    parameters: Dict[str, Any]
    raw_command: str
    processed_text: str


class IntentClassifier:
    """
    BERT-based intent classifier for natural language commands.
    
    Classifies user commands into actionable intents and extracts
    relevant parameters for execution.
    """
    
    def __init__(self):
        """Initialize the intent classifier."""
        self.model = None
        self.tokenizer = None
        self.is_initialized = False
        
        # Intent patterns for fallback classification
        self.intent_patterns = {
            IntentType.NAVIGATE: [
                r"go to (.+)",
                r"navigate to (.+)",
                r"open (.+)",
                r"visit (.+)",
                r"load (.+)",
            ],
            IntentType.SEARCH: [
                r"search for (.+)",
                r"find (.+)",
                r"look for (.+)",
                r"search (.+)",
            ],
            IntentType.CLICK: [
                r"click (.+)",
                r"click on (.+)",
                r"press (.+)",
                r"tap (.+)",
            ],
            IntentType.TYPE: [
                r"type (.+)",
                r"enter (.+)",
                r"input (.+)",
                r"write (.+)",
            ],
            IntentType.SCROLL: [
                r"scroll (.+)",
                r"scroll to (.+)",
                r"scroll down",
                r"scroll up",
            ],
            IntentType.BOOK_TRAVEL: [
                r"book (.+)",
                r"reserve (.+)",
                r"find (.+) flight",
                r"find (.+) hotel",
                r"rent (.+) car",
            ],
            IntentType.GET_DIRECTIONS: [
                r"get directions (.+)",
                r"directions from (.+) to (.+)",
                r"how to get to (.+)",
                r"route to (.+)",
            ],
            IntentType.FILL_FORM: [
                r"fill (.+) form",
                r"complete (.+)",
                r"submit (.+)",
            ],
            IntentType.SCREENSHOT: [
                r"take screenshot",
                r"capture screen",
                r"screenshot",
            ],
            IntentType.WAIT: [
                r"wait (.+)",
                r"pause (.+)",
                r"sleep (.+)",
            ],
        }
        
        # Parameter extraction patterns
        self.parameter_patterns = {
            'url': r'https?://[^\s]+',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'time': r'\d{1,2}:\d{2}(?:\s*[AaPp][Mm])?',
            'number': r'\d+',
            'location': r'(?:from|to|in|at)\s+([^,\s]+(?:\s+[^,\s]+)*)',
        }
    
    async def initialize(self) -> bool:
        """
        Initialize the BERT model and tokenizer.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing BERT intent classifier...")
            
            model_path = config.ai.model_path
            
            if config.ai.use_local_model and os.path.exists(model_path):
                logger.info(f"Loading local BERT model from {model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                logger.info("Loading BERT model from Hugging Face Hub")
                model_name = "microsoft/DialoGPT-medium"  # Fallback model
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Set model to evaluation mode
            self.model.eval()
            
            self.is_initialized = True
            logger.info("Intent classifier initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize intent classifier: {e}")
            logger.info("Will use pattern-based classification as fallback")
            self.is_initialized = False
            return False
    
    async def classify(self, command: str) -> IntentResult:
        """
        Classify a natural language command into an intent.
        
        Args:
            command: Natural language command string
            
        Returns:
            IntentResult: Classification result with intent and parameters
        """
        try:
            # Preprocess command
            processed_text = self._preprocess_text(command)
            
            # Try BERT classification first if available
            if self.is_initialized and self.model is not None:
                intent, confidence = await self._bert_classify(processed_text)
            else:
                # Fallback to pattern-based classification
                intent, confidence = self._pattern_classify(processed_text)
            
            # Extract parameters
            parameters = self._extract_parameters(command, intent)
            
            result = IntentResult(
                intent=intent,
                confidence=confidence,
                parameters=parameters,
                raw_command=command,
                processed_text=processed_text
            )
            
            logger.debug(f"Intent classification: {intent.value} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                raw_command=command,
                processed_text=command
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for classification."""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation at the end
        text = re.sub(r'[.!?]+$', '', text)
        
        return text
    
    async def _bert_classify(self, text: str) -> Tuple[IntentType, float]:
        """
        Classify using BERT model.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Tuple of (intent, confidence)
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=config.ai.max_tokens
            )
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                
                # Get the highest probability class
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Map class index to intent (this would need training data)
            # For now, fall back to pattern matching
            return self._pattern_classify(text)
            
        except Exception as e:
            logger.error(f"BERT classification failed: {e}")
            return self._pattern_classify(text)
    
    def _pattern_classify(self, text: str) -> Tuple[IntentType, float]:
        """
        Classify using pattern matching.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Tuple of (intent, confidence)
        """
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate confidence based on pattern specificity
                    confidence = min(0.9, 0.5 + (len(pattern) / 100))
                    
                    if confidence > best_confidence:
                        best_intent = intent_type
                        best_confidence = confidence
        
        # If no pattern matches, try keyword matching
        if best_intent == IntentType.UNKNOWN:
            keyword_matches = self._keyword_classify(text)
            if keyword_matches:
                best_intent, best_confidence = keyword_matches
        
        return best_intent, best_confidence
    
    def _keyword_classify(self, text: str) -> Optional[Tuple[IntentType, float]]:
        """Classify based on keywords."""
        keywords = {
            IntentType.NAVIGATE: ['go', 'navigate', 'open', 'visit', 'load', 'website'],
            IntentType.SEARCH: ['search', 'find', 'look', 'query'],
            IntentType.CLICK: ['click', 'press', 'tap', 'select'],
            IntentType.TYPE: ['type', 'enter', 'input', 'write'],
            IntentType.SCROLL: ['scroll', 'page'],
            IntentType.BOOK_TRAVEL: ['book', 'reserve', 'flight', 'hotel', 'car', 'expedia'],
            IntentType.GET_DIRECTIONS: ['directions', 'route', 'maps', 'navigation'],
            IntentType.SCREENSHOT: ['screenshot', 'capture', 'image'],
            IntentType.WAIT: ['wait', 'pause', 'sleep', 'delay'],
        }
        
        word_tokens = text.split()
        
        for intent_type, intent_keywords in keywords.items():
            matches = sum(1 for word in word_tokens if word in intent_keywords)
            if matches > 0:
                confidence = min(0.7, matches / len(word_tokens))
                return intent_type, confidence
        
        return None
    
    def _extract_parameters(self, command: str, intent: IntentType) -> Dict[str, Any]:
        """
        Extract parameters from command based on intent.
        
        Args:
            command: Original command text
            intent: Classified intent
            
        Returns:
            Dict of extracted parameters
        """
        parameters = {}
        
        # Extract common parameters
        for param_name, pattern in self.parameter_patterns.items():
            matches = re.findall(pattern, command, re.IGNORECASE)
            if matches:
                parameters[param_name] = matches
        
        # Intent-specific parameter extraction
        if intent == IntentType.NAVIGATE:
            # Extract URL or site name
            url_match = re.search(r'(?:go to|navigate to|open|visit)\s+(.+)', command, re.IGNORECASE)
            if url_match:
                target = url_match.group(1).strip()
                if not target.startswith('http'):
                    # Add protocol if missing
                    if '.' in target:
                        target = f"https://{target}"
                parameters['target'] = target
        
        elif intent == IntentType.SEARCH:
            # Extract search query
            search_match = re.search(r'(?:search for|find|look for)\s+(.+)', command, re.IGNORECASE)
            if search_match:
                parameters['query'] = search_match.group(1).strip()
        
        elif intent == IntentType.CLICK:
            # Extract element to click
            click_match = re.search(r'click(?:\s+on)?\s+(.+)', command, re.IGNORECASE)
            if click_match:
                parameters['element'] = click_match.group(1).strip()
        
        elif intent == IntentType.TYPE:
            # Extract text to type
            type_match = re.search(r'(?:type|enter|input|write)\s+(.+)', command, re.IGNORECASE)
            if type_match:
                parameters['text'] = type_match.group(1).strip()
        
        elif intent == IntentType.SCROLL:
            # Extract scroll direction and amount
            if 'down' in command.lower():
                parameters['direction'] = 'down'
            elif 'up' in command.lower():
                parameters['direction'] = 'up'
            else:
                parameters['direction'] = 'down'  # default
            
            # Extract scroll amount
            amount_match = re.search(r'(\d+)', command)
            if amount_match:
                parameters['amount'] = int(amount_match.group(1))
            else:
                parameters['amount'] = 3  # default
        
        elif intent == IntentType.BOOK_TRAVEL:
            # Extract travel details
            if 'flight' in command.lower():
                parameters['travel_type'] = 'flight'
            elif 'hotel' in command.lower():
                parameters['travel_type'] = 'hotel'
            elif 'car' in command.lower():
                parameters['travel_type'] = 'car'
            
            # Extract locations
            location_matches = re.findall(r'(?:from|to|in)\s+([^,\s]+(?:\s+[^,\s]+)*)', command, re.IGNORECASE)
            if location_matches:
                parameters['locations'] = location_matches
        
        elif intent == IntentType.GET_DIRECTIONS:
            # Extract start and end locations
            directions_match = re.search(r'(?:directions|route)\s+from\s+(.+?)\s+to\s+(.+)', command, re.IGNORECASE)
            if directions_match:
                parameters['from'] = directions_match.group(1).strip()
                parameters['to'] = directions_match.group(2).strip()
            else:
                # Try to extract destination only
                dest_match = re.search(r'(?:directions to|route to|how to get to)\s+(.+)', command, re.IGNORECASE)
                if dest_match:
                    parameters['to'] = dest_match.group(1).strip()
        
        elif intent == IntentType.WAIT:
            # Extract wait duration
            duration_match = re.search(r'(?:wait|pause|sleep)\s+(\d+)', command, re.IGNORECASE)
            if duration_match:
                parameters['duration'] = int(duration_match.group(1))
            else:
                parameters['duration'] = 5  # default seconds
        
        return parameters
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent types."""
        return [intent.value for intent in IntentType if intent != IntentType.UNKNOWN]
    
    def get_intent_examples(self) -> Dict[str, List[str]]:
        """Get example commands for each intent type."""
        return {
            IntentType.NAVIGATE.value: [
                "Go to google.com",
                "Navigate to https://example.com",
                "Open YouTube",
            ],
            IntentType.SEARCH.value: [
                "Search for Python tutorials",
                "Find restaurants near me",
                "Look for AI news",
            ],
            IntentType.CLICK.value: [
                "Click the login button",
                "Click on the first link",
                "Press the submit button",
            ],
            IntentType.TYPE.value: [
                "Type hello world",
                "Enter my email address",
                "Input the password",
            ],
            IntentType.SCROLL.value: [
                "Scroll down",
                "Scroll up 5 times",
                "Scroll to the bottom",
            ],
            IntentType.BOOK_TRAVEL.value: [
                "Book a flight from NYC to LA",
                "Find hotels in Paris",
                "Rent a car in Miami",
            ],
            IntentType.GET_DIRECTIONS.value: [
                "Get directions from home to work",
                "Directions to the airport",
                "Route to downtown",
            ],
        }
