#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF, CSV, TSV

# Define the directory to store the results
directory = "./data/"
if not os.path.exists(directory):
    os.makedirs(directory)

# Initialize SPARQL endpoint
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# SELECT query for JSON, XML, CSV, TSV formats
select_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?predicate
WHERE {
    ?subject rdfs:label "Edgar Quinet (Paris Métro)"@en .
    ?subject ?predicate ?object .
}
"""
sparql.setQuery(select_query)


# CSV example - Decode bytes to string
print('\n\n*** CSV Example')
sparql.setReturnFormat(CSV)
results = sparql.query().convert()
with open(os.path.join(directory, "results.csv"), "w", encoding="utf-8") as f:
    f.write(results.decode("utf-8"))