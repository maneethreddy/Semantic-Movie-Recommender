"""
Semantic Reasoning Engine
Uses SWRL-like rules to infer new facts from the RDF knowledge base.
"""

from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD
from movie_ontology import EX

def infer_similar_movies(graph):
    """
    Rule: If two movies share the same director AND at least one genre,
    mark them as similar.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        Graph with inferred similarity relationships added
    """
    from rdflib import URIRef
    
    # Add similarity property if not exists
    if not (EX.hasSimilarity, None, None) in graph:
        graph.add((EX.hasSimilarity, RDF.type, RDF.Property))
        graph.add((EX.hasSimilarity, RDFS.domain, EX.Movie))
        graph.add((EX.hasSimilarity, RDFS.range, EX.Movie))
    
    movies = list(graph.subjects(RDF.type, EX.Movie))
    
    for movie1 in movies:
        for movie2 in movies:
            if movie1 >= movie2:  # Avoid duplicates and self-comparisons
                continue
            
            # Get directors
            dir1 = list(graph.objects(movie1, EX.directedBy))
            dir2 = list(graph.objects(movie2, EX.directedBy))
            
            # Get genres
            genres1 = set(graph.objects(movie1, EX.hasGenre))
            genres2 = set(graph.objects(movie2, EX.hasGenre))
            
            # Check if same director and share at least one genre
            if dir1 and dir2 and dir1 == dir2 and genres1.intersection(genres2):
                graph.add((movie1, EX.hasSimilarity, movie2))
                graph.add((movie2, EX.hasSimilarity, movie1))
    
    return graph

def infer_high_rated_movies(graph, threshold=8.5):
    """
    Rule: Mark movies with rating >= threshold as high-rated.
    
    Args:
        graph: RDF Graph containing movie data
        threshold: Rating threshold (default 8.5)
        
    Returns:
        Graph with high-rated classification added
    """
    if not (EX.HighRatedMovie, None, None) in graph:
        graph.add((EX.HighRatedMovie, RDF.type, RDFS.Class))
        graph.add((EX.HighRatedMovie, RDFS.subClassOf, EX.Movie))
    
    movies = list(graph.subjects(RDF.type, EX.Movie))
    
    for movie in movies:
        ratings = list(graph.objects(movie, EX.hasRating))
        if ratings and float(ratings[0]) >= threshold:
            graph.add((movie, RDF.type, EX.HighRatedMovie))
    
    return graph

def infer_director_expertise(graph):
    """
    Rule: If a director has directed 3+ movies, mark them as experienced.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        Graph with director expertise classification added
    """
    if not (EX.ExperiencedDirector, None, None) in graph:
        graph.add((EX.ExperiencedDirector, RDF.type, RDFS.Class))
        graph.add((EX.ExperiencedDirector, RDFS.subClassOf, EX.Director))
    
    directors = list(graph.subjects(RDF.type, EX.Director))
    
    for director in directors:
        movies = list(graph.subjects(EX.directedBy, director))
        if len(movies) >= 3:
            graph.add((director, RDF.type, EX.ExperiencedDirector))
    
    return graph

def infer_actor_collaborations(graph):
    """
    Rule: If two actors appear in 2+ movies together, mark them as frequent collaborators.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        Graph with collaboration relationships added
    """
    if not (EX.frequentlyCollaboratesWith, None, None) in graph:
        graph.add((EX.frequentlyCollaboratesWith, RDF.type, RDF.Property))
        graph.add((EX.frequentlyCollaboratesWith, RDFS.domain, EX.Actor))
        graph.add((EX.frequentlyCollaboratesWith, RDFS.range, EX.Actor))
    
    actors = list(graph.subjects(RDF.type, EX.Actor))
    
    # Build actor-to-movies mapping
    actor_movies = {}
    for actor in actors:
        actor_movies[actor] = set(graph.subjects(EX.hasActor, actor))
    
    # Find frequent collaborations
    for actor1 in actors:
        for actor2 in actors:
            if actor1 >= actor2:
                continue
            
            movies1 = actor_movies[actor1]
            movies2 = actor_movies[actor2]
            common_movies = movies1.intersection(movies2)
            
            if len(common_movies) >= 2:
                graph.add((actor1, EX.frequentlyCollaboratesWith, actor2))
                graph.add((actor2, EX.frequentlyCollaboratesWith, actor1))
    
    return graph

def infer_genre_popularity(graph):
    """
    Rule: If a genre appears in 10+ movies, mark it as popular.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        Graph with genre popularity classification added
    """
    if not (EX.PopularGenre, None, None) in graph:
        graph.add((EX.PopularGenre, RDF.type, RDFS.Class))
        graph.add((EX.PopularGenre, RDFS.subClassOf, EX.Genre))
    
    genres = list(graph.subjects(RDF.type, EX.Genre))
    
    for genre in genres:
        movies = list(graph.subjects(EX.hasGenre, genre))
        if len(movies) >= 10:
            graph.add((genre, RDF.type, EX.PopularGenre))
    
    return graph

def infer_highly_comparable_movies(graph, rating_diff_threshold=0.5):
    """
    Rule: If two movies have rating difference < threshold, mark as HighlyComparable.
    
    Args:
        graph: RDF Graph containing movie data
        rating_diff_threshold: Maximum rating difference (default 0.5)
        
    Returns:
        Graph with highly comparable relationships added
    """
    if not (EX.HighlyComparable, None, None) in graph:
        graph.add((EX.HighlyComparable, RDF.type, RDF.Property))
        graph.add((EX.HighlyComparable, RDFS.domain, EX.Movie))
        graph.add((EX.HighlyComparable, RDFS.range, EX.Movie))
    
    movies = list(graph.subjects(RDF.type, EX.Movie))
    
    for movie1 in movies:
        ratings1 = list(graph.objects(movie1, EX.hasRating))
        if not ratings1:
            continue
        
        rating1 = float(ratings1[0])
        
        for movie2 in movies:
            if movie1 >= movie2:
                continue
            
            ratings2 = list(graph.objects(movie2, EX.hasRating))
            if not ratings2:
                continue
            
            rating2 = float(ratings2[0])
            
            if abs(rating1 - rating2) < rating_diff_threshold:
                graph.add((movie1, EX.HighlyComparable, movie2))
                graph.add((movie2, EX.HighlyComparable, movie1))
    
    return graph

def infer_mood_similarity(graph):
    """
    Rule: If two movies share the same mood, mark them as mood-similar.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        Graph with mood similarity relationships added
    """
    movies = list(graph.subjects(RDF.type, EX.Movie))
    
    for movie1 in movies:
        moods1 = set(graph.objects(movie1, EX.hasMood))
        if not moods1:
            continue
        
        for movie2 in movies:
            if movie1 >= movie2:
                continue
            
            moods2 = set(graph.objects(movie2, EX.hasMood))
            if moods1.intersection(moods2):
                graph.add((movie1, EX.SimilarTo, movie2))
                graph.add((movie2, EX.SimilarTo, movie1))
    
    return graph

def apply_all_rules(graph):
    """
    Apply all inference rules to the graph.
    
    Args:
        graph: RDF Graph containing movie data
        
    Returns:
        Graph with all inferred facts added
    """
    print("Applying semantic reasoning rules...")
    print(f"  Initial triples: {len(graph)}")
    
    graph = infer_similar_movies(graph)
    print(f"  After similarity inference: {len(graph)}")
    
    graph = infer_high_rated_movies(graph)
    print(f"  After high-rated inference: {len(graph)}")
    
    graph = infer_director_expertise(graph)
    print(f"  After director expertise inference: {len(graph)}")
    
    graph = infer_actor_collaborations(graph)
    print(f"  After actor collaboration inference: {len(graph)}")
    
    graph = infer_genre_popularity(graph)
    print(f"  After genre popularity inference: {len(graph)}")
    
    graph = infer_highly_comparable_movies(graph)
    print(f"  After highly comparable inference: {len(graph)}")
    
    graph = infer_mood_similarity(graph)
    print(f"  After mood similarity inference: {len(graph)}")
    
    print(f"  Final triples: {len(graph)}\n")
    
    return graph

