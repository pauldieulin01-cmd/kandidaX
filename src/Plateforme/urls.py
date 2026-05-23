from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Quizapp import views
 
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
 
    # Publiques
    path('',                  views.accueil,                 name='accueil'),
    path('inscription/',      views.inscription,             name='inscription'),
    path('connexion/',        views.connexion,               name='connexion'),
    path('deconnexion/',      views.deconnexion,             name='deconnexion'),
    path('conditions/',       views.conditions_generales,    name='conditions_generales'),
    path('confidentialite/',  views.politique_confidentialite, name='confidentialite'),
 
    # Authentifié
    path('dashboard/',        views.dashboard,               name='dashboard'),
    path('question/',         views.page_question,           name='page_question'),
    path('quiz/<int:quiz_id>/finaliser/', views.finaliser_quiz, name='finaliser_quiz'),
    path('quiz/<int:quiz_id>/quitter/', views.quitter_quiz, name='quitter_quiz'),
 
    # Paiement
    path('paiement/niveau/<int:level>/', views.paiement_niveau, name='paiement_niveau'),
 
    # API Quiz
    path('api/reponse/',      views.soumettre_reponse,       name='soumettre_reponse'),
 
    # Chatbot dissertations
    path('dissertations/',    views.dissertations,           name='dissertations'),
    path('api/chatbot/message/',          views.message_chatbot,        name='message_chatbot'),
    path('api/chatbot/nouvelle/',         views.nouvelle_conversation,  name='nouvelle_conversation'),
    path('api/chatbot/renommer/',         views.renommer_conversation,  name='renommer_conversation'),
    path('api/chatbot/supprimer/',        views.supprimer_conversation, name='supprimer_conversation'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
