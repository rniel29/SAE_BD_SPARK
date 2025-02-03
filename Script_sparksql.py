#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import csv
import json
from SPARQLWrapper import SPARQLWrapper, JSON

# Fonction de demande des acteurs
def demande_acteur():
    liste_acteur = []
    i = 0
    question = int(input("Combien d'acteurs ? : "))
    while i < question:
        liste_acteur.append(input("Donne un nom d'acteur : "))
        i += 1
    return liste_acteur

# Dossier de stockage des résultats
RESULTS_DIR = "./data/"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Fichiers de sortie
CSV_FILE = os.path.join(RESULTS_DIR, "movies_data.csv")
JSON_FILE = os.path.join(RESULTS_DIR, "movies_data.json")

def fetch_movies_for_actors(actors):
    if not (3 <= len(actors) <= 5):
        raise ValueError("La liste des acteurs doit contenir entre 3 et 5 noms.")

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    all_movies = []

    # Création du fichier CSV et ajout des en-têtes
    with open(CSV_FILE, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Titre", "Année", "Acteur", "Naissance Acteur", "Rôle", "Réalisateur", "Naissance Réalisateur", "Genres"])

        for actor in actors:
            query = f'''
            SELECT ?movie ?title (YEAR(MIN(?releaseDate)) AS ?releaseYear)
                   ?casting_acteur ?casting_Birth
                   (SAMPLE(?casting_roleLabel) AS ?casting_name)
                   (SAMPLE(?directorLabel) AS ?directorName)
                   (SAMPLE(?directorBirthDate) AS ?directorBirth)
                   (GROUP_CONCAT(DISTINCT ?genreFilmLabel; separator=", ") AS ?genres)
            WHERE {{
              ?varActeur rdfs:label "{actor}"@fr.
              ?movie wdt:P161 ?varActeur;
                     wdt:P31 wd:Q11424 ;
                     wdt:P1476 ?title ;
                     wdt:P577 ?releaseDate ;
                     wdt:P136 ?genreFilm.
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "fr".
                ?genreFilm rdfs:label ?genreFilmLabel.
              }}
              OPTIONAL {{
                ?movie p:P161 ?castingStatement.
                ?castingStatement ps:P161 ?varActeur;
                                   pq:P453 ?roleEntity.  
                ?roleEntity rdfs:label ?casting_roleLabel. FILTER(LANG(?casting_roleLabel) = "fr")
              }}
              BIND("{actor}" AS ?casting_acteur)
              OPTIONAL {{ ?varActeur wdt:P569 ?casting_Birth. }}
              OPTIONAL {{
                ?movie wdt:P57 ?director.
                ?director rdfs:label ?directorLabel. FILTER(LANG(?directorLabel) = "fr")
                OPTIONAL {{ ?director wdt:P569 ?directorBirthDate. }}
              }}
            }}
            GROUP BY ?movie ?title ?casting_acteur ?casting_Birth ?casting_roleLabel
            ORDER BY ?releaseYear
            LIMIT 3
            '''

            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)

            try:
                results = sparql.query().convert()

                # Extraire les films
                for result in results.get("results", {}).get("bindings", []):
                    movie_data = {
                        "title": result.get("title", {}).get("value", "N/A"),
                        "releaseYear": result.get("releaseYear", {}).get("value", "N/A"),
                        "actor": result.get("casting_acteur", {}).get("value", "N/A"),
                        "actorBirth": result.get("casting_Birth", {}).get("value", "N/A"),
                        "role": result.get("casting_name", {}).get("value", "N/A"),
                        "director": result.get("directorName", {}).get("value", "N/A"),
                        "directorBirth": result.get("directorBirth", {}).get("value", "N/A"),
                        "genres": result.get("genres", {}).get("value", "N/A").split(", ")
                    }

                    # Écrire les données dans le fichier CSV
                    writer.writerow([
                        movie_data["title"],
                        movie_data["releaseYear"],
                        movie_data["actor"],
                        movie_data["actorBirth"],
                        movie_data["role"],
                        movie_data["director"],
                        movie_data["directorBirth"],
                        ", ".join(movie_data["genres"])
                    ])

                    # Ajouter les données à la liste
                    all_movies.append(movie_data)
            except Exception as e:
                print(f"Erreur avec l'acteur {actor}: {e}")

    # Sauvegarde des résultats dans un fichier JSON
    with open(JSON_FILE, mode="w", encoding="utf-8") as json_f:
        json.dump(all_movies, json_f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    actors_list = demande_acteur()
    print(f"Acteurs sélectionnés : {actors_list}")
    try:
        fetch_movies_for_actors(actors_list)
        print("Les résultats ont été enregistrés dans les fichiers CSV et JSON.")
    except Exception as e:
        print(f"Erreur générale: {e}")
