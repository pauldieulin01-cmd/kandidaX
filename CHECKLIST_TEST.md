# ✅ CHECKLIST DE TEST - Système de Paiement

## 🧪 Tests basiques (sans API MonCash)

### 1. Vérification de la base de données
- [ ] La table `Payment` a bien été créée
  ```bash
  sqlite3 db.sqlite3 ".tables" | grep -i payment
  ```
- [ ] Accédez à `/admin/quizapp/payment/` → Devrait afficher une liste vide

### 2. Vérification des modèles
- [ ] Les méthodes du modèle Etudiant existent:
  - [ ] `has_paid_for_level(level)`
  - [ ] `get_level_price(level)`
  - [ ] `get_current_level()`
  - [ ] `get_level_info()`

### 3. Vérification des vues
- [ ] Les 3 nouvelles vues existent dans `views.py`:
  - [ ] `paiement_niveau(request, level)`
  - [ ] `initier_paiement_moncash(request)`
  - [ ] `verifier_paiement(request, reference)`

### 4. Vérification des URLs
- [ ] Les 3 routes sont enregistrées dans `urls.py`:
  - [ ] `/paiement/niveau/<int>` → paiement_niveau
  - [ ] `/api/paiement/initier/` → initier_paiement_moncash
  - [ ] `/api/paiement/verifier/<ref>` → verifier_paiement

### 5. Vérification des templates
- [ ] `paiement_niveau.html` existe et est valide
- [ ] `paiement_attente.html` existe et est valide
- [ ] `levels.html` affiche maintenant les niveaux 1-9

## 🌐 Tests fonctionnels

### Phase 1: Navigation
- [ ] Accédez à `/progression/`
- [ ] Vérifiez que 9 niveaux s'affichent
- [ ] Vérifiez que les prix s'affichent correctement:
  - Niveaux 3,4,5,6,9: Affichent un montant (150G, 200G, etc.)
  - Niveaux 1,2,7,8: Aucun montant (gratuit)

### Phase 2: Création d'étudiant et accumulation de points
- [ ] Créez un compte de test
- [ ] Accédez à `/question/` pour répondre à des questions
- [ ] Vérifiez que les points s'accumulent (scores affichés au dashboard)

### Phase 3: Accès à un niveau payant
- [ ] Augmentez votre score pour atteindre le niveau 3+ (60+ points)
- [ ] Tentez d'accéder à `/question/` depuis le niveau 3
- [ ] Vous devriez être **redirigé** vers `/paiement/niveau/3/`

### Phase 4: Page de paiement
- [ ] Vérifiez l'affichage du formulaire
- [ ] Vérifiez que le niveau et le prix s'affichent correctement
- [ ] Entrez un numéro de test (ex: 2250000000000)
- [ ] Cliquez sur "Procéder au paiement"
- [ ] Vous devriez voir `/paiement_attente.html`

### Phase 5: Page d'attente
- [ ] Vérifiez l'affichage de la référence de paiement (format: PAY-XXXXXX)
- [ ] Vérifiez les détails du paiement affichés
- [ ] Vérifiez le spinner d'attente
- [ ] Cliquez sur "Retour au tableau de bord" pour revenir
- [ ] Vérifiez les étapes à suivre

## 🛠️ Tests avec API MonCash (après intégration)

### Phase 6: Initiation du paiement sur API
- [ ] Configurez les clés MonCash dans `settings.py`
- [ ] Refaites Phase 4
- [ ] Vérifiez que le paiement a été créé avec `transaction_id`
- [ ] Vérifiez que le statut est "pending"

### Phase 7: Vérification du paiement
- [ ] Sur `/paiement_attente.html`, le script devrait vérifier toutes les 5s
- [ ] Vous pouvez aussi cliquer "Vérifier le paiement" manuellement
- [ ] Si le paiement est confirmé par MonCash (statut="completed"):
  - [ ] Le statut change en "completed" dans la base de données
  - [ ] Redirection vers `/question/`
  - [ ] Accès au contenu du niveau activé

### Phase 8: Vérification du paiement multiple
- [ ] Payez pour le niveau 3
- [ ] Vérifiez que vous avez accès au niveau 3
- [ ] Tentez d'accéder à nouveau au niveau 3
- [ ] Vous devriez avoir un accès direct (pas de redirection paiement)

## 📊 Tests admin

### Phase 9: Gestion dans l'admin Django
- [ ] Accédez à `/admin/quizapp/payment/`
- [ ] Vous devriez voir les paiements créés
- [ ] Vérifiez les colonnes affichées:
  - [ ] reference (ex: PAY-ABCD1234)
  - [ ] Étudiant (nom_complet)
  - [ ] Niveau
  - [ ] Montant
  - [ ] Statut
  - [ ] Numéro de téléphone
  - [ ] Date de création

### Phase 10: Modification manuelle (test sans API)
- [ ] Sélectionnez un paiement "pending"
- [ ] Changez le statut à "completed"
- [ ] Sauvegardez
- [ ] Accédez à `/paiement_attente.html?reference=...`
- [ ] Cliquez "Vérifier le paiement"
- [ ] Vous devriez être redirigé vers `/question/`

## 🔒 Tests de sécurité

- [ ] Un étudiant ne peut pas accéder à `/paiement/niveau/1/` (niveau gratuit)
- [ ] Un étudiant ne peut pas accéder à `/paiement/niveau/10/` (n'existe pas)
- [ ] Les URLs sont protégées `@login_required`
- [ ] Un étudiant ne peut vérifier que ses propres paiements
- [ ] Les références de paiement sont uniques

## 📱 Tests de responsive
- [ ] **Desktop** (1920x1080): Ok
- [ ] **Tablet** (768x1024): Ok
- [ ] **Mobile** (375x667): Ok
- [ ] Les formulaires restent lisibles
- [ ] Les boutons sont cliquables

## 📋 Résultats des tests

### Points de contrôle critiques ✓
- [ ] Compilation sans erreurs: **OK**
- [ ] Base de données: **OK**
- [ ] Routes URL: **OK**
- [ ] Redirection paiement: **OK**
- [ ] Affichage pages: **OK**
- [ ] Admin Django: **OK**

### Bloqueurs éventuels
- [ ] MonCash non intégré (prévu)
- [ ] Variables d'env non configurées (prévu)
- [ ] Port 8000 en usage (ignorable)

## 🚀 Pour démarrer les tests

1. Dans le terminal:
   ```bash
   cd /home/stagiaire/Documents/Python/plateforme/src
   source ../.env/bin/activate
   python manage.py runserver
   ```

2. Accédez à: http://localhost:8000

3. Créez un compte de test

4. Suivez les phases ci-dessus

## 📞 Troubleshooting

**Erreur: "La table Payment n'existe pas"**
```bash
python manage.py migrate Quizapp
```

**Erreur: Vue non trouvée**
- Vérifiez que `views.py` a bien les imports
- Vérifiez que `urls.py` a les bons chemins

**Erreur: Template non trouvé**
- Vérifiez le chemin: `src/Quizapp/templates/quiz_app/paiement_*.html`

**Erreur: CSRF token missing**
- Assurez-vous que `{% csrf_token %}` est dans les formulaires POST

---

**Date**: 23 Avril 2026
**Version**: 1.0
**Statut**: ✅ Prêt pour test
