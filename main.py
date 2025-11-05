from ontology import create_ontology, load_sample_data, EX
from recommender import build_graph, compute_embeddings, recommend
from visualize import visualize_graph
from rdflib import RDF
import os

print("=" * 70)
print(" " * 15 + "SEMANTIC MOVIE ONTOLOGY")
print("=" * 70)

# 1. Build ontology
g = create_ontology()
load_sample_data(g)
print(f"\nTriples: {len(g)}\n")

# 2. Build graph + embeddings
G = build_graph(g)
model = compute_embeddings(G)

# 3. Get all movies and their ratings
movie_nodes = [str(m) for m in g.subjects(RDF.type, EX.Movie)]
movie_data = []
for m_uri in movie_nodes:
    # Get movie label - keep underscores for format
    uri_part = m_uri.split('#')[-1]
    label_with_underscores = uri_part.replace('m_', '').replace('_', '_')
    label_display = uri_part.replace('m_', '').replace('_', ' ').title()
    # Get rating from RDF
    movie_uri_obj = EX[uri_part]
    rating_triples = list(g.triples((movie_uri_obj, EX.hasRating, None)))
    rating = float(rating_triples[0][2]) if rating_triples else 0.0
    movie_data.append((m_uri, label_with_underscores, label_display, rating))

# Sort by rating
movie_data.sort(key=lambda x: x[3], reverse=True)

# 4. Show movies rated 8.5 and above
high_rated = [m for m in movie_data if m[3] >= 8.5]
if high_rated:
    print("🎯 Movies rated 8.5 and above:\n")
    for _, _, label_display, rating in high_rated:
        print(f"  - {label_display} ({rating})")
    print()

# 5. Show recommendations for key movies (top rated movies)
print("🎬 Top recommendations:\n")

for target_uri, label_underscore, label_display, rating in movie_data:
    if target_uri not in model.wv.key_to_index:
        continue
    
    print(f"Top recommendations for: {label_display}")
    recommendations = recommend(g, model, target_uri, topn=3)
    
    if recommendations:
        for rec, score in recommendations:
            rec_uri_part = rec.split("#")[-1]
            rec_label = rec_uri_part.replace('m_', '').replace('_', '_')
            print(f"  - {rec_label} | score: {score:.2f}")
    else:
        print("  - No recommendations available")
    print()

# 6. Visualize full graph
html = visualize_graph(G)
print(f"Graph saved to {html}\n")
os.system(f"open '{html}'")

