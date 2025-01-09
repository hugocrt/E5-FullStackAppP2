import sqlite3

# Connexion à la base de données SQLite (elle sera créée si elle n'existe pas)
conn = sqlite3.connect('databasetest.db')
cursor = conn.cursor()

# Suppression des tables existantes si elles existent déjà (optionnel)
cursor.execute("DROP TABLE IF EXISTS answers")
cursor.execute("DROP TABLE IF EXISTS questions")
cursor.execute("DROP TABLE IF EXISTS scores")

# Création de la table "questions"
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    image TEXT
)
""")

# Création de la table "answers"
cursor.execute("""
CREATE TABLE IF NOT EXISTS answers (
    question_id INTEGER NOT NULL,
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    is_correct INTEGER COLLATE BINARY,
    FOREIGN KEY(question_id) REFERENCES questions(question_id)
)
""")

# Création de la table "scores"
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL UNIQUE,
    score NUMERIC,
    date TEXT NOT NULL
)
""")

# Sauvegarder les modifications et fermer la connexion
conn.commit()
conn.close()

print("Base de données créée avec succès avec les tables 'answers', 'questions', et 'scores'.")
