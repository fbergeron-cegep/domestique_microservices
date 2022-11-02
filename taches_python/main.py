from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel

import mariadb

import sys

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="root",
        host="localhost",
        port=3306,
        database="domestique"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cursor = conn.cursor()

app = FastAPI()


class TacheForm(BaseModel):
    nom_tache: str
    due_pour: str


class TacheBD(BaseModel):
    id: int
    nom_tache: str
    due_pour: str


@app.on_event("startup")
def creer_bd():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taches (
        id INT NOT NULL AUTO_INCREMENT,
        nom text NOT NULL,
        due_pour text NOT NULL,
        PRIMARY KEY (id)
        );
    """)
    conn.commit()

@app.get("/")
def root():
    return {"message": "Bienvenu au protocole domestique en REST"}


# response_model permet de spécifier le format de la réponse
# si je respecte pas le format, FastApi me donne une erreur
# validation à la sortie gratuite!
@app.post("/taches", status_code=201, response_model=TacheBD)
def ajouter_tache(tache: TacheForm):
    cursor.execute("INSERT INTO taches(nom, due_pour) VALUES(?, ?)", (tache.nom_tache, tache.due_pour,))
    conn.commit()
    return recuperer_tache(cursor.lastrowid)


@app.delete("/taches/{id_tache}", response_model=TacheBD)
def retirer_tache(id_tache: int):
    tache = recuperer_tache(id_tache)
    if tache is None:
        raise HTTPException(status_code=404, detail=f"Une tâche ayant l'identifiant {id_tache} n'a pu être trouvée")
    cursor.execute("DELETE FROM taches WHERE id = ?", (tache.id,))
    conn.commit()
    return tache


@app.get("/taches", response_model=List[TacheBD])
def recuperer_taches():
    cursor.execute("SELECT id, nom, due_pour FROM taches")
    tuples_tache = cursor.fetchall()
    taches = [TacheBD(id=t[0], nom_tache=t[1], due_pour=t[2]) for t in tuples_tache]
    return taches


@app.get("/taches/{id_tache}", response_model=TacheBD)
def recuperer_tache(id_tache: int):
    cursor.execute("SELECT id, nom, due_pour FROM taches WHERE id = ?", (id_tache,))
    tuple_tache = cursor.fetchone()
    if tuple_tache is None:
        raise HTTPException(status_code=404, detail=f"Une tâche ayant l'identifiant {id_tache} n'a pu être trouvée")
    # fetchone retourne un tuple. FastAPI fait la conversion avant de lancer vers le client,
    # mais pas lorsque je l'appelle de l'interne. Donc je dois créer mon objet moi-même
    tache: TacheBD = TacheBD(id=tuple_tache[0], nom_tache=tuple_tache[1], due_pour=tuple_tache[2])
    return tache
