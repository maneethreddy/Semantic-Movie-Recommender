"""
Query Processor Module
Contains all SPARQL queries for movie recommendations and filtering.
"""

from rdflib import Graph, Namespace, RDF, RDFS, Literal
from movie_ontology import EX

def query_similar_movies(graph, movie_uri, limit=5):
    """
    Find movies similar to the given movie based on shared director and genres.
    Uses direct graph traversal to avoid SPARQL parsing issues.
    
    Args:
        graph: RDF Graph containing movie data
        movie_uri: URI of the target movie (as string)
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    from rdflib import URIRef, RDF, RDFS
    
    target_uri = URIRef(movie_uri)
    similar_movies = {}
    
    # Get target movie's director and genres
    target_directors = list(graph.objects(target_uri, EX.directedBy))
    target_genres = list(graph.objects(target_uri, EX.hasGenre))
    
    # Find movies with same director or shared genres
    for movie_uri_obj in graph.subjects(RDF.type, EX.Movie):
        movie_uri_str = str(movie_uri_obj)
        
        # Skip the target movie itself
        if movie_uri_str == movie_uri:
            continue
        
        # Get movie details
        titles = list(graph.objects(movie_uri_obj, RDFS.label))
        if not titles:
            continue
        title = str(titles[0])
        
        ratings = list(graph.objects(movie_uri_obj, EX.hasRating))
        rating = float(ratings[0]) if ratings else 0.0
        
        # Check for similarity
        movie_directors = list(graph.objects(movie_uri_obj, EX.directedBy))
        movie_genres = list(graph.objects(movie_uri_obj, EX.hasGenre))
        
        # Calculate similarity score
        similarity_score = 0.0
        
        # Same director = high similarity
        if any(d in target_directors for d in movie_directors):
            similarity_score += 0.5
        
        # Shared genres = medium similarity
        shared_genres = set(target_genres) & set(movie_genres)
        if shared_genres:
            similarity_score += len(shared_genres) * 0.2
        
        # Boost by rating
        similarity_score += (rating / 10.0) * 0.3
        
        if similarity_score > 0:
            similar_movies[movie_uri_str] = (movie_uri_str, title, rating, similarity_score)
    
    # Sort by similarity score and rating
    result = sorted(similar_movies.values(), key=lambda x: (x[3], x[2]), reverse=True)
    
    # Return top results (without similarity score)
    return [(uri, title, rating) for uri, title, rating, _ in result[:limit]]

def query_by_genre(graph, genre, limit=10):
    """
    Find movies by genre.
    
    Args:
        graph: RDF Graph containing movie data
        genre: Genre name (will be converted to URI format)
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    genre_uri = EX[f"genre_{genre.replace(' ', '_')}"]
    
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?movie ?title ?rating
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        ?movie ex:hasGenre <%s> .
    }
    ORDER BY DESC(?rating)
    LIMIT %d
    """ % (genre_uri, limit)
    
    results = graph.query(query)
    return [(str(row.movie), str(row.title), float(row.rating)) for row in results]

def query_by_rating(graph, min_rating=8.0, limit=10):
    """
    Find movies with rating >= min_rating.
    
    Args:
        graph: RDF Graph containing movie data
        min_rating: Minimum rating threshold
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?movie ?title ?rating
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        FILTER(?rating >= %f)
    }
    ORDER BY DESC(?rating)
    LIMIT %d
    """ % (min_rating, limit)
    
    results = graph.query(query)
    return [(str(row.movie), str(row.title), float(row.rating)) for row in results]

def query_by_actor(graph, actor_name, limit=10):
    """
    Find movies featuring a specific actor.
    
    Args:
        graph: RDF Graph containing movie data
        actor_name: Actor name (will be converted to URI format)
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    actor_uri = EX[f"actor_{actor_name.replace(' ', '_')}"]
    
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?movie ?title ?rating
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        ?movie ex:hasActor <%s> .
    }
    ORDER BY DESC(?rating)
    LIMIT %d
    """ % (actor_uri, limit)
    
    results = graph.query(query)
    return [(str(row.movie), str(row.title), float(row.rating)) for row in results]

def query_by_director(graph, director_name, limit=10):
    """
    Find movies directed by a specific director.
    
    Args:
        graph: RDF Graph containing movie data
        director_name: Director name (will be converted to URI format)
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    director_uri = EX[f"director_{director_name.replace(' ', '_')}"]
    
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?movie ?title ?rating
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        ?movie ex:directedBy <%s> .
    }
    ORDER BY DESC(?rating)
    LIMIT %d
    """ % (director_uri, limit)
    
    results = graph.query(query)
    return [(str(row.movie), str(row.title), float(row.rating)) for row in results]

def query_by_year_range(graph, start_year, end_year, limit=10):
    """
    Find movies released in a year range.
    
    Args:
        graph: RDF Graph containing movie data
        start_year: Start year (inclusive)
        end_year: End year (inclusive)
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating, year)
    """
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?movie ?title ?rating ?year
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        ?movie ex:releasedIn ?year .
        FILTER(?year >= %d && ?year <= %d)
    }
    ORDER BY DESC(?rating)
    LIMIT %d
    """ % (start_year, end_year, limit)
    
    results = graph.query(query)
    return [(str(row.movie), str(row.title), float(row.rating), int(row.year)) for row in results]

def query_high_rated_by_genre(graph, genre, min_rating=8.0, limit=5):
    """
    Find high-rated movies in a specific genre.
    
    Args:
        graph: RDF Graph containing movie data
        genre: Genre name
        min_rating: Minimum rating threshold
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    genre_uri = EX[f"genre_{genre.replace(' ', '_')}"]
    
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?movie ?title ?rating
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        ?movie ex:hasGenre <%s> .
        FILTER(?rating >= %f)
    }
    ORDER BY DESC(?rating)
    LIMIT %d
    """ % (genre_uri, min_rating, limit)
    
    results = graph.query(query)
    return [(str(row.movie), str(row.title), float(row.rating)) for row in results]

def query_movie_details(graph, movie_uri):
    """
    Get complete details for a movie.
    
    Args:
        graph: RDF Graph containing movie data
        movie_uri: URI of the movie
        
    Returns:
        Dictionary with movie details
    """
    query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?title ?rating ?year ?director ?actor ?genre ?language
    WHERE {
        <%s> rdfs:label ?title .
        OPTIONAL { <%s> ex:hasRating ?rating . }
        OPTIONAL { <%s> ex:releasedIn ?year . }
        OPTIONAL { <%s> ex:directedBy ?director . }
        OPTIONAL { <%s> ex:hasActor ?actor . }
        OPTIONAL { <%s> ex:hasGenre ?genre . }
        OPTIONAL { <%s> ex:hasLanguage ?language . }
    }
    """ % (movie_uri, movie_uri, movie_uri, movie_uri, movie_uri, movie_uri, movie_uri)
    
    results = graph.query(query)
    
    details = {
        'title': None,
        'rating': None,
        'year': None,
        'directors': [],
        'actors': [],
        'genres': [],
        'languages': []
    }
    
    for row in results:
        if row.title:
            details['title'] = str(row.title)
        if row.rating:
            details['rating'] = float(row.rating)
        if row.year:
            details['year'] = int(row.year)
        if row.director and str(row.director) not in details['directors']:
            details['directors'].append(str(row.director).split('#')[-1].replace('director_', '').replace('_', ' '))
        if row.actor and str(row.actor) not in details['actors']:
            details['actors'].append(str(row.actor).split('#')[-1].replace('actor_', '').replace('_', ' '))
        if row.genre and str(row.genre) not in details['genres']:
            details['genres'].append(str(row.genre).split('#')[-1].replace('genre_', '').replace('_', ' '))
        if row.language and str(row.language) not in details['languages']:
            details['languages'].append(str(row.language).split('#')[-1].replace('lang_', '').replace('_', ' '))
    
    return details

def get_all_movies(graph):
    """
    Get all movies with their basic information.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    # Use a simpler approach that avoids SPARQL parsing issues
    from movie_ontology import EX
    from rdflib import RDF, RDFS
    
    movies = []
    for movie_uri in graph.subjects(RDF.type, EX.Movie):
        # Get title
        titles = list(graph.objects(movie_uri, RDFS.label))
        if not titles:
            continue
        title = str(titles[0])
        
        # Get rating
        ratings = list(graph.objects(movie_uri, EX.hasRating))
        rating = float(ratings[0]) if ratings else 0.0
        
        movies.append((str(movie_uri), title, rating))
    
    # Sort by rating descending
    movies.sort(key=lambda x: x[2], reverse=True)
    return movies

def query_by_preferences(graph, preferences, limit=10):
    """
    Find movies matching user preferences.
    Uses direct graph traversal to avoid SPARQL parsing issues.
    
    Args:
        graph: RDF Graph containing movie data
        preferences: Dictionary with preferences (genres, director, min_rating, mood, etc.)
        limit: Maximum number of results
        
    Returns:
        List of tuples (movie_uri, title, rating)
    """
    from rdflib import RDF, RDFS
    
    matching_movies = []
    
    for movie_uri in graph.subjects(RDF.type, EX.Movie):
        # Get movie details
        titles = list(graph.objects(movie_uri, RDFS.label))
        if not titles:
            continue
        title = str(titles[0])
        
        ratings = list(graph.objects(movie_uri, EX.hasRating))
        rating = float(ratings[0]) if ratings else 0.0
        
        # Check preferences
        matches = True
        
        # Genre filter
        if preferences.get('genres'):
            movie_genres = [str(g).split('#')[-1].replace('genre_', '').replace('_', ' ') for g in graph.objects(movie_uri, EX.hasGenre)]
            requested_genres = preferences['genres']
            if not any(genre in movie_genres for genre in requested_genres):
                matches = False
        
        # Rating filter
        if matches and preferences.get('min_rating'):
            if rating < preferences['min_rating']:
                matches = False
        
        # Director filter
        if matches and preferences.get('director'):
            movie_directors = [str(d).split('#')[-1].replace('director_', '').replace('_', ' ') for d in graph.objects(movie_uri, EX.directedBy)]
            if preferences['director'] not in movie_directors:
                matches = False
        
        # Mood filter
        if matches and preferences.get('mood'):
            movie_moods = [str(m).split('#')[-1].replace('mood_', '').replace('_', ' ') for m in graph.objects(movie_uri, EX.hasMood)]
            if preferences['mood'] not in movie_moods:
                matches = False
        
        # Year filter
        if matches and preferences.get('year'):
            years = list(graph.objects(movie_uri, EX.releasedIn))
            if not any(int(str(y)) == preferences['year'] for y in years):
                matches = False
        
        if matches:
            matching_movies.append((str(movie_uri), title, rating))
    
    # Sort by rating descending
    matching_movies.sort(key=lambda x: x[2], reverse=True)
    return matching_movies[:limit]

