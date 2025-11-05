"""
Enhanced Knowledge Graph Visualization
Creates an interactive graph showing ontology structure and movie relationships.
"""

import networkx as nx
from pyvis.network import Network
import uuid
import re
from rdflib import RDF, RDFS
from movie_ontology import EX

def clean_label(uri):
    """Extract and clean a readable label from URI"""
    label = uri.split("#")[-1]
    label = re.sub(r'^(m_|actor_|director_|genre_|lang_|mood_)', '', label)
    label = label.replace("_", " ")
    label = label.title()
    return label

def get_node_type(node_id):
    """Determine node type for styling"""
    node_str = str(node_id)
    if "m_" in node_str or "Movie" in node_str:
        return "movie"
    elif "actor_" in node_str or "Actor" in node_str:
        return "actor"
    elif "director_" in node_str or "Director" in node_str:
        return "director"
    elif "genre_" in node_str or "Genre" in node_str:
        return "genre"
    elif "lang_" in node_str or "Language" in node_str:
        return "language"
    elif "mood_" in node_str or "Mood" in node_str:
        return "mood"
    return "other"

def visualize_ontology_graph(graph, max_movies=10):
    """
    Create an interactive knowledge graph visualization showing ontology structure.
    Similar to the food recipe example - shows classes, properties, and instances.
    
    Args:
        graph: RDF Graph containing movie data
        max_movies: Maximum number of movies to show (to avoid clutter)
    """
    # Build NetworkX graph
    G = nx.DiGraph()
    
    # Add all triples
    for s, p, o in graph:
        G.add_node(str(s))
        G.add_node(str(o))
        G.add_edge(str(s), str(o), label=str(p))
    
    # Create visualization with improved settings
    net = Network(
        height="100vh",
        width="100%", 
        bgcolor="#1A201E",
        font_color="#FFFFFF",
        directed=True,
        notebook=False
    )
    
    # Set physics for better layout with improved interactions
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 16,
          "face": "Arial",
          "color": "#FFFFFF"
        },
        "scaling": {
          "min": 15,
          "max": 60
        },
        "shadow": {
          "enabled": true,
          "color": "rgba(0,0,0,0.6)",
          "size": 12,
          "x": 5,
          "y": 5
        }
      },
      "edges": {
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.3
        },
        "shadow": {
          "enabled": true,
          "color": "rgba(0,0,0,0.4)",
          "size": 5
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1.5
          }
        },
        "width": 2,
        "color": {
          "color": "#81C784",
          "highlight": "#4CAF50"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -5000,
          "centralGravity": 0.15,
          "springLength": 250,
          "springConstant": 0.08,
          "damping": 0.12,
          "avoidOverlap": 0.8
        },
        "maxVelocity": 60,
        "solver": "barnesHut",
        "stabilization": {
          "enabled": true,
          "iterations": 2000,
          "updateInterval": 50,
          "onlyDynamicEdges": false,
          "fit": true
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 150,
        "hideEdgesOnDrag": false,
        "hideEdgesOnZoom": false,
        "navigationButtons": true,
        "keyboard": {
          "enabled": true,
          "speed": {
            "x": 15,
            "y": 15,
            "zoom": 0.03
          },
          "bindToWindow": true
        },
        "zoomView": true,
        "dragView": true
      }
    }
    """)
    
    # Sort movies by rating (highest first) for better visualization
    from rdflib import RDFS
    movies_with_ratings = []
    for movie_uri in graph.subjects(RDF.type, EX.Movie):
        ratings = list(graph.objects(movie_uri, EX.hasRating))
        rating = float(ratings[0]) if ratings else 0.0
        movies_with_ratings.append((str(movie_uri), rating))
    
    # Sort by rating descending and take top movies
    movies_with_ratings.sort(key=lambda x: x[1], reverse=True)
    movies = [m[0] for m in movies_with_ratings[:max_movies]]
    
    # Track added nodes to avoid duplicates
    added_nodes = set()
    
    # Add ontology classes (green squares/ellipses for classes)
    classes = {
        str(EX.Movie): "Movie",
        str(EX.Actor): "Actor",
        str(EX.Director): "Director",
        str(EX.Genre): "Genre",
        str(EX.Language): "Language",
        str(EX.Mood): "Mood"
    }
    
    for class_uri, class_name in classes.items():
        net.add_node(
            class_uri,
            label=class_name,
            color={"background": "#4CAF50", "border": "#45a049"},
            size=50,
            shape="box",  # Changed to box for classes
            font={"size": 20, "face": "Arial", "color": "#1A201E", "bold": True},
            borderWidth=4
        )
        added_nodes.add(class_uri)
    
    # Add properties (light green)
    properties = {
        str(EX.hasGenre): "hasGenre",
        str(EX.hasActor): "hasActor",
        str(EX.directedBy): "directedBy",
        str(EX.hasRating): "hasRating",
        str(EX.releasedIn): "releasedIn",
        str(EX.hasLanguage): "hasLanguage",
        str(EX.hasMood): "hasMood"
    }
    
    for prop_uri, prop_name in properties.items():
        net.add_node(
            prop_uri,
            label=prop_name,
            color={"background": "#81C784", "border": "#66BB6A"},
            size=30,
            shape="ellipse",
            font={"size": 14, "face": "Arial", "color": "#1A201E"},
            borderWidth=2
        )
        added_nodes.add(prop_uri)
    
    # Add property-domain-range relationships
    # hasGenre: Movie -> Genre
    net.add_edge(str(EX.hasGenre), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    net.add_edge(str(EX.hasGenre), str(EX.Genre), label="range", color="#81C784", arrows="to", width=3)
    
    # hasActor: Movie -> Actor
    net.add_edge(str(EX.hasActor), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    net.add_edge(str(EX.hasActor), str(EX.Actor), label="range", color="#81C784", arrows="to", width=3)
    
    # directedBy: Movie -> Director
    net.add_edge(str(EX.directedBy), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    net.add_edge(str(EX.directedBy), str(EX.Director), label="range", color="#81C784", arrows="to", width=3)
    
    # hasRating: Movie -> float
    net.add_edge(str(EX.hasRating), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    
    # releasedIn: Movie -> integer
    net.add_edge(str(EX.releasedIn), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    
    # hasLanguage: Movie -> Language
    net.add_edge(str(EX.hasLanguage), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    net.add_edge(str(EX.hasLanguage), str(EX.Language), label="range", color="#81C784", arrows="to", width=3)
    
    # hasMood: Movie -> Mood
    net.add_edge(str(EX.hasMood), str(EX.Movie), label="domain", color="#81C784", arrows="to", width=3)
    net.add_edge(str(EX.hasMood), str(EX.Mood), label="range", color="#81C784", arrows="to", width=3)
    
    # Add sample movies and their relationships
    for movie_uri in movies:
        movie_label = clean_label(movie_uri)
        
        # Get year and rating for movie label
        years = list(graph.objects(movie_uri, EX.releasedIn))
        ratings = list(graph.objects(movie_uri, EX.hasRating))
        
        year_text = f" ({years[0]})" if years else ""
        rating_text = f" ⭐{ratings[0]:.1f}" if ratings else ""
        
        # Add movie node (red box) with year and rating - larger size
        net.add_node(
            movie_uri,
            label=f"{movie_label}{year_text}{rating_text}",
            color={"background": "#FF5252", "border": "#E53935"},
            size=35,
            shape="box",
            font={"size": 14, "face": "Arial", "color": "#FFFFFF", "bold": True},
            borderWidth=3
        )
        added_nodes.add(movie_uri)
        
        # Add "type" edge: Movie instance -> Movie class (green square)
        net.add_edge(movie_uri, str(EX.Movie), label="type", color="#4CAF50", arrows="to", width=4)
        
        # Add ALL genres for this movie
        genres = list(graph.objects(movie_uri, EX.hasGenre))
        for genre in genres:
            genre_uri = str(genre)
            genre_label = clean_label(genre_uri)
            
            # Check if genre node already exists
            if genre_uri not in added_nodes:
                net.add_node(
                    genre_uri,
                    label=genre_label,
                    color={"background": "#81C784", "border": "#66BB6A"},
                    size=25,
                    shape="dot",  # Green circle for genre instances
                    font={"size": 14, "face": "Arial", "color": "#1A201E", "bold": True},
                    borderWidth=3
                )
                added_nodes.add(genre_uri)
                # Type edge: Genre -> Genre class (green square)
                net.add_edge(genre_uri, str(EX.Genre), label="type", color="#4CAF50", arrows="to", width=3)
            
            # Direct edge: Movie -> hasGenre -> Genre
            net.add_edge(movie_uri, genre_uri, label="hasGenre", color="#81C784", arrows="to", width=4)
        
        # Add ALL directors for this movie
        directors = list(graph.objects(movie_uri, EX.directedBy))
        for director in directors:
            director_uri = str(director)
            director_label = clean_label(director_uri)
            
            # Check if director node already exists
            if director_uri not in added_nodes:
                net.add_node(
                    director_uri,
                    label=director_label,
                    color={"background": "#FFC107", "border": "#FFB300"},
                    size=28,
                    shape="triangle",
                    font={"size": 13, "face": "Arial", "color": "#1A201E", "bold": True},
                    borderWidth=3
                )
                added_nodes.add(director_uri)
                # Type edge: Director instance -> Director class (green square)
                net.add_edge(director_uri, str(EX.Director), label="type", color="#4CAF50", arrows="to", width=3)
            
            # Direct edge: Movie -> directedBy -> Director
            net.add_edge(movie_uri, director_uri, label="directedBy", color="#FFC107", arrows="to", width=4)
        
        # Add ALL actors for this movie (up to 5 to avoid too much clutter)
        actors = list(graph.objects(movie_uri, EX.hasActor))[:5]
        for actor in actors:
            actor_uri = str(actor)
            actor_label = clean_label(actor_uri)
            
            # Check if actor node already exists
            if actor_uri not in added_nodes:
                net.add_node(
                    actor_uri,
                    label=actor_label,
                    color={"background": "#4DD0E1", "border": "#00ACC1"},
                    size=22,
                    shape="dot",
                    font={"size": 12, "face": "Arial", "color": "#1A201E", "bold": True},
                    borderWidth=2
                )
                added_nodes.add(actor_uri)
                # Type edge: Actor instance -> Actor class (green square)
                net.add_edge(actor_uri, str(EX.Actor), label="type", color="#4CAF50", arrows="to", width=2)
            
            # Direct edge: Movie -> hasActor -> Actor
            net.add_edge(movie_uri, actor_uri, label="hasActor", color="#4DD0E1", arrows="to", width=3)
        
        # Add language if available
        languages = list(graph.objects(movie_uri, EX.hasLanguage))
        for language in languages:
            language_uri = str(language)
            language_label = clean_label(language_uri)
            
            if language_uri not in added_nodes:
                net.add_node(
                    language_uri,
                    label=language_label,
                    color={"background": "#9575CD", "border": "#7E57C2"},
                    size=24,
                    shape="dot",  # Purple circle for language instances
                    font={"size": 13, "face": "Arial", "color": "#FFFFFF", "bold": True},
                    borderWidth=3
                )
                added_nodes.add(language_uri)
                # Type edge: Language instance -> Language class (green square)
                net.add_edge(language_uri, str(EX.Language), label="type", color="#4CAF50", arrows="to", width=3)
            
            # Direct edge: Movie -> hasLanguage -> Language
            net.add_edge(movie_uri, language_uri, label="hasLanguage", color="#9575CD", arrows="to", width=3)
    
    # Generate filename
    out = f"graph_{uuid.uuid4().hex}.html"
    net.save_graph(out)
    
    # Read the generated HTML
    with open(out, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Inject header and styling into the existing HTML
    import re
    
    # Find and replace the body tag to add header
    body_pattern = r'<body[^>]*>'
    header_html = '''<div class="graph-header">
        <div>
            <h1><span>📊</span>Knowledge Graph Visualization</h1>
            <div class="info">Semantic Movie Ontology Structure & Relationships</div>
        </div>
        <div class="legend">
            <div class="legend-item"><span class="legend-node legend-class box"></span><span>Class</span></div>
            <div class="legend-item"><span class="legend-node legend-property"></span><span>Property</span></div>
            <div class="legend-item"><span class="legend-node legend-movie box"></span><span>Movie</span></div>
            <div class="legend-item"><span class="legend-node legend-genre"></span><span>Genre</span></div>
            <div class="legend-item"><span class="legend-node legend-director triangle"></span><span>Director</span></div>
            <div class="legend-item"><span class="legend-node legend-actor"></span><span>Actor</span></div>
            <div class="legend-item"><span class="legend-node legend-language" style="background: #9575CD; border: 2px solid #7E57C2; width: 20px; height: 20px; border-radius: 50%; display: inline-block;"></span><span>Language</span></div>
        </div>
    </div>
    <div class="controls">
        <button class="control-btn" onclick="window.location.href='/'">← Back to Dashboard</button>
        <button class="control-btn" onclick="location.reload()">🔄 Refresh</button>
    </div>
    <div class="graph-container">'''
    
    html_content = re.sub(body_pattern, '<body>' + header_html, html_content)
    
    # Wrap the network div
    html_content = html_content.replace('</body>', '</div></body>')
    
    # Add CSS and adjust styles
    css_addition = '''<style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f1419; color: #ffffff; overflow: hidden; }
        .graph-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px; z-index: 1000; position: relative; }
        .graph-header h1 { font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; gap: 12px; }
        .graph-header .info { font-size: 0.95rem; opacity: 0.9; }
        .legend { background: rgba(255,255,255,0.1); padding: 15px 20px; border-radius: 10px; backdrop-filter: blur(10px); display: flex; gap: 20px; flex-wrap: wrap; align-items: center; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; }
        .legend-node { width: 20px; height: 20px; border-radius: 50%; border: 2px solid; display: inline-block; }
        .legend-node.box { border-radius: 4px; }
        .legend-node.triangle { width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 18px solid; border-top: none; border-radius: 0; }
        .legend-class { background: #4CAF50; border-color: #45a049; }
        .legend-property { background: #81C784; border-color: #66BB6A; }
        .legend-movie { background: #FF5252; border-color: #E53935; }
        .legend-director { border-bottom-color: #FFC107; border-left-color: transparent; border-right-color: transparent; }
        .legend-actor { background: #4DD0E1; border-color: #00ACC1; }
        .legend-genre { background: #81C784; border-color: #66BB6A; }
        .graph-container { height: calc(100vh - 120px); width: 100%; position: relative; }
        #mynetworkid { width: 100% !important; height: 100% !important; background: #1A201E !important; }
        .controls { position: absolute; top: 130px; right: 20px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px); z-index: 100; display: flex; flex-direction: column; gap: 10px; }
        .control-btn { padding: 8px 16px; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; border-radius: 6px; cursor: pointer; font-size: 0.9rem; transition: all 0.3s ease; }
        .control-btn:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
        @media (max-width: 768px) { .graph-header { padding: 15px 20px; } .graph-header h1 { font-size: 1.4rem; } .legend { font-size: 0.75rem; gap: 10px; } .controls { display: none; } }
    </style>'''
    
    # Insert CSS before closing head tag
    html_content = html_content.replace('</head>', css_addition + '</head>')
    
    # Write enhanced HTML
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Knowledge graph saved to {out}")
    print(f"   Showing {len(movies)} movies with ontology structure")
    return out
