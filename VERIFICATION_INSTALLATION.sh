#!/bin/bash

echo "🔍 Vérification de l'installation du système de paiement MonCash"
echo "=================================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

passed=0
failed=0

# Fonction de vérification
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $1"
        ((failed++))
    fi
}

# 1. Vérifier les fichiers de modèle
echo "📋 Étape 1: Vérification des fichiers"
[ -f "src/Quizapp/models.py" ] && grep -q "class Payment" src/Quizapp/models.py
check "Modèle Payment dans models.py"

[ -f "src/Quizapp/views.py" ] && grep -q "def paiement_niveau" src/Quizapp/views.py
check "Vue paiement_niveau dans views.py"

[ -f "src/Quizapp/views.py" ] && grep -q "def initier_paiement_moncash" src/Quizapp/views.py
check "API initier_paiement_moncash dans views.py"

[ -f "src/Quizapp/views.py" ] && grep -q "def verifier_paiement" src/Quizapp/views.py
check "API verifier_paiement dans views.py"

# 2. Vérifier les templates
echo ""
echo "🎨 Étape 2: Vérification des templates"
[ -f "src/Quizapp/templates/quiz_app/paiement_niveau.html" ]
check "Template paiement_niveau.html"

[ -f "src/Quizapp/templates/quiz_app/paiement_attente.html" ]
check "Template paiement_attente.html"

grep -q "level_num == 8" src/Quizapp/templates/quiz_app/levels.html
check "Niveau 8 dans levels.html"

grep -q "level_num == 9" src/Quizapp/templates/quiz_app/levels.html
check "Niveau 9 dans levels.html"

# 3. Vérifier les URLs
echo ""
echo "🔗 Étape 3: Vérification des URLs"
grep -q "paiement_niveau" src/Plateforme/urls.py
check "Route paiement_niveau dans urls.py"

grep -q "initier_paiement_moncash" src/Plateforme/urls.py
check "Route initier_paiement_moncash dans urls.py"

grep -q "verifier_paiement" src/Plateforme/urls.py
check "Route verifier_paiement dans urls.py"

# 4. Vérifier l'admin
echo ""
echo "👨‍💼 Étape 4: Vérification de l'admin"
grep -q "class PaymentAdmin" src/Quizapp/admin.py
check "Admin PaymentAdmin créé"

grep -q "@admin.register(Payment)" src/Quizapp/admin.py
check "Payment enregistré à l'admin"

# 5. Vérifier les migrations
echo ""
echo "🗄️  Étape 5: Vérification des migrations"
[ -f "src/Quizapp/migrations/0008_payment.py" ]
check "Migration 0008_payment.py créée"

# 6. Vérifier la documentation
echo ""
echo "📚 Étape 6: Vérification de la documentation"
[ -f "RESUME_MODIFICATIONS.md" ]
check "Documentation RESUME_MODIFICATIONS.md"

[ -f "DOCUMENTATION_PAIEMENT.md" ]
check "Documentation DOCUMENTATION_PAIEMENT.md"

[ -f "INTEGRATION_MONCASH.md" ]
check "Documentation INTEGRATION_MONCASH.md"

[ -f "CHECKLIST_TEST.md" ]
check "Documentation CHECKLIST_TEST.md"

[ -f "DEMARRAGE_RAPIDE.md" ]
check "Documentation DEMARRAGE_RAPIDE.md"

[ -f ".env.example" ]
check "Fichier .env.example"

# 7. Vérifier les méthodes du modèle
echo ""
echo "🔧 Étape 7: Vérification des méthodes Etudiant"
grep -q "def has_paid_for_level" src/Quizapp/models.py
check "Méthode has_paid_for_level()"

grep -q "def get_level_price" src/Quizapp/models.py
check "Méthode get_level_price()"

grep -q "'8':" src/Quizapp/models.py
check "Niveau 8 dans get_current_level()"

grep -q "'9':" src/Quizapp/models.py
check "Niveau 9 dans get_current_level()"

# Résumé
echo ""
echo "=================================================================="
echo "📊 Résumé:"
echo -e "   ${GREEN}✓ Réussi: $passed${NC}"
echo -e "   ${RED}✗ Échoué: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ Installation complète et réussie!${NC}"
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "   1. Lire DEMARRAGE_RAPIDE.md"
    echo "   2. Lancer: python manage.py migrate"
    echo "   3. Lancer: python manage.py runserver"
    exit 0
else
    echo -e "${RED}✗ Certains fichiers manquent. Veuillez vérifier.${NC}"
    exit 1
fi
