"""
Enhanced Knowledge Graph Visualization
Creates an interactive graph showing ontology structure and movie relationships.
"""

import networkx as nx
from pyvis.network import Network
import uuid
import re
import math
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

def visualize_ontology_graph(graph, max_movies=5):
    """
    Create a knowledge graph visualization showing 5 movie instances with their relationships.
    Shows: Movies (red boxes) -> Actors, Directors, Genres, Ratings, Years
    """
    # Create visualization with dark background
    net = Network(
        height="100vh",
        width="100%", 
        bgcolor="#1A201E",
        font_color="#FFFFFF",
        directed=True,
        notebook=False
    )
    
    # Physics settings for better layout
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 14,
          "face": "Arial",
          "color": "#FFFFFF"
        },
        "borderWidth": 2
      },
      "edges": {
        "smooth": {
          "type": "straight"
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1.2
          }
        },
        "width": 2
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -3000,
          "centralGravity": 0.3,
          "springLength": 200,
          "springConstant": 0.04,
          "damping": 0.09
        },
        "solver": "barnesHut"
      },
      "interaction": {
        "hover": true,
        "zoomView": true,
        "dragView": true
      }
    }
    """)
    
    # Get top rated movies
    from rdflib import URIRef
    movies_with_ratings = []
    for movie_uri in graph.subjects(RDF.type, EX.Movie):
        ratings = list(graph.objects(movie_uri, EX.hasRating))
        rating = float(ratings[0]) if ratings else 0.0
        movies_with_ratings.append((str(movie_uri), rating))
    
    # Sort by rating and take top movies
    movies_with_ratings.sort(key=lambda x: x[1], reverse=True)
    movies = [m[0] for m in movies_with_ratings[:max_movies]]
    
    # Track added nodes
    added_nodes = set()
    
    # Add movies (red boxes)
    for movie_uri_str in movies:
        movie_uri = URIRef(movie_uri_str)
        movie_label = clean_label(movie_uri_str)
        
        # Get year and rating
        years = list(graph.objects(movie_uri, EX.releasedIn))
        ratings = list(graph.objects(movie_uri, EX.hasRating))
        
        year_text = f" {int(years[0])}" if years else ""
        rating_text = f" {float(ratings[0]):.1f}" if ratings else ""
        
        # Add movie node
        net.add_node(
            movie_uri_str,
            label=f"{movie_label}{rating_text}{year_text}",
            color={"background": "#FF5252", "border": "#E53935"},
            size=40,
            shape="box",
            font={"size": 15, "face": "Arial", "color": "#FFFFFF", "bold": True},
            borderWidth=3
        )
        added_nodes.add(movie_uri_str)
        
        # Add genres (green circles)
        genres = list(graph.objects(movie_uri, EX.hasGenre))
        for genre in genres:
            genre_uri = str(genre)
            genre_label = clean_label(genre_uri)
            
            if genre_uri not in added_nodes:
                net.add_node(
                    genre_uri,
                    label=genre_label,
                    color={"background": "#81C784", "border": "#66BB6A"},
                    size=25,
                    shape="dot",
                    font={"size": 12, "face": "Arial", "color": "#1A201E", "bold": True},
                    borderWidth=2
                )
                added_nodes.add(genre_uri)
            
            net.add_edge(movie_uri_str, genre_uri, label="hasGenre", color="#81C784", arrows="to", width=2)
        
        # Add directors (yellow triangles)
        directors = list(graph.objects(movie_uri, EX.directedBy))
        for director in directors:
            director_uri = str(director)
            director_label = clean_label(director_uri)
            
            if director_uri not in added_nodes:
                net.add_node(
                    director_uri,
                    label=director_label,
                    color={"background": "#FFC107", "border": "#FFB300"},
                    size=30,
                    shape="triangle",
                    font={"size": 12, "face": "Arial", "color": "#1A201E", "bold": True},
                    borderWidth=2
                )
                added_nodes.add(director_uri)
            
            net.add_edge(movie_uri_str, director_uri, label="directedBy", color="#FFC107", arrows="to", width=3)
        
        # Add actors (cyan circles) - limit to 1 per movie
        actors = list(graph.objects(movie_uri, EX.hasActor))[:1]
        for actor in actors:
            actor_uri = str(actor)
            actor_label = clean_label(actor_uri)
            
            if actor_uri not in added_nodes:
                net.add_node(
                    actor_uri,
                    label=actor_label,
                    color={"background": "#4DD0E1", "border": "#00ACC1"},
                    size=25,
                    shape="dot",
                    font={"size": 12, "face": "Arial", "color": "#1A201E", "bold": True},
                    borderWidth=2
                )
                added_nodes.add(actor_uri)
            
            net.add_edge(movie_uri_str, actor_uri, label="hasActor", color="#4DD0E1", arrows="to", width=2)
        
        # Add ratings (grey circles)
        if ratings:
            rating_value = str(int(float(ratings[0]))) if float(ratings[0]).is_integer() else str(float(ratings[0]))
            rating_node_id = f"rating_{movie_uri_str}_{rating_value}"
            if rating_node_id not in added_nodes:
                net.add_node(
                    rating_node_id,
                    label=rating_value,
                    color={"background": "#9E9E9E", "border": "#757575"},
                    size=20,
                    shape="dot",
                    font={"size": 11, "face": "Arial", "color": "#FFFFFF", "bold": True},
                    borderWidth=2
                )
                added_nodes.add(rating_node_id)
            net.add_edge(movie_uri_str, rating_node_id, label="hasRating", color="#9E9E9E", arrows="to", width=2)
        
        # Add years (grey circles)
        if years:
            year_value = str(int(years[0]))
            year_node_id = f"year_{movie_uri_str}_{year_value}"
            if year_node_id not in added_nodes:
                net.add_node(
                    year_node_id,
                    label=year_value,
                    color={"background": "#9E9E9E", "border": "#757575"},
                    size=20,
                    shape="dot",
                    font={"size": 11, "face": "Arial", "color": "#FFFFFF", "bold": True},
                    borderWidth=2
                )
                added_nodes.add(year_node_id)
            net.add_edge(movie_uri_str, year_node_id, label="releasedIn", color="#9E9E9E", arrows="to", width=2)
    
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
        .graph-container { height: calc(100vh - 120px); width: 100%; position: relative; padding: 20px; }
        #mynetworkid { width: 100% !important; height: 100% !important; background: #1A201E !important; border-radius: 10px; }
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
    print(f"   Showing {len(movies)} movies with their relationships")
    return out
