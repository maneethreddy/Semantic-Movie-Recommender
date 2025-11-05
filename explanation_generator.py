"""
Explanation Generator Module
Generates human-readable explanations for movie recommendations based on RDF reasoning.
"""

from rdflib import Graph, RDF
from movie_ontology import EX

def generate_explanation(graph, movie_uri, target_movie_uri=None, preferences=None):
    """
    Generate explanation for why a movie was recommended.
    
    Args:
        graph: RDF Graph containing movie data
        movie_uri: URI of the recommended movie (string or URIRef)
        target_movie_uri: URI of the target movie (if recommendation based on similarity)
        preferences: Dictionary of user preferences (if recommendation based on query)
        
    Returns:
        Dictionary with explanation details
    """
    from rdflib import URIRef
    
    # Convert string URIs to URIRef if needed
    if isinstance(movie_uri, str):
        movie_uri = URIRef(movie_uri)
    if target_movie_uri and isinstance(target_movie_uri, str):
        target_movie_uri = URIRef(target_movie_uri)
    
    explanation = {
        'reasons': [],
        'rdf_triples': [],
        'similarity_score': None
    }
    
    # Get movie details
    movie_title = None
    for title in graph.objects(movie_uri, None):
        if hasattr(title, 'value'):
            movie_title = str(title)
            break
    
    if not movie_title:
        movie_title = str(movie_uri).split('#')[-1].replace('m_', '').replace('_', ' ')
    
    # Explanation based on target movie similarity
    if target_movie_uri:
        # Check for same director
        target_directors = list(graph.objects(target_movie_uri, EX.directedBy))
        movie_directors = list(graph.objects(movie_uri, EX.directedBy))
        common_directors = set(target_directors) & set(movie_directors)
        
        if common_directors:
            director_name = str(common_directors.pop()).split('#')[-1].replace('director_', '').replace('_', ' ')
            explanation['reasons'].append(f"Same director: {director_name}")
            explanation['rdf_triples'].append({
                'subject': str(target_movie_uri),
                'predicate': str(EX.directedBy),
                'object': str(common_directors.pop() if common_directors else '')
            })
        
        # Check for shared genres
        target_genres = set(graph.objects(target_movie_uri, EX.hasGenre))
        movie_genres = set(graph.objects(movie_uri, EX.hasGenre))
        common_genres = target_genres & movie_genres
        
        if common_genres:
            genre_names = [str(g).split('#')[-1].replace('genre_', '').replace('_', ' ') for g in common_genres]
            explanation['reasons'].append(f"Shared genres: {', '.join(genre_names)}")
            for genre in common_genres:
                explanation['rdf_triples'].append({
                    'subject': str(movie_uri),
                    'predicate': str(EX.hasGenre),
                    'object': str(genre)
                })
        
        # Check for direct similarity relationship
        if (movie_uri, EX.hasSimilarity, target_movie_uri) in graph or \
           (target_movie_uri, EX.hasSimilarity, movie_uri) in graph:
            explanation['reasons'].append("Semantically similar (inferred by reasoning engine)")
            explanation['rdf_triples'].append({
                'subject': str(target_movie_uri),
                'predicate': str(EX.hasSimilarity),
                'object': str(movie_uri)
            })
        
        # Check for shared actors
        target_actors = set(graph.objects(target_movie_uri, EX.hasActor))
        movie_actors = set(graph.objects(movie_uri, EX.hasActor))
        common_actors = target_actors & movie_actors
        
        if common_actors:
            actor_names = [str(a).split('#')[-1].replace('actor_', '').replace('_', ' ') for a in list(common_actors)[:2]]
            explanation['reasons'].append(f"Shared actors: {', '.join(actor_names)}")
    
    # Explanation based on user preferences
    if preferences:
        if preferences.get('genres'):
            movie_genres = set(graph.objects(movie_uri, EX.hasGenre))
            matched_genres = []
            for pref_genre in preferences['genres']:
                pref_genre_uri = EX[f"genre_{pref_genre.replace(' ', '_')}"]
                if pref_genre_uri in movie_genres:
                    matched_genres.append(pref_genre)
            
            if matched_genres:
                explanation['reasons'].append(f"Matches requested genre(s): {', '.join(matched_genres)}")
        
        if preferences.get('director'):
            movie_directors = list(graph.objects(movie_uri, EX.directedBy))
            director_uri = EX[f"director_{preferences['director'].replace(' ', '_')}"]
            if director_uri in movie_directors:
                explanation['reasons'].append(f"Directed by {preferences['director']}")
        
        if preferences.get('min_rating'):
            ratings = list(graph.objects(movie_uri, EX.hasRating))
            if ratings and float(ratings[0]) >= preferences['min_rating']:
                explanation['reasons'].append(f"Rating {float(ratings[0])} meets minimum threshold of {preferences['min_rating']}")
        
        if preferences.get('mood'):
            movie_moods = set(graph.objects(movie_uri, EX.hasMood))
            mood_uri = EX[f"mood_{preferences['mood'].replace(' ', '_')}"]
            if mood_uri in movie_moods:
                explanation['reasons'].append(f"Matches requested mood: {preferences['mood']}")
        
        if preferences.get('year'):
            years = list(graph.objects(movie_uri, EX.releasedIn))
            if years and int(years[0]) == preferences['year']:
                explanation['reasons'].append(f"Released in {preferences['year']}")
    
    # Get rating for similarity score calculation
    ratings = list(graph.objects(movie_uri, EX.hasRating))
    if ratings:
        rating_val = float(ratings[0])
        explanation['similarity_score'] = rating_val / 10.0  # Normalize to 0-1
        if not explanation['reasons']:
            explanation['reasons'].append(f"High rating: {rating_val}")
    else:
        explanation['similarity_score'] = 0.5  # Default score
    
    return explanation

def format_explanation(explanation):
    """
    Format explanation as human-readable text.
    
    Args:
        explanation: Explanation dictionary
        
    Returns:
        Formatted string
    """
    if not explanation['reasons']:
        return "Recommended based on semantic similarity in the knowledge graph."
    
    text = "Recommended because:\n"
    for i, reason in enumerate(explanation['reasons'], 1):
        text += f"  {i}. {reason}\n"
    
    return text

def get_rdf_triples_for_movie(graph, movie_uri, limit=10):
    """
    Get relevant RDF triples for a movie to show reasoning path.
    
    Args:
        graph: RDF Graph containing movie data
        movie_uri: URI of the movie (string or URIRef)
        limit: Maximum number of triples to return
        
    Returns:
        List of triple dictionaries
    """
    from rdflib import URIRef
    
    # Convert string URI to URIRef if needed
    if isinstance(movie_uri, str):
        movie_uri = URIRef(movie_uri)
    
    triples = []
    
    # Get direct properties
    for prop in [EX.hasGenre, EX.hasActor, EX.directedBy, EX.hasRating, EX.hasMood, EX.hasLanguage]:
        for obj in graph.objects(movie_uri, prop):
            prop_name = str(prop).split('#')[-1].replace('has', '').replace('directedBy', 'directed by').replace('_', ' ')
            obj_name = str(obj).split('#')[-1].replace('m_', '').replace('actor_', '').replace('director_', '').replace('genre_', '').replace('mood_', '').replace('lang_', '').replace('_', ' ')
            triples.append({
                'subject': str(movie_uri).split('#')[-1].replace('m_', ''),
                'predicate': prop_name,
                'object': obj_name,
                'type': 'property'
            })
    
    # Get similarity relationships
    for similar in graph.objects(movie_uri, EX.hasSimilarity):
        similar_name = str(similar).split('#')[-1].replace('m_', '').replace('_', ' ')
        triples.append({
            'subject': str(movie_uri).split('#')[-1].replace('m_', ''),
            'predicate': 'similar to',
            'object': similar_name,
            'type': 'similarity'
        })
    
    return triples[:limit]

