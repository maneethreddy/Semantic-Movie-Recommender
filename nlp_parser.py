"""
Natural Language Processing Module
Parses user queries to extract movie preferences using pattern matching and optional AI.
"""

import re
from typing import Dict, List, Optional
from movie_ontology import EX

class QueryParser:
    """Parses natural language queries to extract movie preferences."""
    
    def __init__(self):
        self.genre_keywords = {
            'action': 'Action', 'adventure': 'Adventure', 'comedy': 'Comedy',
            'crime': 'Crime', 'drama': 'Drama', 'fantasy': 'Fantasy',
            'horror': 'Horror', 'mystery': 'Mystery', 'romance': 'Romance',
            'sci-fi': 'Sci-Fi', 'science fiction': 'Sci-Fi', 'thriller': 'Thriller',
            'war': 'War', 'western': 'Western'
        }
        
        self.mood_keywords = {
            'thrilling': 'Thrilling', 'thriller': 'Thrilling', 'exciting': 'Thrilling',
            'suspenseful': 'Suspenseful', 'suspense': 'Suspenseful',
            'romantic': 'Romantic', 'romance': 'Romantic',
            'funny': 'Funny', 'humorous': 'Funny', 'comedy': 'Funny',
            'dark': 'Dark', 'gritty': 'Dark',
            'emotional': 'Emotional', 'dramatic': 'Emotional',
            'uplifting': 'Uplifting', 'inspiring': 'Uplifting',
            'thought-provoking': 'Thought-Provoking', 'philosophical': 'Thought-Provoking'
        }
        
        self.director_keywords = {
            'nolan': 'Christopher Nolan', 'christopher nolan': 'Christopher Nolan',
            'tarantino': 'Quentin Tarantino', 'quentin tarantino': 'Quentin Tarantino',
            'scorsese': 'Martin Scorsese', 'martin scorsese': 'Martin Scorsese',
            'spielberg': 'Steven Spielberg', 'steven spielberg': 'Steven Spielberg',
            'cameron': 'James Cameron', 'james cameron': 'James Cameron'
        }
    
    def parse_query(self, query: str) -> Dict:
        """
        Parse natural language query to extract preferences.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with extracted preferences
        """
        query_lower = query.lower()
        preferences = {
            'genres': [],
            'director': None,
            'min_rating': None,
            'max_rating': None,
            'mood': None,
            'year': None,
            'actor': None
        }
        
        # Extract genres
        for keyword, genre in self.genre_keywords.items():
            if keyword in query_lower:
                if genre not in preferences['genres']:
                    preferences['genres'].append(genre)
        
        # Extract director
        for keyword, director in self.director_keywords.items():
            if keyword in query_lower:
                preferences['director'] = director
                break
        
        # Extract rating thresholds
        rating_patterns = [
            r'rated\s+(?:above|over|>\s*)(\d+\.?\d*)',
            r'rating\s+(?:above|over|>\s*)(\d+\.?\d*)',
            r'rated\s+(?:at least|minimum)\s+(\d+\.?\d*)',
            r'rating\s+(?:at least|minimum)\s+(\d+\.?\d*)',
            r'rated\s+(\d+\.?\d*)\s+(?:and|or)\s+(?:above|higher)',
            r'(\d+\.?\d*)\s*\+\s*rating',
            r'rating\s*>\s*(\d+\.?\d*)'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, query_lower)
            if match:
                preferences['min_rating'] = float(match.group(1))
                break
        
        # Extract mood
        for keyword, mood in self.mood_keywords.items():
            if keyword in query_lower:
                preferences['mood'] = mood
                break
        
        # Extract year
        year_patterns = [
            r'from\s+(\d{4})',
            r'released\s+in\s+(\d{4})',
            r'year\s+(\d{4})',
            r'(\d{4})s?\s+movie'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, query_lower)
            if match:
                preferences['year'] = int(match.group(1))
                break
        
        return preferences
    
    def parse_with_gemini(self, query: str, api_key: Optional[str] = None) -> Dict:
        """
        Parse query using Google Gemini AI (optional).
        
        Args:
            query: Natural language query string
            api_key: Google Gemini API key (optional)
            
        Returns:
            Dictionary with extracted preferences
        """
        if not api_key:
            # Fallback to pattern matching
            return self.parse_query(query)
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Extract movie preferences from this query: "{query}"
            
            Return a JSON object with:
            - genres: list of genres (Action, Drama, Sci-Fi, etc.)
            - director: director name or null
            - min_rating: minimum rating (0-10) or null
            - max_rating: maximum rating (0-10) or null
            - mood: mood descriptor (Thrilling, Romantic, Dark, etc.) or null
            - year: release year or null
            - actor: actor name or null
            
            Example: {{"genres": ["Sci-Fi", "Thriller"], "director": "Christopher Nolan", "min_rating": 8.5, "mood": null, "year": null, "actor": null}}
            
            Return only the JSON object, no other text:
            """
            
            response = model.generate_content(prompt)
            import json
            result = json.loads(response.text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to pattern matching.")
            return self.parse_query(query)
    
    def preferences_to_rdf(self, preferences: Dict, graph):
        """
        Convert preferences to RDF triples.
        
        Args:
            preferences: Dictionary of preferences
            graph: RDF Graph to add triples to
            
        Returns:
            UserPreference URI
        """
        from rdflib import RDF, Literal, XSD
        
        pref_uri = EX["UserPref_1"]
        graph.add((pref_uri, RDF.type, EX.UserPreference))
        
        for genre in preferences.get('genres', []):
            genre_uri = EX[f"genre_{genre.replace(' ', '_')}"]
            graph.add((pref_uri, EX.prefersGenre, genre_uri))
        
        if preferences.get('director'):
            director_uri = EX[f"director_{preferences['director'].replace(' ', '_')}"]
            graph.add((pref_uri, EX.prefersDirector, director_uri))
        
        if preferences.get('min_rating'):
            graph.add((pref_uri, EX.prefersRating, Literal(float(preferences['min_rating']), datatype=XSD.float)))
        
        if preferences.get('mood'):
            mood_uri = EX[f"mood_{preferences['mood'].replace(' ', '_')}"]
            graph.add((pref_uri, EX.prefersMood, mood_uri))
        
        return pref_uri

