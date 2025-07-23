# Analyse Intelligente de CV

Ce projet est une application web pour l'analyse intelligente de CV par rapport à une fiche de poste en utilisant l'API Google Gemini.

## Stack Technologique

- **Backend**: Python 3.10+ avec FastAPI
- **Frontend**: React.js
- **Base de données**: PostgreSQL
- **Analyse IA**: Google Gemini API

## Installation et Lancement

### 1. Backend

Assurez-vous d'avoir Python et pip installés.

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
# Créez un fichier .env à partir de .env.example et remplissez-le
cp .env.example .env
nano .env # ou tout autre éditeur

# Initialiser la base de données (si vous utilisez Alembic pour les migrations)
# alembic upgrade head

# Lancer le serveur
uvicorn app.main:app --reload
```
Le serveur backend sera disponible sur `http://127.0.0.1:8000`.

### 2. Frontend

Assurez-vous d'avoir Node.js et npm (ou yarn) installés.

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm start
```
L'interface sera disponible sur `http://localhost:3000`.

### 3. Base de Données PostgreSQL

Vous devez avoir une instance PostgreSQL en cours d'exécution. Créez une base de données et un utilisateur pour l'application, puis configurez l'URL de la base de données dans le fichier `.env` du backend."# AnalyseIntelligenteCV" 
