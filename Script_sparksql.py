#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF, CSV, TSV
def demande_acteur ():
    liste_acteur=[]
    i=0
    question= int (input("combien d'acteur ? : "))
    while i<question:
        liste_acteur.append(input("donnez un nom d'acteur : "))
        i+=1
    return liste_acteur

directory = "./data/"
if not os.path.exists(directory):
    os.makedirs(directory)

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# SELECT query for JSON, XML, CSV, TSV formats
select_query = """
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?movie ?title (YEAR(MIN(?releaseDate)) AS ?releaseYear)
       ?casting_acteur ?casting_Birth 
       (SAMPLE(?casting_roleLabel) AS ?casting_name) 
       (SAMPLE(?directorLabel) AS ?directorName) 
       (SAMPLE(?directorBirthDate) AS ?directorBirth) 
       (GROUP_CONCAT(DISTINCT ?genreFilmLabel; separator=", ") AS ?genres)
WHERE {
  ?varActeur rdfs:label "Andrew Garfield"@fr.

  # Films où la personne est acteur
  ?movie wdt:P161 ?varActeur;
         wdt:P31 wd:Q11424 ;          # Instance de : Film
         wdt:P1476 ?title ;           # Titre du film
         wdt:P577 ?releaseDate ;      # Date de sortie
         wdt:P136 ?genreFilm.         # Genre du film

  # Récupération des labels pour les genres
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "fr". 
    ?genreFilm rdfs:label ?genreFilmLabel.
  }

  # Nom du personnage joué par l'acteur
  OPTIONAL {
    ?movie p:P161 ?castingStatement.
    ?castingStatement ps:P161 ?varActeur; 
                       pq:P453 ?roleEntity.  # P453 pour le rôle joué
    ?roleEntity rdfs:label ?casting_roleLabel. FILTER(LANG(?casting_roleLabel) = "fr")
  }

  # Données sur l'acteur
  BIND("Andrew Garfield" AS ?casting_acteur)
  OPTIONAL { ?varActeur wdt:P569 ?casting_Birth. } # Date de naissance de l'acteur

  # Données optionnelles sur le réalisateur
  OPTIONAL {
    ?movie wdt:P57 ?director.
    ?director rdfs:label ?directorLabel. FILTER(LANG(?directorLabel) = "fr")
    OPTIONAL { ?director wdt:P569 ?directorBirthDate. }
  }
}
GROUP BY ?movie ?title ?casting_acteur ?casting_Birth ?casting_roleLabel
ORDER BY ?releaseYear
LIMIT 3


"""


print('\n\n*** XML Example')
sparql.setReturnFormat(XML)
results = sparql.query().convert()
with open(os.path.join(directory, "results.xml"), "w", encoding="utf-8") as f:
    f.write(results.toxml())