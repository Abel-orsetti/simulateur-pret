from flask import Flask, request, render_template_string, session, redirect, url_for
from projet1 import pret_immobilier, revenue, SimulateurCrise
import sqlite3
import os
import random
import bcrypt
from dotenv import load_dotenv
import psycopg2
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("CHEMIN DB :", os.path.abspath("database.db"))
app = Flask(__name__)


app.secret_key = os.getenv("SECRET_KEY")

"""
sert à sécuriser les sessions, c'est une clé secrète utilisée pour signer les cookies de session. Elle doit être gardée confidentielle pour éviter les attaques de falsification de session.
"""

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Compte (
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            age INTEGER NOT NULL,
            username TEXT PRIMARY KEY,
            mot_de_passe TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PretEnregistre (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            nom_pret TEXT NOT NULL,
            mensualite REAL NOT NULL,
            salaire REAL NOT NULL,
            credit REAL NOT NULL,
            taux REAL NOT NULL,
            interets REAL NOT NULL,
            duree INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES Compte(username)
        )
    """)
    
    conn.commit()
    conn.close()



def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def username_exists(username):
    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM Compte WHERE username = %s", (username,))
    result = cursor.fetchone()

    conn.close()
    return result is not None

def password_valid(password):
    return (
        len(password) >= 8
        and any(c.isdigit() for c in password)
        and any(c.isalpha() for c in password)
        and any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for c in password)
    )

def create_account(nom, prenom, age, username, mot_de_passe):

    if username_exists(username):
        return "username_exists"

    if not password_valid(mot_de_passe):
        return "password_invalid"

    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Compte (nom, prenom, age, username, mot_de_passe)
        VALUES (%s, %s, %s, %s, %s)
    """, (nom, prenom, age, username, hash_password(mot_de_passe)))

    conn.commit()
    conn.close()

    return "ok"

def supprimer_compte(username):
    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Compte WHERE username = %s",
        (username,)
    )
    cursor.execute("""
        DELETE FROM PretEnregistre WHERE user_id = %s
    """, (username,))
    print("Rows supprimées :", cursor.rowcount)
    print("Suppression de :", username)

    conn.commit()
    conn.close()



@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    supprimer_compte(username)
    session.pop("user", None)

    return redirect(url_for("accueil", success="Compte supprimé avec succès"))



def login(username, mot_de_passe):
    """
    Fonction pour vérifier les identifiants de connexion. 
    Elle récupère le mot de passe hashé depuis la base de données et le compare avec le mot de passe hashé fourni par l'utilisateur.
    """
    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT mot_de_passe FROM Compte WHERE username = %s",
        (username,)
    )

    result = cursor.fetchone()
    conn.close()

    if result and verify_password(mot_de_passe, result[0]):
        print("Connexion réussie ✅")
        return True
    else:
        print("Nom d'utilisateur ou mot de passe incorrect ❌")
        return False
    

@app.route("/login", methods=["POST"])
def login_route():
    """
    Route pour gérer la connexion des utilisateurs.
    Elle récupère les données du formulaire, vérifie les identifiants, puis connecte l'utilisateur s'ils sont corrects.
    """
    username = request.form["username"]
    mot_de_passe = request.form["mot_de_passe"]

    if login(username, mot_de_passe):
        session["user"] = username
        return redirect("/simulateur")
    else:
        return redirect(url_for("accueil", error="Username ou mot de passe incorrect", type="login"))



@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("accueil"))



@app.route("/register", methods=["POST"])
def register():
    """
    Route pour gérer l'inscription des utilisateurs. 
    Elle récupère les données du formulaire, vérifie la validité du nom d'utilisateur et du mot de passe, puis crée un compte si tout est correct.
    """
    nom = request.form["Nom"]
    prenom = request.form["Prenom"]
    age = request.form["age"]
    username = request.form["username"]
    mot_de_passe = request.form["mot_de_passe"]

    result = create_account(nom, prenom, age, username, mot_de_passe)

    if result == "username_exists":
        return redirect(url_for("accueil", error="Username déjà utilisé", type ="username"))

    if result == "password_invalid":
        return redirect(url_for("accueil", error="Mot de passe trop faible", type ="password"))
    
    session["user"] = username

    return redirect(url_for("home"))



@app.route("/")
def accueil():
    error = request.args.get("error")
    type_error = request.args.get("type")
    return render_template_string("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 0;
        }

        /* Centre le contenu */
        .container {
            background: white;
            max-width: 500px;
            margin: 60px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }

        /* Titres */
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }

        h2 {
            color: #34495e;
            margin-bottom: 20px;
        }

        /* Labels */
        label {
            display: block;
            text-align: left;
            font-weight: bold;
            margin-top: 10px;
            color: #555;
        }

        /* Inputs */
        input, select {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            transition: 0.2s;
        }

        input:focus, select:focus {
            border-color: #2c3e50;
            outline: none;
        }

        /* Boutons */
        button {
            width: 100%;
            padding: 12px;
            background: #2c3e50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.2s;
        }

        button:hover {
            background: #34495e;
        }

        /* Séparation des formulaires */
        form {
            margin-bottom: 20px;
        }

        /* Petits textes */
        p {
            color: #666;
        }
        petit {
            font-size: 12px;
            color: #999;
        }
    </style>
    <div class="container">
        <h1>Bienvenue sur ce site</h1>
        <p>Veuillez vous connecter ou créer un compte pour accéder au simulateur de prêt.</p>
        <form action="/register" method="post">
            {% if error and type_error == "username" %}
            <p style="color:red; font-weight:bold;">*  {{ error }}</p>
            {% endif %}

            {% if error and type_error == "password" %}
            <p style="color:red; font-weight:bold;">* {{ error }}</p>
            {% endif %}
            <Label>Nom:</Label>
            <input name="Nom" type="text"><br><br>

            <label>Prénom :</label>
            <input name="Prenom" type="text" required><br><br>
                                  
            <label>Age :</label>
            <input name="age" type="number" step="1" min="1" required><br><br>
                                  
            <label>Username  :</label>
            <input name="username" type="text" required><br><br>

            <label>Mot de passe :  </label>
            <petit>*8 caractères comportant au moins 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial.</petit>
            <input type="password" name="mot_de_passe" required><br><br>

            <button type="submit">Créer mon compte</button>
        </form>
        <form action="/login" method="post"> 
            {% if error and type_error == "login" %}
            <p style="color:red; font-weight:bold;">
                * Username ou mot de passe incorrect
            </p>
            {% endif %}
            <label>Username  :</label>
            <input name="username" type="text" required><br><br>
                                  
            <label>Mot de passe :</label>
            <input type="password" name="mot_de_passe" required><br><br> 
            <button type="submit">Se connecter</button>
        </form>
    </div>                   
            
         
    """,error=error, type_error=type_error)

@app.route("/profil")
def profil():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT nom, prenom, age, username, mot_de_passe
        FROM Compte
        WHERE username =%s
    """, (username,))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return "Utilisateur introuvable"

    nom, prenom, age, username, mot_de_passe = user
    
    return render_template_string("""
        <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eef2f7, #dfe9f3);
            margin: 0;
            padding: 0;
        }

        /* Carte principale */
        .container {
            background: white;
            max-width: 520px;
            margin: 70px auto;
            padding: 30px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            text-align: center;
            transition: 0.2s ease;
        }

        /* Titre */
        h1 {
            color: #2c3e50;
            margin-bottom: 8px;
        }
        h2 {  
            color: #34495e;
            margin-bottom: 20px;
        }

        /* Texte général */
        p {
            color: #555;
            margin: 6px 0;
        }

        /* Labels */
        label, Label {
            display: block;
            text-align: left;
            font-weight: bold;
            margin-top: 12px;
            color: #444;
        }

        /* Infos utilisateur (p dans ton code) */
        .container p {
            background: #f4f6f8;
            padding: 8px;
            border-radius: 8px;
            margin-top: 4px;
            color: #2c3e50;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #2c3e50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.2s;
        }

        button:hover {
            background: #34495e;
        }
        </style>

        <div class="container">
        <h1>Profil de {{username}}</h1>
        <h2>Bienvenue sur votre profil !</h2>
        <form action="/pret_enregistrer" method="get">
            {% if error %}
            <p style="color:red; font-weight:bold;">* {{ error }}</p>
            {% endif %}

            {% if success %}
            <p style="color:green; font-weight:bold;">{{ success }}</p>
            {% endif %}
                                  
            <Label>Nom:</Label>
            <p>{{ nom }}</p><br><br>
                                  
            <label>Prénom :</label>
            <p>{{ prenom }}</p><br><br>
                                  
            <label>Age :</label>
            <p>{{ age }}</p><br><br>
                                  
            <label>Username  :</label>
            <p>{{ username }}</p><br><br>

            <label>Mot de passe :</label>
            <p>****************</p><br><br>

            <button type="submit">Voir mes prêts enregistrés</button>
        </form>


            <a href="/confirm_deconnect" style="
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            background: ##b00020;
            color: white;
            border-radius: 8px;
            text-decoration: none;
            ">
                Déconnexion
            </a>
            <form action="/confirm_delete" method="GET" style="position: fixed; top:20px; left:20px;">
                <button type="submit" style="
                    padding: 10px 15px;
                    background: ##b00020;
                    color: white;
                    border-radius: 8px;
                    border: none;
                    cursor: pointer;
                ">
                    Supprimer mon compte
                </button>
            </form>
            <form action = "/simulateur" method="get" style="position: fixed; bottom:20px; left:20px;">
                <button type="submit">Retour à l'accueil</button>
            </form>
        </div>
                                  
        
        """, username=username, nom=nom, prenom=prenom, age=age, mot_de_passe=mot_de_passe)

@app.route("/donner_un_nom", methods=["POST"])
def donner_un_nom():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    salaire = float(request.form["salaire"])
    credit = float(request.form["credit"])
    taux = float(request.form["taux"])
    duree = int(request.form["duree"])

    return render_template_string("""
                                  
    <style>
                                  
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eef2f7, #dfe9f3);
            margin: 0;
            padding: 0;
        }

        /* Carte principale */
        .container {
            background: white;
            max-width: 520px;
            margin: 70px auto;
            padding: 30px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            text-align: center;
            transition: 0.2s ease;
        }
        /* Labels */
        label {
            color: #2c3e50;
            margin-bottom: 8px;
        }

        /* Inputs */
        input, select {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            transition: 0.2s;
        }

        input:focus, select:focus {
            border-color: #2c3e50;
            outline: none;
        }

        /* Boutons */
        button {
            width: 100%;
            padding: 12px;
            background: #2c3e50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.2s;
        }

        button:hover {
            background: #34495e;
        }
    </style>
        <div class="container">
            <form action="/enregistrer_pret" method="post">
                <input type="hidden" name="salaire" value="{{ salaire }}">
                <input type="hidden" name="credit" value="{{ credit }}">
                <input type="hidden" name="taux" value="{{ taux }}">
                <input type="hidden" name="duree" value="{{ duree }}">
                <Label>Nom du prêt :</Label>
                <input type="text" name="nom_pret" required><br><br>
                <button type="submit">Enregistrer le prêt</button>
            </form>
        </div>
    """, username=username, salaire=salaire, credit=credit, taux=taux, duree=duree)

@app.route("/enregistrer_pret", methods=["POST"])
def enregistrer_pret():

    if "user" not in session:
        return redirect("/")

    username = session["user"]
    nom_pret = request.form["nom_pret"]

    salaire = float(request.form["salaire"])
    credit = float(request.form["credit"])
    taux = float(request.form["taux"])
    duree = int(request.form["duree"])

    salaire_ = revenue()
    salaire_.revenue_annuel = salaire
    salaire_.revenue_net_mensuel()
    pret = pret_immobilier()
    pret.credit = credit
    pret.taux_pret = taux
    pret.dure_en_annee = duree

    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO PretEnregistre
        (user_id, nom_pret, mensualite,salaire, credit, taux, interets, duree)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (username, nom_pret, pret.calcul_mensualite_pret(), salaire, credit, taux, pret.etendue_pret(), duree))

    conn.commit()
    conn.close()

    return redirect("/pret_enregistrer")

@app.route("/pret_enregistrer")
def pret_enregistrer():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    user_id = username

    cursor.execute("""
        SELECT id, credit, mensualite, salaire, interets, taux, duree, nom_pret, engage, mois_rembourses
        FROM PretEnregistre
        WHERE user_id = %s
    """, (username,))

    prets = cursor.fetchall()
    conn.close()

    return render_template_string("""
        <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eef2f7, #dfe9f3);
            margin: 0;
            padding: 0;
        }

        .container {
            background: white;
            max-width: 700px;
            margin: 70px auto;
            padding: 30px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            text-align: center;
        }

        .card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        }

        h2 {
            color: #2c3e50;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        td, th {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: center;
        }
        .progress-circle {
            width: 140px;
            height: 140px;
            border-radius: 50%;
            margin: 20px auto;
            position: relative;

            background:
                conic-gradient(
                    #27ae60 calc(var(--progress) * 1%),
                    #dddddd 0
                );

            transform: rotate(-90deg);

            display: flex;
            align-items: center;
            justify-content: center;
        }

        .progress-circle::before {
            content: "";
            position: absolute;
            width: 100px;
            height: 100px;
            background: white;
            border-radius: 50%;
        }

        .progress-circle span {
            position: relative;
            z-index: 1;
            transform: rotate(90deg);
            font-size: 18px;
            font-weight: bold;
        }
                                  
        .reste-payer {
        margin-top: 15px;
        padding: 12px;
        background-color: #f4f6f9;
        border-left: 5px solid #2c3e50;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
    }
        </style>

        <div class="container">

            <h1>Mes prêts enregistrés</h1>

            {% if prets|length == 0 %}

                <p>Vous n'avez aucun prêt enregistré.</p>

            {% else %}

                {% for pret in prets %}

                <div class="card">

                    <h2>{{ pret[7] }}</h2>

                    <table>

                        <tr>
                            <th>Info</th>
                            <th>Valeur</th>
                        </tr>

                        <tr>
                            <td>Crédit</td>
                            <td>{{ "%.2f"|format(pret[1]) }} €</td>
                        </tr>

                        <tr>
                            <td>Mensualité</td>
                            <td>{{ "%.2f"|format(pret[2]) }} €</td>
                        </tr>
                                  
                        <tr>
                            <td>Intérêts</td>
                            <td>{{ "%.2f"|format(pret[4]) }} €</td>
                        </tr>
                        <tr>
                            <td>Taux</td>
                            <td>{{ pret[5] }} %</td>
                        </tr>

                        <tr>
                            <td>Durée</td>
                            <td>{{ pret[6] }} ans</td>
                        </tr>
                        <tr>
                            <td>Salaire</td>
                            <td>{{ "%.2f"|format(pret[3]) }} €</td>
                        </tr>
                        <a href="/calculer?salaire={{ pret[3] }}&credit={{ pret[1] }}&taux={{ pret[5] }}&duree={{ pret[6] }}"
                            style="
                                    display: inline-block;
                                    margin-right: 100px;
                                    padding:8px 12px;
                                    background:#3498db;
                                    color:white;
                                    border-radius:6px;
                                    text-decoration:none;
                            ">
                                Voir les détails du prêt
                        </a>
                        
                        <form action="/confirm_delete_pret" method="get"
                            style="margin-right: 100px;">

                            <input type="hidden" name="pret_id" value="{{ pret[0] }}">

                            <button type="submit" style="
                                padding: 8px 12px;
                                background: #b00020;
                                color: white;
                                border-radius: 6px;
                                border: none;
                                cursor: pointer;
                            ">
                                Supprimer le prêt
                            </button>
                        </form>
                        

                    </table>
                    {% if pret[8] == 0 %}
                    <form action="/engager_pret" method="post">
                        <input type="hidden" name="pret_id" value="{{ pret[0] }}">
                        <button type="submit">
                            S'engager
                        </button>
                    </form>
                    {% endif %}

                    {% if pret[8] == 1 %}

                    {% set total = pret[6] * 12 %}
                    {% set progression = (pret[9] / total) * 100 %}

                    <div class="progress-circle"
                        style="--progress: {{ progression }}">
                        <span>
                            {{ pret[9] }}/{{ total }}
                        </span>  
                    </div>
                    <div class="reste-payer">
                        💰 Il vous reste à payer :
                        <br><br>
                        {{ "%.2f"|format((pret[2] * pret[6] * 12) - (pret[9] * pret[2])) }} €
                    </div>
                    <br>
                    <form action="/valider_mois" method="post">
                        <input type="hidden" name="pret_id" value="{{ pret[0] }}">
                        <button type="submit"
                            style="display: inline-block;
                            margin-top: 20px;
                            padding: 10px 20px;
                            background: #2c3e50;
                            color: white;
                            border-radius: 8px;
                            text-decoration: none;
                        ">
                            Valider un mois
                        </button>
                    </form>
                    

                    {% endif %}

                </div>

                {% endfor %}

            {% endif %}

            <a href="/profil" style="
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #2c3e50;
                color: white;
                border-radius: 8px;
                text-decoration: none;
            ">
                Retour au profil
            </a>

        </div>
        """, prets=prets)


@app.route("/engager_pret", methods=["POST"])
def engager_pret():

    pret_id = request.form["pret_id"]

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE PretEnregistre
        SET engage = TRUE
        WHERE id = %s
    """, (pret_id,))

    conn.commit()
    conn.close()

    return redirect("/pret_enregistrer")

@app.route("/valider_mois", methods=["POST"])
def valider_mois():

    pret_id = request.form["pret_id"]

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT duree, mois_rembourses
        FROM PretEnregistre
        WHERE id = %s
    """, (pret_id,))

    duree, mois = cursor.fetchone()

    if mois < duree * 12:
        cursor.execute("""
            UPDATE PretEnregistre
            SET mois_rembourses = mois_rembourses + 1
            WHERE id = %s
        """, (pret_id,))

    conn.commit()
    conn.close()

    return redirect("/pret_enregistrer")

@app.route("/confirm_delete_pret", methods=["GET"])
def confirm_delete_pret():
    if "user" not in session:
        return redirect("/")

    pret_id = request.args.get("pret_id")

    return render_template_string("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eef2f7, #dfe9f3);
            margin: 0;
            padding: 0;
        }

        .container {
            background: white;
            max-width: 500px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
            text-align: center;
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }

        button {
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }

        .delete-btn {
            background: ##b00020;
            color: white;
        }

        .cancel-btn {
            background: #2c3e50;
            color: white;
            text-decoration: none;
            display: inline-block;
            margin-left: 10px;
            padding: 10px 15px;
            border-radius: 8px;
        }

        .btn-group {
            margin-top: 20px;
        }
    </style>

    <div class="container">
        <h1>Êtes-vous sûr de vouloir supprimer ce prêt ?</h1>

            <form action="/delete_pret" method="post">
                <input type="hidden" name="pret_id" value="{{ pret_id }}">
                <button class="delete-btn" type="submit">
                    Supprimer le prêt
                </button>
            </form>

            <a href="/profil" class="cancel-btn">
                Annuler
            </a>
        </div>
    </div>
    """,pret_id= pret_id)
@app.route("/delete_pret", methods=["POST"])
def delete_pret():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    pret_id = request.form["pret_id"]

    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM PretEnregistre
        WHERE id = %s AND user_id = %s
    """, (pret_id, username))

    conn.commit()
    conn.close()

    return redirect("/pret_enregistrer")


@app.route("/confirm_deconnect")
def confirm_deconnect():
    if "user" not in session:
        return redirect("/")

    return render_template_string("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eef2f7, #dfe9f3);
            margin: 0;
            padding: 0;
        }

        .container {
            background: white;
            max-width: 500px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
            text-align: center;
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }

        button {
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }

        .delete-btn {
            background: #e74c3c;
            color: white;
        }

        .cancel-btn {
            background: #2c3e50;
            color: white;
            text-decoration: none;
            display: inline-block;
            margin-left: 10px;
            padding: 10px 15px;
            border-radius: 8px;
        }

        .btn-group {
            margin-top: 20px;
        }
    </style>

    <div class="container">
        <h1>Êtes-vous sûr de vouloir déconnecter votre compte ?</h1>

        <div class="btn-group">
            <form action="/logout" method="GET" style="display:inline;">
                <button class="delete-btn" type="submit">
                    Déconnexion
                </button>
            </form>

            <a href="/profil" class="cancel-btn">
                Annuler
            </a>
        </div>
    </div>
    """)

@app.route("/confirm_delete", methods=["GET"])
def confirm_delete():
    if "user" not in session:
        return redirect("/")

    return render_template_string("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eef2f7, #dfe9f3);
            margin: 0;
            padding: 0;
        }

        .container {
            background: white;
            max-width: 500px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
            text-align: center;
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }

        button {
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }

        .delete-btn {
            background: #e74c3c;
            color: white;
        }

        .cancel-btn {
            background: #2c3e50;
            color: white;
            text-decoration: none;
            display: inline-block;
            margin-left: 10px;
            padding: 10px 15px;
            border-radius: 8px;
        }

        .btn-group {
            margin-top: 20px;
        }
    </style>

    <div class="container">
        <h1>Êtes-vous sûr de vouloir supprimer votre compte ?</h1>

        <div class="btn-group">
            <form action="/delete_account" method="post" style="display:inline;">
                <button class="delete-btn" type="submit">
                    Supprimer mon compte
                </button>
            </form>

            <a href="/profil" class="cancel-btn">
                Annuler
            </a>
        </div>
    </div>
    """)


@app.route("/simulateur")
def home():
    if "user" not in session:
        return redirect("/")
    
    username = session["user"]
    return render_template_string("""
    <style>
    body {
        font-family: Arial, sans-serif;
        background: #f4f6f9;
        margin: 0;
        padding: 40px;
    }

    /* Conteneur principal */
    .container {
        background: white;
        padding: 40px;
        border-radius: 12px;
        max-width: 500px;
        margin: auto;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }

    /* Titres */
    h1 {
        color: #2c3e50;
        margin-bottom: 20px;
    }

    /* Label */
    label {
        font-weight: bold;
        color: #555;
    }

    /* Select */
    select {
        width: 100%;
        padding: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
        border-radius: 8px;
        border: 1px solid #ccc;
    }

    /* Bouton */
    button {
        width: 100%;
        padding: 12px;
        background: #2c3e50;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
    }

    button:hover {
        background: #34495e;
    }
    </style>
    <div class="container">
        <h1>Bienvenue {{username}} sur le simulateur de prêt</h1>
        <h2>Veuillez choisir une option :</h2>

        <form action="/pret" method="get">
            <label>Choix :</label>
            <select name="choix">
                <option value="1">Info revenu + prêt</option>
                <option value="2">Comparer prêts</option>
            </select>

            <button type="submit">Valider</button>
        </form>
                                  
            <a href="/profil" style="
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            background: #2c3e50;
            color: white;
            border-radius: 8px;
            text-decoration: none;
            ">
                Profile
            </a>
        
        
    </div>
    """,username=username)

@app.route("/pret")
def calcul_pret():
    if "user" not in session:
        return redirect("/")
    choix = int(request.args.get("choix"))
    if choix == 1:
        return render_template_string("""
        <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 40px;
        }

        /* Conteneur centré */
        form {
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        }

        /* Titres */
        h1 {
            text-align: center;
            color: #2c3e50;
        }

        h2 {
            color: #34495e;
            margin-top: 20px;
        }

        /* Labels */
        label {
            font-weight: bold;
            color: #555;
        }

        /* Inputs */
        input, select {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            transition: 0.2s;
        }

        input:focus, select:focus {
            border-color: #2c3e50;
            outline: none;
        }

        /* Bouton */
        button {
            width: 100%;
            padding: 12px;
            background: #2c3e50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.2s;
        }

        button:hover {
            background: #34495e;
        }
        </style>
        <form action="/calculer" method="get">
            <Label>Veuillez saisir votre salaire annuel brut :</Label>
            <input name="salaire" type="number" step="1"><br><br>

            <label>Crédit :</label>
            <input name="credit" type="number" step="1" min="1" required><br><br>
            <label>Taux (%) :</label>
            <input name="taux" type="number" step="0.01"><br><br>

            <label>Durée (années) :</label>
            <input name="duree" type="number" step="1" min="1" required><br><br>


            <button type="submit">Calculer</button>
    </form>
    <a href="/simulateur" style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        text-decoration: none;
        padding: 10px 20px;
        background: #2c3e50;
        color: white;
        border-radius: 8px;
    ">
        Retour
    </a>
    <a href="/profil" style="
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 15px;
        background: #2c3e50;
        color: white;
        border-radius: 8px;
        text-decoration: none;
    ">
        Profile
    </a>
                                    
    """)
    elif choix == 2:
        return render_template_string("""
        <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 40px;
        }

        /* Conteneur centré */
        form {
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        }

        /* Titres */
        h1 {
            text-align: center;
            color: #2c3e50;
        }

        h2 {
            color: #34495e;
            margin-top: 20px;
        }

        /* Labels */
        label {
            font-weight: bold;
            color: #555;
        }

        /* Inputs */
        input, select {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            transition: 0.2s;
        }

        input:focus, select:focus {
            border-color: #2c3e50;
            outline: none;
        }

        /* Bouton */
        button {
            width: 100%;
            padding: 12px;
            background: #2c3e50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.2s;
        }

        button:hover {
            background: #34495e;
        }
        </style>
                                
        <h1>Comparaison de prêts</h1>
        <form action="/comparaison" method="get">
            <h2>Prêt 1</h2>
            <label>Crédit :</label>
            <input name="credit1" type="number" step="1" min="1" required><br><br>

            <label>Taux (%) :</label>
            <input name="taux1" type="number" step="0.01"><br><br>

            <label>Durée (années) :</label>
            <input name="duree1" type="number" step="1" min="1" required><br><br>

            <h2>Prêt 2</h2>
            <label>Crédit :</label>
            <input name="credit2" type="number" step="1" min="1" required><br><br>

            <label>Taux (%) :</label>
            <input name="taux2" type="number" step="0.01"><br><br>

            <label>Durée (années) :</label>
            <input name="duree2" type="number" step="1" min="1" required><br><br>

            <button type="submit">Comparer</button>
        <a href="/simulateur" style="
            position: fixed;
            bottom: 20px;
            left: 20px;
            text-decoration: none;
            padding: 10px 20px;
            background: #2c3e50;
            color: white;
            border-radius: 8px;
        ">
            Retour
        </a>
        <a href="/profil" style="
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            background: #2c3e50;
            color: white;
            border-radius: 8px;
            text-decoration: none;
        ">
            Profile
        </a>
        """)


# ----------------------------
# CALCUL
# ----------------------------
@app.route("/calculer")
def resultat_choix1():
    salaire_annuel = float(request.args.get("salaire"))
    credit = float(request.args.get("credit"))
    taux = float(request.args.get("taux"))
    duree = int(float(request.args.get("duree")))

    salaire = revenue()
    salaire.revenue_annuel = salaire_annuel
    salaire.revenue_net_mensuel()
    pret = pret_immobilier()
    pret.credit = credit
    pret.taux_pret = taux
    pret.dure_en_annee = duree

    return f"""
    <style>
    body {{
        font-family: Arial, sans-serif;
        margin: 40px;
        background-color: #f4f6f8;
    }}

    .container {{
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }}

    h1 {{
        color: #2c3e50;
    }}

    h2 {{
        color: #34495e;
        margin-top: 30px;
    }}

    .card {{
        background: #ecf0f1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}

    .good {{
        color: green;
        font-weight: bold;
    }}

    .bad {{
        color: red;
        font-weight: bold;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }}

    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }}

    th {{
        background-color: #2c3e50;
        color: white;
    }}

    tr:nth-child(even) {{
        background-color: #f2f2f2;
    }}
    </style>

    <div class="container">

        <h1>💰 Résultat de votre simulation</h1>

            <a href="/profil" style="
        position: absolute;
        top: 80px;
        right: 80px;
        padding: 10px 15px;
        background: #2c3e50;
        color: white;
        border-radius: 8px;
        text-decoration: none;
    ">
        Profile
    </a>

        <div class="card">
            <p><strong>Salaire net mensuel :</strong> {salaire._beauté_chiffre_(str(salaire.revenue_net_mensuel()))} €</p>
            <p><strong>Mensualité :</strong> {pret._beauté_chiffre(str(pret.calcul_mensualite_pret()))} €</p>
            <p><strong>Total remboursé :</strong> {pret._beauté_chiffre(str(pret.montant_total_à_rembourser()))} €</p>
            <p><strong>Intérêts :</strong> {pret._beauté_chiffre(str(pret.etendue_pret()))} €</p>
             <p><strong>Charge / revenu  (Taux d'endettement mensuel) :</strong> {pret._beauté_chiffre(str((pret.calcul_mensualite_pret() / max(salaire.revenue_net_mensuel(),1)) * 100))} %</p>
        </div>

        <h2>📊 Détail du prêt</h2>

        <table>
        <tr>
            <th>Mois</th>
            <th>Intérêt (€)</th>
            <th>Capital (€)</th>
            <th>Restant (€)</th>
        </tr>

        {pret.tableau_html()}  
        </table>

        <h2>📋 Résumé</h2>
        <div class="card">
            {pret.afficher()}
        </div>

        <h2>💡 Conseil</h2>
            <div class="card">
            {pret.capacite_emprunt(salaire.revenue_net_mensuel())}
        </div>

        <br>
       <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-top:20px;
        ">


            <a href="/pret?choix=1" style="
                text-decoration:none;
                padding:10px 20px;
                background:#2c3e50;
                color:white;
                border-radius:8px;
            ">
                Retour
            </a>


            <form action="/donner_un_nom" method="post">
                <input type="hidden" name="salaire" value="{salaire_annuel}">
                <input type="hidden" name="credit" value="{credit}">
                <input type="hidden" name="taux" value="{taux}">
                <input type="hidden" name="duree" value="{duree}">


                <button type="submit" style="
                    padding:10px 20px;
                    background:#2c3e50;
                    color:white;
                    border-radius:8px;
                    border:none;
                    cursor:pointer;
                ">
                    Enregistrer ce prêt
                </button>
            </form>

            <form action="/anticiper_crise" method="get">

                <input type="hidden" name="salaire" value="{salaire_annuel}">
                <input type="hidden" name="credit" value="{credit}">
                <input type="hidden" name="taux" value="{taux}">
                <input type="hidden" name="duree" value="{duree}">

                <button type="submit" style="
                    padding:10px 20px;
                    background:#2c3e50;
                    color:white;
                    border-radius:8px;
                    border:none;
                    cursor:pointer;
                ">
                    Anticiper une crise financière
                </button>
            </form>
        </div>
    </div>
    """

@app.route("/anticiper_crise")
def anticiper_crise():
    salaire_base = float(request.args.get("salaire"))
    credit = float(request.args.get("credit"))
    taux = float(request.args.get("taux"))
    duree = int(float(request.args.get("duree")))

    # simulation crise
    salaire_base_ = revenue()
    salaire_base_.revenue_annuel = salaire_base
    simulateur = SimulateurCrise(salaire_base_.revenue_annuel)
    salaire_crise = simulateur.revenu_apres_crise()

    revenue_crise_ = revenue()
    revenue_crise_.revenue_annuel = salaire_crise
    revenue_crise_.revenue_net_mensuel()

    pret = pret_immobilier()
    pret.credit = credit
    pret.taux_pret = taux
    pret.dure_en_annee = duree

    return f"""
    <style>
    body {{
        font-family: Arial, sans-serif;
        margin: 40px;
        background-color: #f4f6f8;
    }}

    .container {{
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }}

    h1 {{
        color: #2c3e50;
    }}

    h2 {{
        color: #34495e;
        margin-top: 30px;
    }}

    .card {{
        background: #ecf0f1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }}

    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }}

    th {{
        background-color: #2c3e50;
        color: white;
    }}

    tr:nth-child(even) {{
        background-color: #f2f2f2;
    }}
    </style>

    <div class="container">

        <h1>⚠️ Simulation de stress financier (crise économique)</h1>

        <div class="card">
            <p>
                Cette simulation modélise une situation économique incertaine.<br>
                Elle repose sur des probabilités simplifiées :
            </p>

            <ul>
                <li>En période de crise le revenu diminue ~ -30%</li>
            </ul>

            <p>
                ⚠️ Ceci est une simulation statistique et non une prédiction réelle.
            </p>
        </div>

        <h2>📊 Résultats</h2>

        <div class="card">
            <p><strong>Salaire initial :</strong> {pret._beauté_chiffre(str(salaire_base))} €</p>
            <p><strong>Salaire annuel simulé en crise :</strong> {simulateur._beauté_chiffreS(str(salaire_crise))} €</p>
            <p><strong>Salaire net mensuel en crise :</strong> {revenue_crise_._beauté_chiffre_(str(revenue_crise_.revenue_net_mensuel()))} €</p>
            <p><strong>Mensualité du prêt :</strong> {pret._beauté_chiffre(str(pret.calcul_mensualite_pret()))} €</p>
            <p><strong>Charge / revenu en crise (Taux d'endettement mensuel) :</strong> {pret._beauté_chiffre(str((pret.calcul_mensualite_pret() / max(revenue_crise_.revenue_net_mensuel(),1)) * 100))} %</p>
        </div>

        <h2>📊 Détail du prêt</h2>

        <table>
        <tr>
            <th>Mois</th>
            <th>Intérêt (€)</th>
            <th>Capital (€)</th>
            <th>Restant (€)</th>
        </tr>

        {pret.tableau_html()}  
        </table>

        <h2>💡 Conseil </h2>

        <div class="card">
            {pret.capacite_emprunt(revenue_crise_.revenue_net_mensuel())}
        </div>

        <br>

        <a href="/calculer?salaire={salaire_base}&credit={credit}&taux={taux}&duree={duree}" 
           style="
           text-decoration:none;
           padding:10px 20px;
           background:#2c3e50;
           color:white;
           border-radius:8px;
           display:inline-block;
        ">
            Retour simulation normale
        </a>

    </div>
    """



@app.route("/comparaison")
def resultat_choix2():

    credit1 = float(request.args.get("credit1"))
    taux1 = float(request.args.get("taux1"))
    duree1= int(request.args.get("duree1"))

    pret1 = pret_immobilier()
    pret1.credit = credit1
    pret1.taux_pret = taux1
    pret1.dure_en_annee = duree1


    credit2 = float(request.args.get("credit2"))
    taux2 = float(request.args.get("taux2"))     
    duree2= int(request.args.get("duree2"))

    pret2 = pret_immobilier()
    pret2.credit = credit2
    pret2.taux_pret = taux2 
    pret2.dure_en_annee = duree2
    return f"""
    <style>
    body {{
        font-family: Arial;
        background-color: #f4f6f9;
    }}

    .container {{
        display: flex;
        gap: 20px;
        justify-content: center;
    }}

    .card {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        width: 300px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}

    h2 {{
        text-align: center;
        color: #2c3e50;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }}

    td, th {{
        padding: 10px;
        border-bottom: 1px solid #ddd;
        text-align: center;
    }}

    .best {{
        color: green;
        font-weight: bold;
    }}

    .worst {{
        color: red;
    }}

    .compare {{
        margin-top: 40px;
        background: white;
        padding: 20px;
        border-radius: 12px;
        width: 650px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}
    </style>

    <h1 style="text-align:center;">Comparaison des prêts</h1>
    

    <div class="container">

        <div class="card">
            <h2>Prêt n°1</h2>
            <table>
                <tr><th>Info</th><th>Valeur</th></tr>
                <tr><td>Mensualité</td><td>{pret1._beauté_chiffre(str(pret1.calcul_mensualite_pret()))} €</td></tr>
                <tr><td>Total</td><td>{pret1._beauté_chiffre(str(pret1.montant_total_à_rembourser()))} €</td></tr>
                <tr><td>Intérêts</td><td>{pret1._beauté_chiffre(str(pret1.etendue_pret()))} €</td></tr>
            </table>
        </div>

        <div class="card">
            <h2>Prêt n°2</h2>
            <table>
                <tr><th>Info</th><th>Valeur</th></tr>
                <tr><td>Mensualité</td><td>{pret2._beauté_chiffre(str(pret2.calcul_mensualite_pret()))} €</td></tr>
                <tr><td>Total</td><td>{pret2._beauté_chiffre(str(pret2.montant_total_à_rembourser()))} €</td></tr>
                <tr><td>Intérêts</td><td>{pret2._beauté_chiffre(str(pret2.etendue_pret()))} €</td></tr>
            </table>
        </div>

    </div>

    <div class="compare">
        <h2>Résumé de comparaison</h2>
        <table>
            <tr>
                <th></th>
                <th>Prêt 1</th>
                <th>Prêt 2</th>
            </tr>
            <tr>
                <td>Mensualité</td>
                <td class="{'best' if pret1.calcul_mensualite_pret() < pret2.calcul_mensualite_pret() else 'worst'}">
                    {pret1._beauté_chiffre(str(pret1.calcul_mensualite_pret()))} €
                </td>
                <td class="{'best' if pret2.calcul_mensualite_pret() < pret1.calcul_mensualite_pret() else 'worst'}">
                    {pret2._beauté_chiffre(str(pret2.calcul_mensualite_pret()))} €
                </td>
            </tr>
            <tr>
                <td>Total remboursé</td>
                <td class="{'best' if pret1.montant_total_à_rembourser() < pret2.montant_total_à_rembourser() else 'worst'}">
                    {pret1._beauté_chiffre(str(pret1.montant_total_à_rembourser()))} €
                </td>
                <td class="{'best' if pret2.montant_total_à_rembourser() < pret1.montant_total_à_rembourser() else 'worst'}">
                    {pret2._beauté_chiffre(str(pret2.montant_total_à_rembourser()))} €
                </td>
            </tr>
            <tr>
                <td>Intérêts</td>
                <td class="{'best' if pret1.etendue_pret() < pret2.etendue_pret() else 'worst'}">
                    {pret1._beauté_chiffre(str(pret1.etendue_pret()))} €
                </td>
                <td class="{'best' if pret2.etendue_pret() < pret1.etendue_pret() else 'worst'}">
                    {pret2._beauté_chiffre(str(round(pret2.etendue_pret(),2)))} €
                </td>
            </tr>
        </table>

        <h3 style="text-align:center; margin-top:20px;">
            👉 Meilleur choix : 
            {"Prêt 1" if pret1.montant_total_à_rembourser() < pret2.montant_total_à_rembourser() else "Prêt 2"}
        </h3>
    </div>

    <br><br>
    <div style="text-align:left;">
        <a href="/" style="text-decoration:none; padding:10px 20px; background:#2c3e50; color:white; border-radius:8px;">
            Retour
        </a>
    </div>

    <form action="/details" method="get">
        <input type="hidden" name="credit1" value="{credit1}">
        <input type="hidden" name="taux1" value="{taux1}">
        <input type="hidden" name="duree1" value="{duree1}">

        <input type="hidden" name="credit2" value="{credit2}">
        <input type="hidden" name="taux2" value="{taux2}">
        <input type="hidden" name="duree2" value="{duree2}">

        <div style="text-align:right;">
            <button type="submit" style="
                text-decoration:none;
                padding:10px 20px;
                background:#2c3e50;
                color:white;
                border-radius:8px;
                border:none;
                cursor:pointer;
            ">
                Voir les détails
            </button>
            <a href="/profil" style="
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 15px;
                background: #2c3e50;
                color: white;
                border-radius: 8px;
                text-decoration: none;
            ">
                Profile
            </a>
        </div>
    </form>
    """
@app.route("/details")
def details_comparaison():
    credit1 = float(request.args.get("credit1"))
    taux1 = float(request.args.get("taux1"))
    duree1 = int(request.args.get("duree1"))

    credit2 = float(request.args.get("credit2"))
    taux2 = float(request.args.get("taux2"))
    duree2 = int(request.args.get("duree2"))

    pret1 = pret_immobilier()
    pret1.credit = credit1
    pret1.taux_pret = taux1
    pret1.dure_en_annee = duree1

    pret2 = pret_immobilier()
    pret2.credit = credit2
    pret2.taux_pret = taux2
    pret2.dure_en_annee = duree2
    return f"""
    <style>
    body {{
        font-family: Arial, sans-serif;
        margin: 40px;
        background-color: #f4f6f8;
    }}

    .container {{
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }}

    h1 {{
        color: #2c3e50;
    }}

    h2 {{
        color: #34495e;
        margin-top: 30px;
    }}

    .card {{
        background: #ecf0f1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}

    .good {{
        color: green;
        font-weight: bold;
    }}

    .bad {{
        color: red;
        font-weight: bold;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }}

    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }}

    th {{
        background-color: #2c3e50;
        color: white;
    }}

    tr:nth-child(even) {{
        background-color: #f2f2f2;
    }}

    .compare {{
        margin-top: 40px;
        background: white;
        padding: 20px;
        border-radius: 12px;
        width: 650px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}
    </style>

    <div class="container">
        <a href="/profil" style="
            position: absolute;
            top: 80px;
            right: 80px;
            padding: 10px 15px;
            background: #2c3e50;
            color: white;
            border-radius: 8px;
            text-decoration: none;
        ">
            Profile
        </a>

        <h1>💰 Voici les détails de vos deux prêts.</h1>
        <h1>Prêt n°1</h1>

        <div class="card">
            <p><strong>Mensualité :</strong> {pret1._beauté_chiffre(str(pret1.calcul_mensualite_pret()))} €</p>
            <p><strong>Total remboursé :</strong> {pret1._beauté_chiffre(str(pret1.montant_total_à_rembourser()))} €</p>
            <p><strong>Intérêts :</strong> {pret1._beauté_chiffre(str(pret1.etendue_pret()))} €</p>
        </div>

        <h2>📊 Détail du prêt n°1</h2>

        <table>
        <tr>
            <th>Mois</th>
            <th>Intérêt (€)</th>
            <th>Capital (€)</th>
            <th>Restant (€)</th>
        </tr>

        {pret1.tableau_html()}  
        </table>

        <h2>📋 Résumé du prêt n°1</h2>
        <div class="card">
            {pret1.afficher()}
        </div>

        <h1>Prêt n°2</h1>

        <div class="card">
            <p><strong>Mensualité :</strong> {pret2._beauté_chiffre(str(pret2.calcul_mensualite_pret()))} €</p>
            <p><strong>Total remboursé :</strong> {pret2._beauté_chiffre(str(pret2.montant_total_à_rembourser()))} €</p>
            <p><strong>Intérêts :</strong> {pret2._beauté_chiffre(str(pret2.etendue_pret()))} €</p>
        </div>

        <h2>📊 Détail du prêt n°2</h2>

        <table>
        <tr>
            <th>Mois</th>
            <th>Intérêt (€)</th>
            <th>Capital (€)</th>
            <th>Restant (€)</th>
        </tr>

        {pret2.tableau_html()}  
        </table>

        <h2>📋 Résumé du prêt n°2</h2>
        <div class="card">
            {pret2.afficher()}
        </div>

        <div class="compare">
            <h2>Comparaison</h2>
            {pret1.compare(pret2)}
        </div>

        <br>

        <a href="/pret?choix=2" style="
        bottom: 20px;
        left: 20px;
        text-decoration: none;
        padding: 10px 20px;
        background: #2c3e50;
        color: white;
        border-radius: 8px;
        ">
            Retour
        </a>

    </div>
    """



if __name__ == "__main__":
    init_db()
    app.run(debug=True)