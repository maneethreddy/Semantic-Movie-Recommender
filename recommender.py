import networkx as nx
from node2vec import Node2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ontology import EX
from rdflib import RDF

def build_graph(g):
    G = nx.Graph()
    for s,p,o in g:
        G.add_node(str(s))
        G.add_node(str(o))
        G.add_edge(str(s), str(o), label=str(p))
    return G

def compute_embeddings(G):
    node2vec = Node2Vec(G, dimensions=64, walk_length=10, num_walks=80, workers=2, seed=42)
    model = node2vec.fit(window=5, min_count=1)
    return model

def recommend(g, model, target_uri, topn=3):
    movie_nodes = [str(m) for m in g.subjects(RDF.type, EX.Movie)]
    movie_nodes = [m for m in movie_nodes if m in model.wv.key_to_index]

    vectors = [model.wv.get_vector(m) for m in movie_nodes]
    mat = np.vstack(vectors)
    sim = cosine_similarity(mat)
    target_idx = movie_nodes.index(target_uri)
    ranking = np.argsort(-sim[target_idx])[1:topn+1]
    return [(movie_nodes[i], round(sim[target_idx,i],3)) for i in ranking]

