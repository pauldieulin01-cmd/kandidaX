from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect, render
from django.contrib import messages as django_messages
import csv
from io import TextIOWrapper
 
from .models import Matiere, Question, Etudiant, Quiz, Reponse, Payment, Conversation, Message
 
 
# ─────────────────────────────────────────
# MATIÈRE

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nb_questions')
    search_fields = ('nom',)
 
    def nb_questions(self, obj):
        return obj.question_set.count()
    nb_questions.short_description = 'Questions'
 
 
# ─────────────────────────────────────────
# QUESTION  (avec import CSV)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/quizapp/question/change_list.html'
    list_display  = ('texte_court', 'matiere', 'type_question', 'niveau_requis', 'difficulte')
    list_filter   = ('matiere', 'type_question', 'niveau_requis', 'difficulte')
    search_fields = ('texte',)
    ordering      = ('niveau_requis', 'matiere', 'type_question')
 
    fieldsets = (
        ('Général', {'fields': ('matiere', 'type_question', 'texte', 'niveau_requis', 'difficulte')}),
        ('QCM',     {'classes': ('collapse',), 'fields': ('choix_a','choix_b','choix_c','choix_d','reponse_correcte')}),
        ('Vrai/Faux',  {'classes': ('collapse',), 'fields': ('reponse_vf',)}),
        ('Ouverte',    {'classes': ('collapse',), 'fields': ('reponse_ouverte',)}),
    )
 
    def texte_court(self, obj):
        return obj.texte[:80] + ('…' if len(obj.texte) > 80 else '')
    texte_court.short_description = 'Question'
 
    def get_urls(self):
        urls = super().get_urls()
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv_view),
                     name='question_import_csv')] + urls
 
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_csv_url'] = request.path + 'import-csv/'
        return super().changelist_view(request, extra_context=extra_context)
 
    def import_csv_view(self, request):
        if request.method == 'POST' and 'csv_file' in request.FILES:
            try:
                decoded = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader  = csv.DictReader(decoded)
                created = 0
                errors  = []
                for i, row in enumerate(reader, 2):
                    try:
                        mat, _ = Matiere.objects.get_or_create(nom=row['matiere'].strip())
                        q = Question.objects.create(
                            matiere=mat,
                            texte=row['texte'].strip(),
                            type_question=row.get('type_question','QCM').strip().upper(),
                            difficulte=int(row.get('difficulte', 1)),
                            niveau_requis=int(row.get('niveau_requis', 1)),
                            choix_a=row.get('choix_a','').strip(),
                            choix_b=row.get('choix_b','').strip(),
                            choix_c=row.get('choix_c','').strip(),
                            choix_d=row.get('choix_d','').strip(),
                            reponse_correcte=row.get('reponse_correcte','').strip(),
                            reponse_vf=(row.get('reponse_vf','').lower() in ('true','1')),
                            reponse_ouverte=row.get('reponse_ouverte','').strip(),
                        )
                        created += 1
                    except Exception as e:
                        errors.append(f'Ligne {i}: {e}')
                django_messages.success(request, f'✓ {created} question(s) importée(s).')
                if errors:
                    django_messages.warning(request, ' | '.join(errors[:5]))
                return redirect(reverse('admin:Quizapp_question_changelist'))
            except Exception as e:
                django_messages.error(request, f'Erreur CSV : {e}')
 
        return render(request, 'admin/question_import_csv.html', {
            'title': 'Importer des questions (CSV)',
            'opts':  Question._meta,
        })
 
 
# ─────────────────────────────────────────
# ÉTUDIANT

class EtudiantInline(admin.StackedInline):
    model = Etudiant
    can_delete = False
    fields = ('nom_complet', 'serie', 'option', 'entite', 'score_total', 'niveau_actuel')
 
 
class CustomUserAdmin(UserAdmin):
    inlines = (EtudiantInline,)
    list_display = ('username', 'email', 'get_nom', 'get_score', 'is_staff')
 
    def get_nom(self, obj):
        try: return obj.etudiant.nom_complet
        except: return '—'
    get_nom.short_description = 'Nom'
 
    def get_score(self, obj):
        try:
            s = obj.etudiant.score_total
            c = '#22c55e' if s >= 50 else '#f59e0b' if s >= 20 else '#ef4444'
            return format_html('<span style="color:{};font-weight:700;">{} pts</span>', c, s)
        except: return '—'
    get_score.short_description = 'Score'
 
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
 
 
@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display  = ('nom_complet', 'serie', 'option', 'score_total', 'niveau_actuel', 'date_inscription')
    list_filter   = ('serie', 'option')
    search_fields = ('nom_complet', 'user__username')
    ordering      = ('-score_total',)
    readonly_fields = ('date_inscription',)
    actions = ['reset_scores']
 
    @admin.action(description='🔄 Remettre les scores à zéro')
    def reset_scores(self, request, queryset):
        queryset.update(score_total=0, niveau_actuel=1)
        self.message_user(request, 'Scores remis à zéro.')
 
 
# ─────────────────────────────────────────
# QUIZ & RÉPONSE

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display  = ('id', 'etudiant', 'level', 'score', 'total_questions', 'termine', 'date_creation')
    list_filter   = ('level', 'termine', 'date_creation')
    search_fields = ('etudiant__nom_complet',)
    ordering      = ('-date_creation',)
    readonly_fields = ('date_creation',)
 
 
# ─────────────────────────────────────────
# PAIEMENT  ← point clé de l'admin

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('reference', 'etudiant_nom', 'level', 'amount', 'status_badge', 'date_creation')
    list_filter   = ('status', 'level', 'date_creation')
    search_fields = ('reference', 'etudiant__nom_complet')
    ordering      = ('-date_creation',)
    readonly_fields = ('reference', 'date_creation')
 
    fieldsets = (
        ('Paiement', {'fields': ('reference', 'etudiant', 'level', 'amount', 'status')}),
        ('Dates',    {'classes': ('collapse',), 'fields': ('date_creation', 'date_completion')}),
    )
 
    def etudiant_nom(self, obj):
        return obj.etudiant.nom_complet
    etudiant_nom.short_description = 'Étudiant'
 
    def status_badge(self, obj):
        colors = {'pending': '#f59e0b', 'completed': '#22c55e', 'failed': '#ef4444'}
        c = colors.get(obj.status, '#94a3b8')
        return format_html('<span style="color:{};font-weight:700;">{}</span>', c, obj.get_status_display())
    status_badge.short_description = 'Statut'
 
    # Action rapide : valider un paiement
    @admin.action(description='✅ Valider les paiements sélectionnés')
    def valider_paiements(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for p in queryset.filter(status='pending'):
            p.status = 'completed'
            p.date_completion = timezone.now()
            p.save()
            # Mettre à jour le niveau de l'étudiant
            etudiant = p.etudiant
            if p.level > etudiant.niveau_actuel:
                etudiant.niveau_actuel = p.level
                etudiant.save()
            updated += 1
        self.message_user(request, f'{updated} paiement(s) validé(s).')
    actions = ['valider_paiements']
 
 
# ─────────────────────────────────────────
# CHATBOT

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etudiant', 'date_modification')
    search_fields = ('titre', 'etudiant__nom_complet')
 
 
# ─────────────────────────────────────────
# BRANDING ADMIN

admin.site.site_header  = '🎓 Plateforme Concours — Admin'
admin.site.site_title   = 'Admin Concours'
admin.site.index_title  = 'Tableau de bord administrateur'
 
