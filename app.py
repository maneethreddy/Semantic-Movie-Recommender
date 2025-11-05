"""
Flask Web Interface
Simple Flask app for the Semantic Movie Recommendation System.
"""

from flask import Flask, render_template, jsonify, request
from movie_ontology import create_ontology, load_ontology_from_file
from semantic_reasoner import apply_all_rules
from queries import query_similar_movies, get_all_movies, query_movie_details, query_by_preferences
from explanation_generator import generate_explanation, get_rdf_triples_for_movie
from visualize import visualize_ontology_graph
import networkx as nx
import os

app = Flask(__name__)

# Initialize the knowledge base
print("Loading movie ontology and data...")
graph = create_ontology()
data_file = os.path.join(os.path.dirname(__file__), 'data', 'movies_data.ttl')
if os.path.exists(data_file):
    graph = load_ontology_from_file(graph, data_file)
    print(f"Loaded {len(graph)} triples from {data_file}")
else:
    print(f"Warning: {data_file} not found. Using empty ontology.")

# Apply inference rules
graph = apply_all_rules(graph)

@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template('movie_recommender_ui.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies for the dropdown."""
    movies = get_all_movies(graph)
    movies_list = []
    for uri, title, rating in movies:
        uri_part = uri.split('#')[-1]
        movies_list.append({
            'id': uri_part,
            'uri': uri,
            'title': title,
            'rating': rating
        })
    return jsonify(movies_list)

@app.route('/api/movie/<movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get detailed information about a specific movie."""
    from movie_ontology import EX
    movie_uri = EX[movie_id]
    movie_uri_str = str(movie_uri)
    
    details = query_movie_details(graph, movie_uri_str)
    return jsonify(details)

@app.route('/api/recommendations/<movie_id>/explanation', methods=['GET'])
def get_recommendation_explanation(movie_id):
    """Get explanation for why a movie was recommended."""
    from movie_ontology import EX
    target_movie_id = request.args.get('target_movie_id')
    
    movie_uri = EX[movie_id]
    movie_uri_str = str(movie_uri)
    
    target_movie_uri = None
    if target_movie_id:
        target_movie_uri = EX[target_movie_id]
        target_movie_uri_str = str(target_movie_uri)
    else:
        target_movie_uri_str = None
    
    explanation = generate_explanation(graph, movie_uri_str, target_movie_uri=target_movie_uri_str)
    rdf_triples = get_rdf_triples_for_movie(graph, movie_uri_str, limit=10)
    
    return jsonify({
        'explanation': explanation,
        'rdf_triples': rdf_triples,
        'formatted_explanation': '\n'.join(explanation['reasons']) if explanation['reasons'] else 'Recommended based on semantic similarity.'
    })

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get movie recommendations based on selected movie."""
    data = request.json
    movie_id = data.get('movie_id')
    
    if not movie_id:
        return jsonify({'error': 'Movie ID is required'}), 400
    
    # Convert movie_id to full URI
    from movie_ontology import EX
    movie_uri = EX[movie_id]
    movie_uri_str = str(movie_uri)
    
    # Get similar movies
    similar_movies = query_similar_movies(graph, movie_uri_str, limit=5)
    
    recommendations = []
    for uri, title, rating in similar_movies:
        uri_part = uri.split('#')[-1]
        explanation = generate_explanation(graph, uri, target_movie_uri=movie_uri_str)
        rdf_triples = get_rdf_triples_for_movie(graph, uri, limit=5)
        
        # Calculate similarity score
        score = 0.85 + (rating - 7.0) * 0.02
        score = min(0.99, max(0.70, score))
        
        recommendations.append({
            'id': uri_part,
            'title': title,
            'rating': rating,
            'similarity_score': round(score, 3),
            'explanation': explanation['reasons'],
            'rdf_triples': rdf_triples
        })
    
    # Sort by similarity score
    recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return jsonify({
        'recommendations': recommendations[:3]  # Return top 3
    })

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter options (genres, rating ranges)."""
    from movie_ontology import EX
    from rdflib import RDF, RDFS
    
    # Get all genres
    genres_query = """
    PREFIX ex: <http://example.org/movie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?genre ?label
    WHERE {
        ?genre rdf:type ex:Genre .
        ?genre rdfs:label ?label .
    }
    ORDER BY ?label
    """
    
    genres = []
    for row in graph.query(genres_query):
        genre_uri = str(row.genre)
        genre_id = genre_uri.split('#')[-1].replace('genre_', '').replace('_', ' ')
        genres.append({
            'id': genre_id,
            'label': str(row.label)
        })
    
    # Rating ranges
    rating_ranges = [
        {'id': 'any', 'label': 'Any Rating'},
        {'id': 'high', 'label': '8.0+ Excellent'},
        {'id': 'good', 'label': '7.0+ Good'},
        {'id': 'moderate', 'label': '6.0+ Moderate'}
    ]
    
    return jsonify({
        'genres': genres,
        'rating_ranges': rating_ranges
    })

@app.route('/api/recommendations/preferences', methods=['POST'])
def get_recommendations_by_preferences():
    """Get movie recommendations based on user preferences."""
    data = request.json
    genre = data.get('genre')
    rating_range = data.get('rating_range', 'any')
    
    preferences = {}
    
    if genre and genre != 'any':
        # Convert genre label back to format needed for query
        genre_normalized = genre.replace(' ', '_')
        preferences['genres'] = [genre_normalized]
    
    if rating_range == 'high':
        preferences['min_rating'] = 8.0
    elif rating_range == 'good':
        preferences['min_rating'] = 7.0
    elif rating_range == 'moderate':
        preferences['min_rating'] = 6.0
    
    # Get movies matching preferences
    movies = query_by_preferences(graph, preferences, limit=10)
    
    recommendations = []
    for uri, title, rating in movies:
        uri_part = uri.split('#')[-1]
        details = query_movie_details(graph, uri)
        
        # Extract genres and director for tags
        tags = []
        if details.get('genres'):
            # Get unique genres (already formatted strings)
            unique_genres = list(set(details['genres']))[:2]
            tags.extend([{'type': 'genre', 'label': g.title()} for g in unique_genres])
        if details.get('directors'):
            director_name = details['directors'][0]  # Already formatted
            tags.append({'type': 'director', 'label': director_name})
        if rating >= 8.0:
            tags.append({'type': 'rating', 'label': 'High Rating'})
        elif rating >= 7.0:
            tags.append({'type': 'rating', 'label': 'Good Rating'})
        
        # Build description
        genre_name = 'Movie'
        if details.get('genres'):
            genre_name = details['genres'][0].title()
        director_text = ''
        if details.get('directors'):
            director_name = details['directors'][0]
            director_text = f' directed by {director_name}'
        
        recommendations.append({
            'id': uri_part,
            'uri': uri,
            'title': title,
            'rating': rating,
            'year': details.get('year'),
            'director': details.get('directors', [None])[0],
            'description': f"{title} is a {genre_name} film{director_text}.",
            'tags': tags,
            'genres': list(set(details.get('genres', []))),
            'actors': list(set(details.get('actors', [])))[:3]
        })
    
    return jsonify({
        'recommendations': recommendations
    })

@app.route('/graph')
def view_graph():
    """Serve the knowledge graph visualization."""
    # Generate visualization HTML showing ontology structure
    html_file = visualize_ontology_graph(graph, max_movies=10)
    
    # Read and return the HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Clean up the temporary file
    try:
        os.remove(html_file)
    except:
        pass
    
    return html_content

if __name__ == '__main__':
    # Ensure templates directory exists
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Copy HTML file to templates if it doesn't exist
    html_file = os.path.join(os.path.dirname(__file__), 'movie_recommender_ui.html')
    template_file = os.path.join(templates_dir, 'movie_recommender_ui.html')
    if os.path.exists(html_file) and not os.path.exists(template_file):
        import shutil
        shutil.copy(html_file, template_file)
    
    print("\n" + "="*70)
    print(" " * 20 + "SEMANTIC MOVIE RECOMMENDER")
    print("="*70)
    print(f"\nKnowledge Base: {len(graph)} triples")
    print("Starting Flask server on http://127.0.0.1:5001")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)

