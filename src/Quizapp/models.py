from django.db import models
from django.contrib.auth.models import User
 
 
# ──────────────────────────────────────────────────────────────
# ÉTUDIANT
# ──────────────────────────────────────────────────────────────
class Etudiant(models.Model):
    NIVEAU_CHOICES = [
        ('MP',  'Série MP'),
        ('SVT', 'Série SVT'),
        ('SES', 'Série SES'),
        ('LLA', 'Série LLA'),
    ]
    OPTION_CHOICES = [
        ('Genie',       'Génie'),
        ('Medecine',    'Médecine / Sces infirmières'),
        ('Agronomie',   'Sces agronomiques'),
        ('Humaines',    'Sces humaines'),
        ('Education',   'Sces éducation'),
        ('Economiques', 'Sces économiques'),
        ('Juridiques',  'Sces juridiques'),
    ]
    ENTITE_CHOICES = [
        ('FMP',      'FACULTÉ DE MÉDECINE ET DE PHARMACIE'),
        ('CHCL',     'CAMPUS HENRY CHRISTOPHE DE LIMONADE'),
        ('FASCH',    'FACULTÉ DES SCIENCES HUMAINES'),
        ('FDS',      'FACULTÉ DES SCIENCES'),
        ('FDSE',     'FACULTÉ DE DROIT ET DES SCIENCES ÉCONOMIQUES'),
        ('ENS',      'ÉCOLE NORMALE SUPÉRIEURE'),
        ('FAMV',     'FACULTÉ D\'AGRONOMIE ET DE MÉDECINE VÉTÉRINAIRE'),
        ('INAGHEI',  'INAGHEI'),
        ('FE',       'FACULTÉ D\'ETHNOLOGIE'),
        ('FLA',      'FACULTÉ DE LINGUISTIQUE APPLIQUÉE'),
        ('AUTRE',    'Autre'),
    ]
 
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    nom_complet    = models.CharField(max_length=100)
    serie          = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='MP')
    option         = models.CharField(max_length=50, choices=OPTION_CHOICES, default='Genie')
    entite         = models.CharField(max_length=100, choices=ENTITE_CHOICES, default='FDS')
    score_total    = models.IntegerField(default=0)
    niveau_actuel  = models.IntegerField(default=1)   # niveau courant (1-9)
    photo          = models.ImageField(
                        upload_to='photos_etudiants/',
                        null=True, blank=True,
                        default='photos_etudiants/default.png')
    date_inscription = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.nom_complet
 
    # ── Paliers de niveaux ──────────────────────────────────
    # Niveau N est débloqué quand score_total >= seuil[N]
    SEUILS = {
        1: 0,
        2: 10,
        3: 20,
        4: 40,
        5: 70,
        6: 110,
        7: 160,
        8: 220,
        9: 300,
    }
    NOMS_NIVEAUX = {
        1: 'Débutant',
        2: 'Intermédiaire',
        3: 'Avancé',
        4: 'Expert',
        5: 'Maître',
        6: 'Champion',
        7: 'Légendaire',
        8: 'Maître Suprême',
        9: 'Immortel',
    }
    # Niveaux payants → prix en gourdes
    PRIX_NIVEAUX = {
        3: 150,
        4: 200,
        5: 300,
        6: 400,
        7: 500,
        8: 600,
        9: 700,
    }
 
    def niveau_score(self):
        """Niveau calculé uniquement à partir du score."""
        lvl = 1
        for n, seuil in sorted(self.SEUILS.items()):
            if self.score_total >= seuil:
                lvl = n
        return lvl
 
    def get_current_level(self):
        """Niveau réel = max(niveau_score, niveau_actuel débloqué par paiement)."""
        return max(self.niveau_score(), self.niveau_actuel)
 
    def is_paid_level(self, level):
        """Vrai si le niveau est gratuit, si l'admin a débloqué ce niveau
        (niveau_actuel >= level), ou si l'étudiant a un paiement complété."""
        if level not in self.PRIX_NIVEAUX:
            return True
        # L'admin a manuellement accordé l'accès à ce niveau (ou à un niveau supérieur)
        if self.niveau_actuel >= level:
            return True
        return Payment.objects.filter(
            etudiant=self, level=level, status='completed'
        ).exists()
 
    def get_level_price(self, level):
        return self.PRIX_NIVEAUX.get(level, 0)
 
    def points_to_next(self):
        cur = self.get_current_level()
        nxt = cur + 1
        if nxt > 9:
            return 0
        return max(0, self.SEUILS.get(nxt, 0) - self.score_total)
 
    def level_info(self):
        lvl = self.get_current_level()
        return {
            'numero': lvl,
            'nom':    self.NOMS_NIVEAUX.get(lvl, ''),
            'prix':   self.PRIX_NIVEAUX.get(lvl, 0),
        }
 
 
# ──────────────────────────────────────────────────────────────
# MATIÈRE

class Matiere(models.Model):
    nom = models.CharField(max_length=100)
 
    def __str__(self):
        return self.nom
 
 
# ──────────────────────────────────────────────────────────────
# QUESTION

class Question(models.Model):
    TYPE_CHOICES = [
        ('QCM', 'Choix multiples'),
        ('VF',  'Vrai / Faux'),
        ('OUV', 'Réponse ouverte'),
    ]
    DIFFICULTE_CHOICES = [
        (1, 'Facile'),
        (2, 'Moyen'),
        (3, 'Difficile'),
        (4, 'Très difficile'),
        (5, 'Expert'),
    ]
 
    matiere        = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    texte          = models.TextField()
    type_question  = models.CharField(max_length=3, choices=TYPE_CHOICES, default='QCM')
    difficulte     = models.IntegerField(choices=DIFFICULTE_CHOICES, default=1)
    niveau_requis  = models.IntegerField(default=1)
 
    # QCM
    choix_a        = models.CharField(max_length=255, blank=True, null=True)
    choix_b        = models.CharField(max_length=255, blank=True, null=True)
    choix_c        = models.CharField(max_length=255, blank=True, null=True)
    choix_d        = models.CharField(max_length=255, blank=True, null=True)
    reponse_correcte = models.CharField(
        max_length=10, blank=True, null=True,
        help_text="A, B, C ou D (ou combiné A,C)"
    )
    # VF
    reponse_vf     = models.BooleanField(blank=True, null=True)
    # OUV
    reponse_ouverte = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return f"[N{self.niveau_requis}] {self.texte[:60]}"
 
    def is_correct(self, reponse):
        if self.type_question == 'QCM':
            corrects = [r.strip().upper() for r in (self.reponse_correcte or '').split(',')]
            return (reponse or '').upper() in corrects
        elif self.type_question == 'VF':
            return str(reponse).lower() == str(self.reponse_vf).lower()
        elif self.type_question == 'OUV':
            return (reponse or '').lower().strip() == (self.reponse_ouverte or '').lower().strip()
        return False
 
 
# ──────────────────────────────────────────────────────────────
# QUIZ  (une session de questions pour un étudiant)

class Quiz(models.Model):
    etudiant       = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    level          = models.IntegerField(default=1)
    matiere        = models.ForeignKey(Matiere, on_delete=models.SET_NULL, null=True, blank=True)
    questions      = models.ManyToManyField(Question, blank=True)
    score          = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    termine        = models.BooleanField(default=False)
    date_creation  = models.DateTimeField(auto_now_add=True)
    date_fin       = models.DateTimeField(null=True, blank=True)
    is_retry_mode  = models.BooleanField(default=False)
    parent_quiz    = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='retry_quizzes'
    )
 
 
# ──────────────────────────────────────────────────────────────
# RÉPONSE
# ──────────────────────────────────────────────────────────────
class Reponse(models.Model):
    quiz          = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='reponses')
    question      = models.ForeignKey(Question, on_delete=models.CASCADE)
    valeur        = models.CharField(max_length=500, blank=True, null=True)
    est_correcte  = models.BooleanField(default=False)
 
    def __str__(self):
        return f"Rep Q{self.question_id} quiz{self.quiz_id}"
 
 
# ──────────────────────────────────────────────────────────────
# PAIEMENT
# ──────────────────────────────────────────────────────────────
class Payment(models.Model):
    STATUS = [
        ('pending',   'En attente'),
        ('completed', 'Complété'),
        ('failed',    'Échoué'),
    ]
    etudiant      = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='payments')
    level         = models.IntegerField()
    amount        = models.IntegerField()
    status        = models.CharField(max_length=20, choices=STATUS, default='pending')
    reference     = models.CharField(max_length=100, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_completion = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        ordering = ['-date_creation']
 
    def __str__(self):
        return f"{self.reference} – {self.etudiant} – lvl{self.level} – {self.status}"
 
 
# ──────────────────────────────────────────────────────────────
# CHATBOT (conservé, minimal)
# ──────────────────────────────────────────────────────────────
class Conversation(models.Model):
    etudiant         = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='conversations')
    titre            = models.CharField(max_length=200, default='Nouvelle conversation')
    date_creation    = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['-date_modification']
 
    def __str__(self):
        return f"{self.etudiant} – {self.titre}"
 
 
class Message(models.Model):
    ROLES = [('user', 'Étudiant'), ('assistant', 'Chatbot')]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role         = models.CharField(max_length=20, choices=ROLES)
    contenu      = models.TextField()
    timestamp    = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['timestamp']
