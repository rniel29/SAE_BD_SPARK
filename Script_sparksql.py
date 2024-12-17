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
demande_acteur()
directory = "./data/"
if not os.path.exists(directory):
    os.makedirs(directory)

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# SELECT query for JSON, XML, CSV, TSV formats
select_query = """
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX ps: <http://www.wikidata.org/prop/statement/value/>
PREFIX bd: <http://www.bigdata.com/rdf#>
SELECT DISTINCT ?movie ?title (YEAR(?releaseDate) AS ?releaseYear) ?genreFilmLabel 
?casting_acteur ?casting_Birth ?casting_role
?directorLabel ?directorBirthDate
WHERE {
  ?varActeur rdfs:label "Louis de Funès"@fr.
  
  # Films où Louis de Funès est acteur
  ?movie wdt:P161 ?varActeur;
         wdt:P31 wd:Q11424 ;          # Instance de : Film
         wdt:P1476 ?title ;           # Titre du film
         wdt:P577 ?releaseDate ;      # Date de sortie
         wdt:P136 ?genreFilm.         # Genre du film
  
  # Récupération des labels pour les genres
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "fr". # Priorité au français pour les labels
    ?genreFilm rdfs:label ?genreFilmLabel.
  }
  
  # Nom du personnage joué par Louis de Funès
  OPTIONAL {
    ?movie p:P161 ?castingStatement.           # Déclaration de casting
    ?castingStatement ps:P161 ?varActeur;        # Louis de Funès est l'acteur
                       pq:P453 ?roleEntity.    # Propriété "joue le rôle de"
    ?roleEntity rdfs:label ?casting_role. FILTER(LANG(?casting_role) = "fr")
  }

  # Données sur Louis de Funès (acteur)
  BIND(?varActeur AS ?casting_acteur)    # Nom explicite
  OPTIONAL { wd:Q2737 wdt:P569 ?casting_Birth. } # Date de naissance de Louis de Funès

  # Données optionnelles sur le réalisateur
  OPTIONAL {
    ?movie wdt:P57 ?director.
    ?director rdfs:label ?directorLabel. FILTER(LANG(?directorLabel) = "fr")
    
    # Date de naissance du réalisateur
    OPTIONAL { ?director wdt:P569 ?directorBirthDate. }
  }
}
ORDER BY ?releaseYear


"""
sparql.setQuery(select_query)
print('\n\n*** CSV Example')
sparql.setReturnFormat(CSV)
results = sparql.query().convert()
with open(os.path.join(directory, "results.csv"), "w", encoding="utf-8") as f:
    f.write(results.decode("utf-8"))