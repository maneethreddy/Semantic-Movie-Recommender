"""
Movie Ontology Design Module
Defines RDF classes and properties for the movie recommendation system.
"""

from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD

EX = Namespace("http://example.org/movie#")

def create_ontology():
    """
    Creates and returns an RDF graph with the movie ontology schema.
    Defines classes: Movie, Actor, Director, Genre, Language
    Defines properties: hasActor, hasGenre, directedBy (hasDirector), hasRating, releasedIn, hasLanguage
    """
    g = Graph()
    g.bind("ex", EX)

    # Define classes and properties
    g.parse(data="""
    @prefix : <http://example.org/movie#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    :Movie a rdfs:Class .
    :Actor a rdfs:Class .
    :Director a rdfs:Class .
    :Genre a rdfs:Class .
    :Language a rdfs:Class .
    :Mood a rdfs:Class .
    :UserPreference a rdfs:Class .

    :hasGenre a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Genre .
    :hasActor a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Actor .
    :directedBy a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Director .
    :hasDirector a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Director .
    :hasRating a rdf:Property ; rdfs:domain :Movie ; rdfs:range xsd:float .
    :releasedIn a rdf:Property ; rdfs:domain :Movie ; rdfs:range xsd:integer .
    :hasLanguage a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Language .
    :hasMood a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Mood .
    :SimilarTo a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Movie .
    :prefersGenre a rdf:Property ; rdfs:domain :UserPreference ; rdfs:range :Genre .
    :prefersDirector a rdf:Property ; rdfs:domain :UserPreference ; rdfs:range :Director .
    :prefersRating a rdf:Property ; rdfs:domain :UserPreference ; rdfs:range xsd:float .
    :prefersMood a rdf:Property ; rdfs:domain :UserPreference ; rdfs:range :Mood .
    """, format="turtle")

    return g

def load_ontology_from_file(graph, filepath):
    """
    Loads RDF triples from a Turtle file into the graph.
    
    Args:
        graph: RDF Graph object
        filepath: Path to the .ttl file containing movie data
    """
    graph.parse(filepath, format="turtle")
    return graph

