# Migration 0011 — Simplification des modèles
# À appliquer après les migrations existantes (0001-0010)
# 
# ATTENTION : cette migration adapte les champs existants.
# Exécuter : python manage.py migrate Quizapp
#
# Ce fichier documente les changements à apporter manuellement
# si vous migrez depuis l'ancienne version :
#
#   1. Etudiant.niveau     → renommer en serie
#   2. Etudiant.niveau_actuel (IntegerField, default=1) → NOUVEAU
#   3. Quiz.level (IntegerField, default=1)             → NOUVEAU
#   4. Quiz.termine (BooleanField, default=False)       → NOUVEAU
#   5. Reponse.valeur (CharField 500)                   → remplace reponse_text/bool/choice
#   6. Payment.date_completion  → déjà présent
#
# Script de migration Django à créer :
 
from django.db import migrations, models
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ('Quizapp', '0010_quiz_is_retry_mode_quiz_parent_quiz'),
    ]
 
    operations = [
        # Ajouter niveau_actuel à Etudiant
        migrations.AddField(
            model_name='etudiant',
            name='niveau_actuel',
            field=models.IntegerField(default=1),
        ),
        # Ajouter level à Quiz
        migrations.AddField(
            model_name='quiz',
            name='level',
            field=models.IntegerField(default=1),
        ),
        # Ajouter termine à Quiz
        migrations.AddField(
            model_name='quiz',
            name='termine',
            field=models.BooleanField(default=False),
        ),
        # Ajouter valeur à Reponse (champ unifié)
        migrations.AddField(
            model_name='reponse',
            name='valeur',
            field=models.CharField(max_length=500, blank=True, null=True),
        ),
        # Renommer niveau → serie dans Etudiant
        migrations.RenameField(
            model_name='etudiant',
            old_name='niveau',
            new_name='serie',
        ),
    ]
 
