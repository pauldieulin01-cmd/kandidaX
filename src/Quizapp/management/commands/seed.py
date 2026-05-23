

from django.core.management.base import BaseCommand
from Quizapp.models import Matiere, Question


DATA = {
    "Mathématiques": {
        "QCM": [
            {
                "texte": "Quelle est la valeur de π (pi) arrondie à 2 décimales ?",
                "choix_a": "3.12", "choix_b": "3.14", "choix_c": "3.16", "choix_d": "3.18",
                "reponse_correcte": "B",
            },
            {
                "texte": "Combien vaut 2⁸ ?",
                "choix_a": "128", "choix_b": "256", "choix_c": "512", "choix_d": "64",
                "reponse_correcte": "B",
            },
            {
                "texte": "Quel est le résultat de (3 + 5) × 2 − 4 ?",
                "choix_a": "8", "choix_b": "12", "choix_c": "16", "choix_d": "20",
                "reponse_correcte": "B",
            },
            {
                "texte": "La somme des angles d'un triangle est :",
                "choix_a": "90°", "choix_b": "180°", "choix_c": "270°", "choix_d": "360°",
                "reponse_correcte": "B",
            },
            {
                "texte": "Quelle est la racine carrée de 144 ?",
                "choix_a": "10", "choix_b": "11", "choix_c": "12", "choix_d": "13",
                "reponse_correcte": "C",
            },
        ],
        "VF": [
            {"texte": "Le nombre 0 est un entier naturel.", "reponse_vf": True},
            {"texte": "Un carré est un cas particulier de rectangle.", "reponse_vf": True},
            {"texte": "√2 est un nombre rationnel.", "reponse_vf": False},
            {"texte": "Tout nombre pair est divisible par 4.", "reponse_vf": False},
        ],
        "OUV": [
            {"texte": "Combien font 15 % de 200 ?", "reponse_ouverte": "30"},
            {"texte": "Quel est le PGCD de 12 et 18 ?", "reponse_ouverte": "6"},
        ],
    },
    "Physique": {
        "QCM": [
            {
                "texte": "Quelle est la vitesse de la lumière dans le vide ?",
                "choix_a": "300 000 km/s", "choix_b": "150 000 km/s",
                "choix_c": "3 000 km/s", "choix_d": "30 000 km/s",
                "reponse_correcte": "A",
            },
            {
                "texte": "L'unité de la force dans le SI est :",
                "choix_a": "Joule", "choix_b": "Watt", "choix_c": "Newton", "choix_d": "Pascal",
                "reponse_correcte": "C",
            },
            {
                "texte": "La formule de l'énergie cinétique est :",
                "choix_a": "E = mc²", "choix_b": "Ec = ½mv²", "choix_c": "P = mv", "choix_d": "W = Fd",
                "reponse_correcte": "B",
            },
            {
                "texte": "Quelle loi relie tension, intensité et résistance ?",
                "choix_a": "Loi de Faraday", "choix_b": "Loi d'Ohm",
                "choix_c": "Loi de Joule", "choix_d": "Loi de Coulomb",
                "reponse_correcte": "B",
            },
        ],
        "VF": [
            {"texte": "Le son se propage plus vite dans l'air que dans l'eau.", "reponse_vf": False},
            {"texte": "La masse et le poids sont deux grandeurs identiques.", "reponse_vf": False},
            {"texte": "L'intensité électrique s'exprime en Ampères.", "reponse_vf": True},
        ],
        "OUV": [
            {"texte": "Quelle est la formule de la vitesse (v) en fonction de la distance (d) et du temps (t) ?",
             "reponse_ouverte": "v = d/t"},
        ],
    },
    "Chimie": {
        "QCM": [
            {
                "texte": "Quelle est la formule chimique de l'eau ?",
                "choix_a": "CO2", "choix_b": "H2O", "choix_c": "NaCl", "choix_d": "O2",
                "reponse_correcte": "B",
            },
            {
                "texte": "Le tableau périodique est classé par ordre croissant de :",
                "choix_a": "Masse atomique", "choix_b": "Numéro atomique",
                "choix_c": "Électronégativité", "choix_d": "Valence",
                "reponse_correcte": "B",
            },
            {
                "texte": "Quel gaz est produit lors de la photosynthèse ?",
                "choix_a": "CO2", "choix_b": "N2", "choix_c": "O2", "choix_d": "H2",
                "reponse_correcte": "C",
            },
            {
                "texte": "Le pH d'une solution neutre est :",
                "choix_a": "0", "choix_b": "7", "choix_c": "14", "choix_d": "3",
                "reponse_correcte": "B",
            },
        ],
        "VF": [
            {"texte": "Le sel de cuisine est du chlorure de sodium (NaCl).", "reponse_vf": True},
            {"texte": "L'oxygène est un métal.", "reponse_vf": False},
            {"texte": "Une solution acide a un pH inférieur à 7.", "reponse_vf": True},
        ],
        "OUV": [
            {"texte": "Quel est le symbole chimique du fer ?", "reponse_ouverte": "Fe"},
            {"texte": "Quel est le numéro atomique de l'hydrogène ?", "reponse_ouverte": "1"},
        ],
    },
    "SVT": {
        "QCM": [
            {
                "texte": "Quelle molécule porte l'information génétique ?",
                "choix_a": "ARN", "choix_b": "ATP", "choix_c": "ADN", "choix_d": "AMP",
                "reponse_correcte": "C",
            },
            {
                "texte": "Combien de chromosomes possède une cellule humaine normale ?",
                "choix_a": "23", "choix_b": "46", "choix_c": "48", "choix_d": "44",
                "reponse_correcte": "B",
            },
            {
                "texte": "Quel organite est le centre énergétique de la cellule ?",
                "choix_a": "Noyau", "choix_b": "Ribosome", "choix_c": "Mitochondrie", "choix_d": "Golgi",
                "reponse_correcte": "C",
            },
            {
                "texte": "La photosynthèse se déroule dans :",
                "choix_a": "Les mitochondries", "choix_b": "Les chloroplastes",
                "choix_c": "Le noyau", "choix_d": "Le réticulum",
                "reponse_correcte": "B",
            },
        ],
        "VF": [
            {"texte": "Les virus sont des êtres vivants autonomes.", "reponse_vf": False},
            {"texte": "Les globules rouges transportent l'oxygène.", "reponse_vf": True},
            {"texte": "L'ADN est présent uniquement dans le noyau cellulaire.", "reponse_vf": False},
        ],
        "OUV": [
            {"texte": "Comment s'appelle la division cellulaire produisant deux cellules identiques ?",
             "reponse_ouverte": "mitose"},
        ],
    },
    "Français": {
        "QCM": [
            {
                "texte": "Quel est le pluriel de 'bail' ?",
                "choix_a": "bails", "choix_b": "bailes", "choix_c": "baux", "choix_d": "bailx",
                "reponse_correcte": "C",
            },
            {
                "texte": "Quelle figure de style est dans : 'Il est fort comme un lion' ?",
                "choix_a": "Métaphore", "choix_b": "Comparaison",
                "choix_c": "Hyperbole", "choix_d": "Métonymie",
                "reponse_correcte": "B",
            },
            {
                "texte": "Lequel de ces mots est un adverbe ?",
                "choix_a": "Rapide", "choix_b": "Rapidement",
                "choix_c": "Rapidité", "choix_d": "Rapider",
                "reponse_correcte": "B",
            },
        ],
        "VF": [
            {"texte": "Un verbe du 2ème groupe fait -issons à la 1ère personne du pluriel.", "reponse_vf": True},
            {"texte": "L'imparfait exprime une action ponctuelle dans le passé.", "reponse_vf": False},
        ],
        "OUV": [
            {"texte": "Quel est l'auteur des Misérables ?", "reponse_ouverte": "Victor Hugo"},
        ],
    },
    "Culture générale": {
        "QCM": [
            {
                "texte": "Quelle est la capitale d'Haïti ?",
                "choix_a": "Cap-Haïtien", "choix_b": "Jacmel",
                "choix_c": "Port-au-Prince", "choix_d": "Les Cayes",
                "reponse_correcte": "C",
            },
            {
                "texte": "En quelle année Haïti a-t-il proclamé son indépendance ?",
                "choix_a": "1791", "choix_b": "1804", "choix_c": "1820", "choix_d": "1915",
                "reponse_correcte": "B",
            },
            {
                "texte": "Qui a peint la Joconde ?",
                "choix_a": "Michel-Ange", "choix_b": "Raphaël",
                "choix_c": "Léonard de Vinci", "choix_d": "Botticelli",
                "reponse_correcte": "C",
            },
        ],
        "VF": [
            {"texte": "Jean-Jacques Dessalines fut le premier chef d'État d'Haïti.", "reponse_vf": True},
            {"texte": "Le mont Everest est situé en Afrique.", "reponse_vf": False},
        ],
        "OUV": [
            {"texte": "Quel est le plus grand pays du monde par sa superficie ?",
             "reponse_ouverte": "Russie"},
        ],
    },
}


class Command(BaseCommand):
    help = "Peuple la base de données avec des matières et questions d'exemple."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les questions et matières avant insertion.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Question.objects.all().delete()
            Matiere.objects.all().delete()
            self.stdout.write(self.style.WARNING("⚠️  Base vidée."))

        created_m = 0
        created_q = 0

        for matiere_nom, types in DATA.items():
            matiere, m_new = Matiere.objects.get_or_create(nom=matiere_nom)
            if m_new:
                created_m += 1
                self.stdout.write(f"  ✅ Matière : {matiere_nom}")

            for type_q, questions in types.items():
                for q_data in questions:
                    if Question.objects.filter(matiere=matiere, texte=q_data["texte"]).exists():
                        continue

                    q = Question(matiere=matiere, type_question=type_q, texte=q_data["texte"])

                    # Assigner les niveaux selon le type de question
                    # Les questions QCM basiques: niveau 1-2
                    # VF: niveau 2-3
                    # Ouvertes: niveau 3-4
                    if type_q == "QCM":
                        q.niveau_requis = 1
                        q.difficulte = 1
                    elif type_q == "VF":
                        q.niveau_requis = 2
                        q.difficulte = 2
                    elif type_q == "OUV":
                        q.niveau_requis = 3
                        q.difficulte = 3

                    if type_q == "QCM":
                        q.choix_a = q_data.get("choix_a")
                        q.choix_b = q_data.get("choix_b")
                        q.choix_c = q_data.get("choix_c")
                        q.choix_d = q_data.get("choix_d")
                        q.reponse_correcte = q_data.get("reponse_correcte")
                    elif type_q == "VF":
                        q.reponse_vf = q_data.get("reponse_vf")
                    elif type_q == "OUV":
                        q.reponse_ouverte = q_data.get("reponse_ouverte")

                    q.save()
                    created_q += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✔ {created_m} matière(s) créée(s), {created_q} question(s) ajoutée(s)."
        ))
        self.stdout.write(
            f"  Total : {Matiere.objects.count()} matières, {Question.objects.count()} questions."
        )