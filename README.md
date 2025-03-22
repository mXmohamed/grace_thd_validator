# GRACE THD Validator

Application web pour la validation des données GRACE THD (Géoréférencement des Réseaux d'Amélioration des Communications Électroniques pour la Très Haute Définition).

## Présentation

GRACE THD Validator est une application qui permet d'importer, de visualiser et de valider des données selon le modèle GRACE THD, un standard pour la gestion des réseaux de fibre optique.

Cette version se concentre sur la validation des tables `t_adresse` et `t_organisme` et sera progressivement étendue aux autres tables du modèle GRACE THD.

## Fonctionnalités

- Importation unifiée de toutes les tables GRACE THD depuis un fichier ZIP
- Validation automatique des données selon les règles du modèle GRACE THD
- Génération d'un rapport de validation unique au format CSV
- Visualisation des adresses et organismes avec pagination
- Affichage détaillé des adresses et organismes
- API REST pour interagir avec l'application programmatiquement

## Installation

### Prérequis

- Python 3.8 ou supérieur
- PostgreSQL 12 ou supérieur avec l'extension PostGIS
- Base de données GRACE THD existante

### 1. Cloner le dépôt

```bash
git clone https://github.com/mXmohamed/grace_thd_validator.git
cd grace_thd_validator
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l'environnement virtuel

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Créer un fichier `.env`

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
SECRET_KEY=votre_cle_secrete
DATABASE_URL=postgresql://username:password@localhost/grace_thd
```

Remplacez `username`, `password` et éventuellement `localhost` par vos informations de connexion à PostgreSQL.

### 6. Initialiser la base de données

Assurez-vous que votre base de données PostgreSQL est créée et contient les schémas et tables GRACE THD (exécutez les scripts SQL fournis dans le dossier `sql` si nécessaire).

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Lancer l'application

```bash
python run.py
```

L'application sera accessible à l'adresse `http://127.0.0.1:5000/`

## Utilisation

1. Accédez à l'application via votre navigateur
2. Utilisez l'onglet "Importer" pour télécharger votre fichier ZIP contenant les tables GRACE THD
3. Un rapport de validation sera automatiquement généré après l'importation
4. Téléchargez le rapport pour consulter les résultats des contrôles (OK ou NOK)
5. Consultez la liste des adresses et organismes pour plus de détails

## Extension à d'autres tables

Cette version se concentre sur les tables `t_adresse` et `t_organisme`. Les prochaines versions intégreront la validation d'autres tables du modèle GRACE THD, comme `t_cable`, `t_site`, `t_ebp`, etc.

## Licence

Ce projet est distribué sous licence MIT.
