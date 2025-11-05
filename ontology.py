from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD

EX = Namespace("http://example.org/movie#")

def create_ontology():
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

    :hasGenre a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Genre .
    :hasActor a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Actor .
    :directedBy a rdf:Property ; rdfs:domain :Movie ; rdfs:range :Director .
    :hasRating a rdf:Property ; rdfs:domain :Movie ; rdfs:range xsd:float .
    :releasedIn a rdf:Property ; rdfs:domain :Movie ; rdfs:range xsd:integer .
    """, format="turtle")

    return g

def add_movie(g, uri_label, title, genres, actors, director, rating, year):
    m = EX[uri_label]
    g.add((m, RDF.type, EX.Movie))
    g.add((m, RDFS.label, Literal(title)))
    g.add((m, EX.hasRating, Literal(float(rating), datatype=XSD.float)))
    g.add((m, EX.releasedIn, Literal(int(year), datatype=XSD.integer)))

    for genre in genres:
        gen = EX["genre_" + genre.replace(" ", "_")]
        g.add((gen, RDF.type, EX.Genre))
        g.add((m, EX.hasGenre, gen))

    for actor in actors:
        a = EX["actor_" + actor.replace(" ", "_")]
        g.add((a, RDF.type, EX.Actor))
        g.add((m, EX.hasActor, a))

    dirnode = EX["director_" + director.replace(" ", "_")]
    g.add((dirnode, RDF.type, EX.Director))
    g.add((m, EX.directedBy, dirnode))

def load_sample_data(g):
    # Original 5 movies
    add_movie(g, "m_inception", "Inception", ["Sci-Fi","Thriller"], ["Leonardo DiCaprio","Joseph Gordon-Levitt"], "Christopher Nolan", 8.8, 2010)
    add_movie(g, "m_interstellar", "Interstellar", ["Sci-Fi","Drama"], ["Matthew McConaughey","Anne Hathaway"], "Christopher Nolan", 8.6, 2014)
    add_movie(g, "m_avengers", "Avengers_Endgame", ["Action","Sci-Fi"], ["Robert_Downey_Jr","Chris_Evans"], "Anthony_Russo", 8.4, 2019)
    add_movie(g, "m_shutter", "Shutter_Island", ["Thriller","Mystery"], ["Leonardo_DiCaprio"], "Martin_Scorsese", 8.1, 2010)
    add_movie(g, "m_django", "Django_Unchained", ["Drama","Western"], ["Jamie_Foxx","Leonardo_DiCaprio"], "Quentin_Tarantino", 8.4, 2012)
    # Additional 5 movies
    add_movie(g, "m_dark_knight", "The Dark Knight", ["Action","Crime","Thriller"], ["Christian Bale","Heath Ledger"], "Christopher Nolan", 9.0, 2008)
    add_movie(g, "m_departed", "The Departed", ["Crime","Thriller","Drama"], ["Leonardo DiCaprio","Matt Damon"], "Martin_Scorsese", 8.5, 2006)
    add_movie(g, "m_pulp", "Pulp Fiction", ["Crime","Drama"], ["John Travolta","Samuel L Jackson"], "Quentin_Tarantino", 8.9, 1994)
    add_movie(g, "m_iron_man", "Iron Man", ["Action","Sci-Fi"], ["Robert_Downey_Jr","Gwyneth Paltrow"], "Jon Favreau", 7.9, 2008)
    add_movie(g, "m_prestige", "The Prestige", ["Drama","Mystery","Thriller"], ["Christian Bale","Hugh Jackman"], "Christopher Nolan", 8.5, 2006)

