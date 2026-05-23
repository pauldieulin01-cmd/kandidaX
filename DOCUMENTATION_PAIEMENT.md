# 💳 Système de Paiement MonCash - Documentation

## 📋 Résumé des changements

Un système complet de paiement MonCash a été implémenté pour déverrouiller les niveaux premium (3, 4, 5, 6, 9) de la plateforme.

## 🎯 Tarification par niveau

| Niveau | Nom | Seuil de points | Prix (Gourdes) |
|--------|-----|-----------------|----------------|
| 1-2 | Débutant/Intermédiaire | 0-60 | **GRATUIT** |
| 3 | Avancé | 60-120 | **150G** |
| 4 | Expert | 120-250 | **200G** |
| 5 | Maître | 250-500 | **300G** |
| 6 | Champion | 500-1000 | **400G** |
| 7-8 | Légendaire/Maître Suprême | 1000-2000 | **GRATUIT** |
| 9 | Immortel | 2000+ | **500G** |

## 📂 Fichiers modifiés

### 1. **Models** (`src/Quizapp/models.py`)
- ✅ Ajout des niveaux 8 et 9 dans `get_current_level()`
- ✅ Mise à jour de `get_level_info()` avec les nouveaux niveaux et leurs prix
- ✅ Création de la méthode `has_paid_for_level(level)` pour vérifier le paiement
- ✅ Création de la méthode `get_level_price(level)` pour obtenir le prix
- ✅ **Nouveau modèle `Payment`** pour gérer les paiements:
  - `etudiant`: ForeignKey vers Etudiant
  - `level`: Numéro du niveau
  - `amount`: Montant en gourdes
  - `status`: État du paiement (pending, completed, failed, canceled)
  - `transaction_id`: Référence MonCash
  - `reference`: Référence interne unique
  - `phone_number`: Numéro MonCash de l'étudiant
  - `date_creation` / `date_completion`: Timestamps

### 2. **Views** (`src/Quizapp/views.py`)
- ✅ Modification de `page_question()` pour vérifier le paiement avant d'accéder
- ✅ **Nouvelle vue `paiement_niveau(level)`**: Page pour initiator du paiement
- ✅ **Nouvelle API `initier_paiement_moncash()`**: POST pour créer un paiement
- ✅ **Nouvelle API `verifier_paiement(reference)`**: GET pour vérifier le statut

### 3. **URLs** (`src/Plateforme/urls.py`)
- ✅ Route: `/paiement/niveau/<int:level>/` → `paiement_niveau`
- ✅ Route: `/api/paiement/initier/` → `initier_paiement_moncash`
- ✅ Route: `/api/paiement/verifier/<str:reference>/` → `verifier_paiement`

### 4. **Templates**
- ✅ **`paiement_niveau.html`**: Formulaire de paiement avec:
  - Affichage du niveau et du prix
  - Champ pour le numéro MonCash
  - Instructions claires
  - Design cohérent avec la plateforme
  
- ✅ **`paiement_attente.html`**: Page d'attente avec:
  - Spinner d'attente
  - Détails du paiement
  - Référence de transaction
  - Étapes à suivre
  - Vérification automatique (toutes les 5 secondes)
  - Bouton de vérification manuelle

- ✅ **`levels.html`**: Améliorations:
  - Ajout des niveaux 8 et 9
  - Affichage des prix à côté des niveaux payants
  - Boutons de paiement pour débloquer les niveaux

### 5. **Admin** (`src/Quizapp/admin.py`)
- ✅ Ajout du modèle `Payment` à l'interface admin Django
- ✅ Affichage: référence, étudiant, niveau, montant, statut, téléphone
- ✅ Filtrage par statut, niveau, date

## 🚀 Migrations

Une nouvelle migration a été créée:
```
Quizapp/migrations/0008_payment.py
```

Pour appliquer les migrations:
```bash
python manage.py makemigrations Quizapp
python manage.py migrate
```

## 🔗 Points d'intégration MonCash

Le système est prêt pour l'intégration MonCash. Les placeholders suivants doivent être complétés:

### 1. **Dans `initier_paiement_moncash()`** (views.py ~ligne 335)
```python
# INTÉGRATION MONCASH REQUISE ICI
# Appeler l'API MonCash pour initier le paiement
# payment.transaction_id = response.transaction_id
# payment.save()
```

### 2. **Dans `verifier_paiement()`** (views.py ~ligne 360)
```python
# INTÉGRATION MONCASH REQUISE ICI
# Vérifier le statut avec l'API MonCash
# if moncash_api.check_payment(payment.transaction_id):
#     payment.status = 'completed'
#     payment.date_completion = datetime.now()
#     payment.save()
```

## 📱 Flux d'utilisation

1. **ACCÈS AUX NIVEAUX PAYANTS**
   - Étudiant atteint le score requis pour un niveau payant (3, 4, 5, 6, 9)
   - Tentative d'accès à `page_question` redirige vers `/paiement/niveau/<level>`

2. **INITIATION DU PAIEMENT**
   - Étudiant remplit le numéro MonCash
   - Clique sur "Procéder au paiement"
   - Le système crée un objet `Payment` avec status="pending"
   - Redirection vers `paiement_attente.html`

3. **ATTENTE DE CONFIRMATION**
   - Page affiche la référence de paiement
   - Script JavaScript vérifie automatiquement le statut toutes les 5 secondes
   - Utilisateur peut cliquer "Vérifier le paiement" manuellement
   - Une fois confirmé, redirection vers `page_question`

4. **ACCÈS AU CONTENU**
   - Une fois le paiement confirmé, l'étudiant a accès aux questions du niveau
   - Les futures tentatives d'accès à ce même niveau sont autorisées

## 🔐 Sécurité

- ✅ Les paiements sont stockés en base de données avec statut
- ✅ Vérification au niveau de la requête que le paiement a été effectué
- ✅ Références uniques pour chaque paiement
- ✅ Suivi complet des transactions dans l'admin

## 📊 Gestion dans l'admin

- Voir tous les paiements: `/admin/quizapp/payment/`
- Filtrer par statut (pending, completed, failed, canceled)
- Filtrer par niveau ou date
- Chercher par référence ou téléphone étudiant
- Voir les détails complets et la date de complétion

## 🧪 Test en développement

Vous devez manuellement marquer les paiements comme "completed" dans l'admin pour tester le flux complet (jusqu'à ce que l'API MonCash soit intégrée).

## 📌 Notes importantes

- Les niveaux 1-2, 7-8 restent **totalement gratuits**
- Les niveaux 3, 4, 5, 6, 9 sont **payants**
- Un étudiant ne peut accéder au paiement que s'il a atteint le score requis
- Le système n'actualise pas automatiquement le statut du paiement - il faut utiliser l'API MonCash
- Les références de paiement sont uniques et peuvent servir de numéro de support client
