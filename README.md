# Semantic Movie Recommender

A semantic web-based movie recommendation system powered by RDF ontologies, SPARQL queries, and graph embeddings.

## Features

- **Semantic Movie Recommendations**: Get movie recommendations based on semantic similarity using RDF ontologies
- **Interactive Knowledge Graph**: Visualize the movie ontology structure with movies, genres, directors, actors, and their relationships
- **Dual Recommendation Modes**:
  - Select a movie and get similar recommendations
  - Filter by genre and rating preferences
- **Explainable AI**: Understand why movies are recommended with semantic explanations
- **Modern Web Interface**: Clean, responsive UI with dark theme

## Technology Stack

- **Backend**: Flask (Python)
- **Semantic Web**: RDFLib, SPARQL queries
- **Knowledge Graph**: NetworkX, PyVis
- **Frontend**: HTML5, CSS3, JavaScript

## Project Structure

```
semantic_movie_ontology/
├── app.py                 # Flask web application
├── movie_ontology.py      # RDF ontology definitions
├── semantic_reasoner.py   # Inference rules engine
├── queries.py             # SPARQL query functions
├── explanation_generator.py  # Generate explanations
├── visualize.py           # Graph visualization
├── data/
│   └── movies_data.ttl    # Movie knowledge base (RDF/Turtle)
├── templates/
│   └── movie_recommender_ui.html  # Web interface
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/maneethreddy/Semantic-Movie-Recommender.git
cd Semantic-Movie-Recommender
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python3 app.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5001
```

3. Use the application:
   - **Select a Movie**: Choose a movie from the dropdown and get similar recommendations
   - **Filter by Preferences**: Select genre and rating range to discover movies
   - **View Knowledge Graph**: Click "View Knowledge Graph" to see the interactive visualization

## API Endpoints

- `GET /api/movies` - Get all movies
- `POST /api/recommendations` - Get recommendations for a selected movie
- `POST /api/recommendations/preferences` - Get recommendations by preferences
- `GET /api/filters` - Get available filters (genres, rating ranges)
- `GET /graph` - Interactive knowledge graph visualization

## Ontology Structure

The system uses an RDF ontology with the following classes:
- **Movie**: Movie instances
- **Actor**: Actor entities
- **Director**: Director entities
- **Genre**: Movie genres
- **Language**: Movie languages
- **Mood**: Movie moods

## License

MIT License

## Author

Maneeth Reddy
