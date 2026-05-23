
import json
import random
import time
import uuid
from datetime import datetime
from urllib.parse import quote
 
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import OperationalError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
 
from .forms import ConnexionForm, CustomUserCreationForm
from .models import Etudiant, Matiere, Payment, Question, Quiz, Reponse
 
 
# ──────────────────────────────────────────────────────────────
# PAGES PUBLIQUES

 
def accueil(request):
    return render(request, 'quiz_app/plateforme.html')
 
 
def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Etudiant.objects.create(
                user=user,
                nom_complet=form.cleaned_data['nom_complet'],
                serie=form.cleaned_data['serie'],
                option=form.cleaned_data['option'],
                entite=form.cleaned_data['entite'],
            )
            messages.success(request, 'Compte créé ! Connectez-vous.')
            return redirect('connexion')
        messages.error(request, 'Vérifiez vos informations.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'quiz_app/inscription.html', {'form': form})
 
 
@never_cache
def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('dashboard')
            messages.error(request, 'Identifiants incorrects.')
    else:
        form = ConnexionForm()
    return render(request, 'quiz_app/connexion.html', {'form': form})
 
 
def deconnexion(request):
    logout(request)
    return redirect('accueil')
 
 
def conditions_generales(request):
    return render(request, 'quiz_app/conditions.html')
 
 
def politique_confidentialite(request):
    return render(request, 'quiz_app/confidentialite.html')
 
 
# ──────────────────────────────────────────────────────────────
# DASHBOARD

 
@login_required
def dashboard(request):
    etudiant = _get_or_create_etudiant(request.user)
    matieres = Matiere.objects.all()
    classement = list(Etudiant.objects.order_by('-score_total')).index(etudiant) + 1
 
    return render(request, 'quiz_app/dashboard.html', {
        'etudiant':     etudiant,
        'matieres':     matieres,
        'classement':   classement,
        'total':        Etudiant.objects.count(),
        'level_info':   etudiant.level_info(),
        'points_to_next': etudiant.points_to_next(),
        'niveaux_info': _all_levels_info(etudiant),
    })
 
 
# ──────────────────────────────────────────────────────────────
# PAGE QUIZ (unique, dynamique)
# ──────────────────────────────────────────────────────────────
 
@login_required
def page_question(request):
    etudiant = _get_or_create_etudiant(request.user)
    level    = etudiant.get_current_level()
 
    # Vérifier paiement pour niveaux ≥ 3
    if level >= 3 and not etudiant.is_paid_level(level):
        return redirect('paiement_niveau', level=level)
 
    matiere_nom = request.GET.get('matiere')
    matiere = Matiere.objects.filter(nom=matiere_nom).first() if matiere_nom else None
 
    # Exclure les questions déjà répondues par cet étudiant
    answered_question_ids = Reponse.objects.filter(
        quiz__etudiant=etudiant
    ).values_list('question_id', flat=True).distinct()
    
    qs = Question.objects.filter(niveau_requis=level).exclude(id__in=answered_question_ids)
    if matiere:
        qs = qs.filter(matiere=matiere)
    if qs.count() < 5:
        qs = Question.objects.filter(niveau_requis__lte=level).exclude(id__in=answered_question_ids)
        if matiere:
            qs = qs.filter(matiere=matiere)

    questions = random.sample(list(qs), min(len(qs), 10))

    # SQLite peut être verrouillé brièvement si une autre requête écrit en même temps.
    # On retente pour éviter une erreur 500 sur /question/.
    quiz = None
    for attempt in range(3):
        try:
            with transaction.atomic():
                quiz = Quiz.objects.create(etudiant=etudiant, level=level, matiere=matiere)
                quiz.questions.set(questions)
                quiz.total_questions = len(questions)
                quiz.save(update_fields=['total_questions'])
            break
        except OperationalError:
            if attempt == 2:
                messages.error(request, "Le quiz est momentanement indisponible. Reessayez dans quelques secondes.")
                return redirect('dashboard')
            time.sleep(0.2 * (attempt + 1))

    return render(request, 'quiz_app/page_question.html', {
        'quiz':      quiz,
        'questions': questions,
        'level':     level,
        'level_nom': Etudiant.NOMS_NIVEAUX.get(level, ''),
        'matiere':   matiere,
    })
 
 
# ──────────────────────────────────────────────────────────────
# API : soumettre une réponse

 
@login_required
@require_http_methods(['POST'])
def soumettre_reponse(request):
    try:
        data       = json.loads(request.body)
        quiz_id    = data.get('quiz_id')
        question_id = data.get('question_id')
        valeur     = data.get('reponse', '')
 
        quiz     = Quiz.objects.get(id=quiz_id, etudiant=request.user.etudiant)
        if quiz.termine:
            return JsonResponse({'error': 'Ce quiz est déjà terminé.'}, status=400)
        question = Question.objects.get(id=question_id)
 
        correct = question.is_correct(valeur)
        Reponse.objects.create(quiz=quiz, question=question, valeur=valeur, est_correcte=correct)
 
        result = {'correct': correct}
        
        # Si incorrect, envoyer la bonne réponse
        if not correct:
            if question.type_question == 'QCM':
                result['bonne_reponse'] = question.reponse_correcte
            elif question.type_question == 'VF':
                result['bonne_reponse'] = 'true' if question.reponse_vf else 'false'
            elif question.type_question == 'OUV':
                result['bonne_reponse'] = question.reponse_ouverte
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ──────────────────────────────────────────────────────────────
# API : finaliser le quiz

def _clore_quiz_et_crediter(quiz, etudiant):
    """Clôture un quiz de façon idempotente et crédite les points une seule fois."""
    if quiz.termine:
        return quiz.score, quiz.score * 2, False

    bonnes = quiz.reponses.filter(est_correcte=True).count()
    pts_gagnes = bonnes * 2  # 2 points par bonne réponse

    quiz.score = bonnes
    quiz.termine = True
    quiz.date_fin = datetime.now()
    quiz.save()

    etudiant.score_total += pts_gagnes

    # Montée de niveau automatique — UNIQUEMENT pour les niveaux gratuits (1-2)
    nouveau_niveau = etudiant.niveau_score()
    if nouveau_niveau > etudiant.niveau_actuel and nouveau_niveau <= 2:
        etudiant.niveau_actuel = nouveau_niveau

    etudiant.save()
    return bonnes, pts_gagnes, True

@login_required
def finaliser_quiz(request, quiz_id):
    try:
        etudiant = request.user.etudiant
        quiz = Quiz.objects.get(id=quiz_id, etudiant=etudiant)
        bonnes, pts_gagnes, freshly_closed = _clore_quiz_et_crediter(quiz, etudiant)

        if freshly_closed:
            messages.success(
                request,
                f'Quiz terminé ! {bonnes}/{quiz.total_questions} correctes → +{pts_gagnes} points'
            )
        else:
            messages.info(request, 'Ce quiz était déjà enregistré.')
        return redirect('dashboard')

    except Quiz.DoesNotExist:
        messages.error(request, 'Quiz introuvable.')
        return redirect('dashboard')


@login_required
@require_http_methods(['POST'])
def quitter_quiz(request, quiz_id):
    """Sauvegarde les points déjà gagnés si l'étudiant quitte avant la fin."""
    try:
        etudiant = request.user.etudiant
        quiz = Quiz.objects.get(id=quiz_id, etudiant=etudiant)
        bonnes, pts_gagnes, freshly_closed = _clore_quiz_et_crediter(quiz, etudiant)
        return JsonResponse({
            'success': True,
            'already_saved': not freshly_closed,
            'bonnes': bonnes,
            'points': pts_gagnes,
        })
    except Quiz.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Quiz introuvable.'}, status=404)


# ──────────────────────────────────────────────────────────────
# PAIEMENT (WhatsApp simple)

@login_required
def paiement_niveau(request, level):
    etudiant = _get_or_create_etudiant(request.user)

    # N'autoriser la demande de paiement que si le seuil est atteint
    seuil_requis = Etudiant.SEUILS.get(level, 0)
    if etudiant.score_total < seuil_requis:
        messages.warning(
            request,
            f"Vous devez atteindre {seuil_requis} points pour demander l'accès au niveau {level}."
        )
        return redirect('dashboard')

    # Déjà payé ?
    if etudiant.is_paid_level(level):
        messages.info(request, 'Accès déjà débloqué.')
        return redirect('page_question')

    prix = etudiant.get_level_price(level)
    if prix == 0:
        messages.info(request, 'Ce niveau est gratuit.')
        return redirect('page_question')

    admin_moncash  = getattr(settings, 'ADMIN_MONCASH_NUMBER', '50947023167')
    admin_whatsapp = getattr(settings, 'ADMIN_WHATSAPP_NUMBER', admin_moncash)
    # Nettoyer le numéro
    wa_number = ''.join(c for c in str(admin_whatsapp) if c.isdigit())
    if wa_number.startswith('00'):
        wa_number = wa_number[2:]
 
    if request.method == 'POST':
        # Créer/réutiliser un Payment en attente
        payment = Payment.objects.filter(
            etudiant=etudiant, level=level, status='pending'
        ).first()
 
        if not payment:
            ref = f"PAY-{uuid.uuid4().hex[:10].upper()}"
            payment = Payment.objects.create(
                etudiant=etudiant,
                level=level,
                amount=prix,
                reference=ref,
            )
 
        msg = (
            f"Bonjour, j'ai fait le paiement MonCash pour le Niveau {level} "
            f"({prix}G).\n"
            f"Nom : {etudiant.nom_complet}\n"
            f"Utilisateur : {request.user.username}\n"
            f"Référence : {payment.reference}\n"
            f"Merci de valider mon accès."
        )
        whatsapp_url = f"https://wa.me/{wa_number}?text={quote(msg)}"
 
        return render(request, 'quiz_app/paiement_attente.html', {
            'payment':            payment,
            'level':              level,
            'level_nom':          Etudiant.NOMS_NIVEAUX.get(level, ''),
            'prix':               prix,
            'admin_moncash':      admin_moncash,
            'whatsapp_url':       whatsapp_url,
        })
 
    return render(request, 'quiz_app/paiement_niveau.html', {
        'level':          level,
        'level_nom':      Etudiant.NOMS_NIVEAUX.get(level, ''),
        'prix':           prix,
        'admin_moncash':  admin_moncash,
    })
 
 
# ──────────────────────────────────────────────────────────────
# CHATBOT (conservé, minimal)

 
@login_required
def dissertations(request):
    try:
        etudiant      = request.user.etudiant
        conversations = etudiant.conversations.all()
        conv_id       = request.GET.get('conv_id')
        conversation  = None
 
        if conv_id:
            conversation = conversations.filter(id=conv_id).first()
        if not conversation:
            conversation = conversations.first()
        if not conversation:
            from .models import Conversation
            conversation = Conversation.objects.create(
                etudiant=etudiant, titre='Nouvelle conversation'
            )
 
        return render(request, 'quiz_app/dissertations.html', {
            'conversations': conversations,
            'conversation':  conversation,
        })
    except Exception:
        return redirect('dashboard')
 
 
@login_required
@require_http_methods(['POST'])
def message_chatbot(request):
    try:
        from .models import Conversation, Message
        from .chatbot import chatbot
 
        if not chatbot:
            return JsonResponse({'error': 'Chatbot non configuré.'}, status=500)
 
        data            = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        message_text    = data.get('message')
        action          = data.get('action', 'discuss')
 
        etudiant     = request.user.etudiant
        conversation = Conversation.objects.get(id=conversation_id, etudiant=etudiant)
 
        user_msg = Message.objects.create(
            conversation=conversation, role='user', contenu=message_text
        )
 
        if conversation.messages.count() == 1:
            conversation.titre = message_text[:50]
            conversation.save()
 
        if action == 'analyze':
            response_text = chatbot.analyser_dissertation(message_text)
        elif action == 'plan':
            response_text = chatbot.generer_plan(message_text)
        elif action == 'correct':
            response_text = chatbot.corriger_texte(message_text)
        elif action == 'conseil':
            response_text = chatbot.conseil_redactionnel(message_text)
        else:
            prev_qs = conversation.messages.filter(id__lt=user_msg.id).values('role', 'contenu').order_by('-id')[:10]
            prev = list(reversed(list(prev_qs)))
            response_text = chatbot.discuter(message_text, prev)
 
        assistant_msg = Message.objects.create(
            conversation=conversation, role='assistant', contenu=response_text
        )
        return JsonResponse({'success': True, 'response': response_text, 'message_id': assistant_msg.id})
 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
 
@login_required
def nouvelle_conversation(request):
    try:
        from .models import Conversation
        conv = Conversation.objects.create(
            etudiant=request.user.etudiant, titre='Nouvelle conversation'
        )
        return redirect(f'/dissertations/?conv_id={conv.id}')
    except Exception:
        return redirect('dissertations')
 
 
@login_required
def renommer_conversation(request):
    if request.method == 'POST':
        try:
            from .models import Conversation
            data = json.loads(request.body)
            conv = Conversation.objects.get(
                id=data['conversation_id'], etudiant=request.user.etudiant
            )
            conv.titre = data['titre']
            conv.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
 
 
@login_required
def supprimer_conversation(request):
    if request.method == 'POST':
        try:
            from .models import Conversation
            data = json.loads(request.body)
            conv = Conversation.objects.get(
                id=data['conversation_id'], etudiant=request.user.etudiant
            )
            conv.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
 
 
# ──────────────────────────────────────────────────────────────
# HELPERS PRIVÉS

 
def _get_or_create_etudiant(user):
    etudiant, _ = Etudiant.objects.get_or_create(
        user=user,
        defaults={
            'nom_complet': user.get_full_name() or user.username,
            'serie': 'MP',
        },
    )
    return etudiant
 
 
def _all_levels_info(etudiant):
    """Retourne une liste de dicts pour l'affichage de tous les niveaux."""
    current = etudiant.get_current_level()
    infos = []
    for n in range(1, 10):
        seuil = Etudiant.SEUILS.get(n, 0)
        prix  = Etudiant.PRIX_NIVEAUX.get(n, 0)
        statut = 'actuel' if n == current else ('debloque' if n < current else 'verrouille')
        payant_ok = etudiant.is_paid_level(n) if prix > 0 else True
        seuil_atteint = etudiant.score_total >= seuil
        can_request_access = prix > 0 and seuil_atteint and not payant_ok
        infos.append({
            'numero':    n,
            'nom':       Etudiant.NOMS_NIVEAUX.get(n, ''),
            'seuil':     seuil,
            'prix':      prix,
            'statut':    statut,
            'payant_ok': payant_ok,
            'seuil_atteint': seuil_atteint,
            'can_request_access': can_request_access,
        })
    return infos
