# Guide de mise en production

Ce document résume les changements appliqués pour préparer le projet Django a la production, ainsi que les commandes a utiliser.

## Ce qui a ete modifie

Le fichier [src/Plateforme/settings.py](src/Plateforme/settings.py) a ete ajuste pour:

- lire `SECRET_KEY` depuis les variables d'environnement
- lire `DEBUG` depuis les variables d'environnement
- lire `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` depuis les variables d'environnement
- lire `GOOGLE_GEMINI_API_KEY` depuis les variables d'environnement
- activer les options de securite HTTP quand `DEBUG=False`
- definir `STATIC_ROOT` pour `collectstatic`
- conserver PostgreSQL par defaut avec fallback SQLite

Le fichier [.env.example](.env.example) a ete complete avec:

- variables PostgreSQL
- variables de securite production
- exemples de domaine public

Le fichier [.env.production.example](.env.production.example) a ete ajoute pour fournir un modele directement exploitable sur un serveur de production.

## Code principal ajoute dans settings.py

```python
def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(',') if item.strip()]


SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-only-change-me')
DEBUG = env_bool('DEBUG', True)
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY', '')
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Code de securite active en production:

```python
if not DEBUG:
    SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
    CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', True)
```

## Variables a definir en production

Le point de depart recommande est [.env.production.example](.env.production.example).

Exemple minimal:

```bash
export SECRET_KEY='change-moi-avec-une-cle-longue-et-aleatoire'
export DEBUG=False
export ALLOWED_HOSTS='monsite.com,www.monsite.com'
export CSRF_TRUSTED_ORIGINS='https://monsite.com,https://www.monsite.com'
export GOOGLE_GEMINI_API_KEY='ta_cle_api'

export DB_ENGINE='django.db.backends.postgresql'
export DB_NAME='plateforme_db'
export DB_USER='plateforme_user'
export DB_PASSWORD='mot_de_passe_fort'
export DB_HOST='127.0.0.1'
export DB_PORT='5432'

export SESSION_COOKIE_SECURE=True
export CSRF_COOKIE_SECURE=True
export SECURE_SSL_REDIRECT=True
export SECURE_HSTS_SECONDS=31536000
export SECURE_HSTS_INCLUDE_SUBDOMAINS=True
export SECURE_HSTS_PRELOAD=True
```

Si ton serveur est derriere Nginx, Caddy ou un proxy inverse qui termine HTTPS:

```bash
export USE_X_FORWARDED_PROTO=True
```

## Commandes de verification

Depuis la racine du projet:

```bash
source .env/bin/activate
cd src
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

## Utilisateur PostgreSQL recommande

Ne pas utiliser `postgres` en production. Creer un utilisateur dedie:

```sql
CREATE USER plateforme_user WITH PASSWORD 'mot_de_passe_fort';
ALTER ROLE plateforme_user SET client_encoding TO 'utf8';
ALTER ROLE plateforme_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE plateforme_user SET timezone TO 'America/Port-au-Prince';
GRANT ALL PRIVILEGES ON DATABASE plateforme_db TO plateforme_user;
```

## Ce que j'ai utilise pour la migration SQLite -> PostgreSQL

Export SQLite:

```bash
cd /home/stagiaire/Documents/Python/plateforme/src
DB_ENGINE=django.db.backends.sqlite3 \
DB_NAME=db.sqlite3 \
/home/stagiaire/Documents/Python/plateforme/.env/bin/python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude admin.logentry \
  --exclude sessions \
  > postgres_migration_dump.json
```

Migration schema PostgreSQL:

```bash
DB_ENGINE=django.db.backends.postgresql \
DB_NAME=plateforme_db \
DB_USER=postgres \
DB_PASSWORD='password' \
DB_HOST=127.0.0.1 \
DB_PORT=5432 \
/home/stagiaire/Documents/Python/plateforme/.env/bin/python manage.py migrate
```

Chargement PostgreSQL:

```bash
DB_ENGINE=django.db.backends.postgresql \
DB_NAME=plateforme_db \
DB_USER=postgres \
DB_PASSWORD='password' \
DB_HOST=127.0.0.1 \
DB_PORT=5432 \
/home/stagiaire/Documents/Python/plateforme/.env/bin/python manage.py loaddata postgres_migration_dump.json
```

## Etat actuel

- PostgreSQL fonctionne
- les donnees principales ont ete migrees
- la configuration Django est maintenant compatible production
- il reste a brancher les vraies valeurs de domaine, secrets et HTTPS de ton serveur