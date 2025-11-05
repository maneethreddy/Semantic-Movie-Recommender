# Semantic Movie Recommendation System - Project Structure

This project has been restructured according to the modular architecture specification.

## Project Modules

### 1. **movie_ontology.py** - Ontology Design
Defines RDF classes and properties for the movie recommendation system.

**Classes:**
- `Movie`
- `Actor`
- `Director`
- `Genre`
- `Language`

**Properties:**
- `hasGenre` (Movie → Genre)
- `hasActor` (Movie → Actor)
- `directedBy` / `hasDirector` (Movie → Director)
- `hasRating` (Movie → float)
- `releasedIn` (Movie → integer)
- `hasLanguage` (Movie → Language)

**Functions:**
- `create_ontology()` - Creates and returns the RDF graph with ontology schema
- `load_ontology_from_file(graph, filepath)` - Loads movie data from Turtle file

### 2. **data/movies_data.ttl** - RDF Knowledge Base
Contains 100+ movie triples with their relationships and metadata.

**Content:**
- Movie instances with titles, ratings, years
- Actor relationships
- Director relationships
- Genre classifications
- Language information
- Release years and ratings

**Statistics:**
- 100+ movies
- Multiple genres (Action, Drama, Sci-Fi, Thriller, etc.)
- Various languages (English, Korean, French, etc.)
- Diverse directors and actors

### 3. **semantic_reasoner.py** - Semantic Reasoning Engine
Implements SWRL-like inference rules to infer new facts from the RDF knowledge base.

**Inference Rules:**
1. **Similar Movies** - If two movies share the same director AND at least one genre, mark them as similar
2. **High-Rated Movies** - Mark movies with rating >= 8.5 as high-rated
3. **Director Expertise** - Mark directors with 3+ movies as experienced
4. **Actor Collaborations** - Mark actors appearing in 2+ movies together as frequent collaborators
5. **Genre Popularity** - Mark genres appearing in 10+ movies as popular

**Functions:**
- `infer_similar_movies(graph)` - Creates similarity relationships
- `infer_high_rated_movies(graph, threshold)` - Classifies high-rated movies
- `infer_director_expertise(graph)` - Identifies experienced directors
- `infer_actor_collaborations(graph)` - Finds frequent actor collaborations
- `infer_genre_popularity(graph)` - Identifies popular genres
- `apply_all_rules(graph)` - Applies all inference rules

### 4. **queries.py** - Query Processor
Contains all SPARQL queries for movie recommendations and filtering.

**Query Functions:**
- `query_similar_movies(graph, movie_uri, limit)` - Find movies similar to a given movie
- `query_by_genre(graph, genre, limit)` - Find movies by genre
- `query_by_rating(graph, min_rating, limit)` - Find movies with rating >= threshold
- `query_by_actor(graph, actor_name, limit)` - Find movies featuring an actor
- `query_by_director(graph, director_name, limit)` - Find movies by director
- `query_by_year_range(graph, start_year, end_year, limit)` - Find movies in year range
- `query_high_rated_by_genre(graph, genre, min_rating, limit)` - High-rated movies in genre
- `query_movie_details(graph, movie_uri)` - Get complete movie details
- `get_all_movies(graph)` - Get all movies with basic information

### 5. **app.py** - Flask Web Interface
Simple Flask application that provides REST API endpoints and serves the web interface.

**Endpoints:**
- `GET /` - Serves the main HTML interface
- `GET /api/movies` - Returns list of all movies for dropdown
- `POST /api/recommendations` - Returns movie recommendations based on selected movie
- `GET /api/movie/<movie_id>` - Returns detailed information about a specific movie

**Features:**
- Loads ontology and movie data on startup
- Applies inference rules automatically
- Serves the modern web UI
- Provides JSON API for frontend

### 6. **templates/movie_recommender_ui.html** - Web Interface
Modern, cinematic-themed web interface with:
- Animated graph background
- Movie dropdown selection
- Recommendation display with similarity scores
- Responsive design
- API integration

### 7. **visualize.py** - Visualization (Optional)
PyVis-based graph visualization module (from original project).

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Running the Flask Application
```bash
python app.py
```

The application will:
1. Load the ontology schema
2. Load movie data from `data/movies_data.ttl`
3. Apply semantic reasoning rules
4. Start the Flask server on http://127.0.0.1:5000

### Using the Web Interface
1. Open http://127.0.0.1:5000 in your browser
2. Select a movie from the dropdown
3. Click "Get Recommendations"
4. View similar movies with semantic similarity scores

### Using the Python Modules Directly
```python
from movie_ontology import create_ontology, load_ontology_from_file
from semantic_reasoner import apply_all_rules
from queries import query_similar_movies, get_all_movies

# Create ontology
graph = create_ontology()

# Load data
graph = load_ontology_from_file(graph, 'data/movies_data.ttl')

# Apply inference rules
graph = apply_all_rules(graph)

# Query for similar movies
similar = query_similar_movies(graph, 'http://example.org/movie#m_inception', limit=5)
```

## File Structure

```
semantic_movie_ontology/
│
├── data/
│   └── movies_data.ttl          # RDF knowledge base (100+ movies)
│
├── templates/
│   └── movie_recommender_ui.html # Web interface template
│
├── movie_ontology.py             # Ontology design module
├── semantic_reasoner.py          # Inference rules engine
├── queries.py                    # SPARQL query processor
├── app.py                        # Flask web application
├── visualize.py                  # Graph visualization (optional)
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

## Dependencies

- **rdflib** - RDF graph manipulation
- **flask** - Web framework
- **networkx** - Graph data structures (for visualization)
- **node2vec** - Graph embeddings (for advanced recommendations)
- **pandas** - Data manipulation
- **scikit-learn** - Machine learning utilities
- **pyvis** - Interactive network visualization

## Architecture Flow

1. **Data Loading**: `movie_ontology.py` creates ontology → `movies_data.ttl` loads data
2. **Inference**: `semantic_reasoner.py` applies rules → creates new relationships
3. **Querying**: `queries.py` executes SPARQL queries → returns recommendations
4. **Interface**: `app.py` serves web UI → `templates/movie_recommender_ui.html` displays results

## Extension Points

- Add more movies to `data/movies_data.ttl`
- Create new inference rules in `semantic_reasoner.py`
- Add new query types in `queries.py`
- Customize the web interface in `templates/movie_recommender_ui.html`
- Integrate with external movie databases (OMDB, TMDB, etc.)

