# Quizapp/chatbot.py
"""
Utilitaire pour interagir avec Google Gemini API
Analyse de dissertations et aide rédactionnelle
"""

import google.generativeai as genai
import os
from django.conf import settings


class DissertationChatbot:
    """Chatbot pour analyser les dissertations et aider les étudiants"""
    
    def __init__(self):
        """Initialiser le chatbot avec la clé API Google"""
        api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY not configured in settings")
        
        genai.configure(api_key=api_key)
        # Utiliser le meilleur modèle gratuit disponible: Gemini 2.5 Flash
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Système de prompt pour le contexte du chatbot
        self.system_prompt = """Tu es un expert en dissertations et textes argumentatifs haïtiens/français. 
Tu aides les étudiants à écrire de meilleures dissertations, à améliorer leur argumentation et à corriger leurs textes.

Tes compétences:
1. Analyser les dissertations et donner du feedback constructif
2. Identifier les forces et les faiblesses de l'argumentation
3. Suggérer des améliorations structurelles et stylistiques
4. Générer des plans de dissertation
5. Corriger la grammaire et l'orthographe
6. Expliquer les concepts philosophiques et argumentatifs
7. Aider à trouver des exemples et des citations pertinents

Format tes réponses de manière claire et pédagogique.
Utilise des listes à puces quand approprié.
Sois encourageant mais honnête dans ton feedback."""
    
    def analyser_dissertation(self, texte):
        """
        Analyser une dissertation et retourner un feedback détaillé
        
        Args:
            texte (str): Le texte de la dissertation à analyser
            
        Returns:
            str: Feedback et suggestions d'amélioration
        """
        prompt = f"""Analyse cette dissertation et fournis un feedback détaillé:

DISSERTATION:
{texte}

Fournir un retour complet incluant:
1. Structure générale (introduction, développement, conclusion)
2. Qualité de la thèse et de l'argumentation
3. Utilisation des preuves et exemples
4. Clarté et cohérence
5. Suggestions spécifiques d'amélioration
6. Points forts à conserver
7. Erreurs grammaticales ou orthographiques identifiées

Sois constructif et motivant dans ton feedback."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de l'analyse: {str(e)}"
    
    def generer_plan(self, sujet, type_dissertation="balancé"):
        """
        Générer un plan de dissertation basé sur le sujet
        
        Args:
            sujet (str): Le sujet de la dissertation
            type_dissertation (str): "pour-contre", "balancé", "critique"
            
        Returns:
            str: Un plan détaillé
        """
        type_map = {
            "pour-contre": "présente les arguments pour ET contre",
            "balancé": "développe une position nuancée avec analyse",
            "critique": "critique une proposition ou une idée"
        }
        
        prompt = f"""Crée un plan de dissertation pour le sujet suivant:

SUJET: {sujet}
TYPE: Ce type de dissertation {type_map.get(type_dissertation, type_map['balancé'])}

Fournis:
1. Une reformulation du sujet
2. L'enjeu principal
3. Une thèse proposée
4. Un plan détaillé avec 3 parties:
   - Partie I: [Titre] - [3 sous-points]
   - Partie II: [Titre] - [3 sous-points]
   - Partie III: [Titre] - [3 sous-points]
5. Conclusion suggérée (en 1-2 phrases)
6. Références ou exemples possibles

Format le résultat de manière claire et utilisable."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de la génération du plan: {str(e)}"
    
    def corriger_texte(self, texte):
        """
        Corriger un texte (grammaire, orthographe, style)
        
        Args:
            texte (str): Le texte à corriger
            
        Returns:
            dict: Corrections suggérées et texte corrigé
        """
        prompt = f"""Corrige ce texte en français:

TEXTE ORIGINAL:
{texte}

Fournir:
1. Le texte CORRIGÉ (version améliorée)
2. Une liste des ERREURS IDENTIFIÉES:
   - Erreur de grammaire
   - Erreur d'orthographe
   - Problème de style ou de formulation
   - Suggestions pour améliorer la clarté
3. AMÉLIORATIONS STYLISTIQUES:
   - Formulations plus élégantes
   - Transitions meilleures
   - Variété du vocabulaire

Sois précis et explique chaque correction."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de la correction: {str(e)}"
    
    def conseil_redactionnel(self, question):
        """
        Donner des conseils rédactionnels basés sur une question
        
        Args:
            question (str): La question ou le sujet
            
        Returns:
            str: Conseils pratiques
        """
        prompt = f"""L'étudiant a une question sur la rédaction:

QUESTION: {question}

Fournis des conseils pratiques, des stratégies et des exemples concrets pour aider l'étudiant.
Sois clair et direct. Utilise des listes à puces si approprié."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de la génération des conseils: {str(e)}"
    
    def discuter(self, message, contexte_conversation=None):
        """
        Discuter avec le chatbot sur les dissertations
        
        Args:
            message (str): Le message de l'utilisateur
            contexte_conversation (list): Contexte des messages précédents
            
        Returns:
            str: Réponse du chatbot
        """
        try:
            # Construire l'historique de la conversation
            if contexte_conversation:
                full_prompt = self.system_prompt + "\n\nHistorique de la conversation:\n"
                for msg in contexte_conversation:
                    full_prompt += f"{msg['role'].upper()}: {msg['contenu']}\n"
                full_prompt += f"ÉTUDIANT: {message}\nCHATBOT:"
            else:
                full_prompt = f"{self.system_prompt}\n\nÉTUDIANT: {message}\nCHATBOT:"
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de la discussion: {str(e)}"


# Instancier le chatbot
try:
    chatbot = DissertationChatbot()
except ValueError as e:
    # Si la clé n'est pas configurée, créer un chatbot dummy
    chatbot = None
