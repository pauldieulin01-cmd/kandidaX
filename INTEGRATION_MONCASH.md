# 🔧 GUIDE D'INTÉGRATION MonCash

## 📋 Étapes pour intégrer l'API MonCash

### 1. Créer un compte MonCash Business
- Visitez [moncash.ht](https://moncash.ht)
- Créez un compte marchand
- Obtenez vos clés API (API Key et Secret Key)

### 2. Installer le SDK/Client MonCash
```bash
pip install python-moncash
# ou
pip install moncash
```

### 3. Créer un fichier de configuration
Créez `src/settings_payment.py`:
```python
# Paramètres MonCash
MONCASH_API_KEY = "votre_api_key"
MONCASH_SECRET_KEY = "votre_secret_key"
MONCASH_ENVIRONMENT = "sandbox"  # "sandbox" ou "production"
MONCASH_CALLBACK_URL = "https://votresite.com/api/paiement/callback/"
```

### 4. Ajouter à settings.py
Dans `src/Plateforme/settings.py`:
```python
# Import des paramètres de paiement
try:
    from .settings_payment import *
except ImportError:
    # Paramètres par défaut
    MONCASH_API_KEY = ""
    MONCASH_SECRET_KEY = ""
    MONCASH_ENVIRONMENT = "sandbox"
    MONCASH_CALLBACK_URL = ""
```

### 5. Créer un service MonCash
Créez `src/Quizapp/services/moncash_service.py`:
```python
import requests
from django.conf import settings
from Quizapp.models import Payment
from django.utils import timezone

class MonCashService:
    """Service pour gérer les transactions MonCash"""
    
    def __init__(self):
        self.api_key = settings.MONCASH_API_KEY
        self.secret_key = settings.MONCASH_SECRET_KEY
        self.environment = settings.MONCASH_ENVIRONMENT
        
        if self.environment == "sandbox":
            self.base_url = "https://sandbox.moncash.ht/api"
        else:
            self.base_url = "https://moncash.ht/api"
    
    def create_transaction(self, payment_reference, amount, phone, description):
        """Crée une transaction MonCash"""
        
        payload = {
            "transaction_id": payment_reference,
            "amount": amount,
            "currency": "HTG",
            "customer_phone": phone,
            "description": description,
            "notif_url": settings.MONCASH_CALLBACK_URL
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transactions",
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def verify_transaction(self, transaction_id):
        """Vérifie le statut d'une transaction"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

# Créer une instance globale
moncash_service = MonCashService()
```

### 6. Mettre à jour les vues
Dans `src/Quizapp/views.py`, remplacer les placeholders:

**Pour `initier_paiement_moncash()`:**
```python
from Quizapp.services.moncash_service import moncash_service

@login_required
@require_http_methods(["POST"])
def initier_paiement_moncash(request):
    """API pour initier un paiement MonCash"""
    try:
        data = json.loads(request.body)
        level = data.get('level')
        phone = data.get('phone', '').strip()
        
        etudiant = request.user.etudiant
        price = etudiant.get_level_price(level)
        
        if price == 0:
            return JsonResponse({'error': 'Ce niveau n\'est pas payant'}, status=400)
        
        if not phone:
            return JsonResponse({'error': 'Numéro de téléphone requis'}, status=400)
        
        # Vérifier si le paiement n'existe pas déjà
        existing = Payment.objects.filter(
            etudiant=etudiant,
            level=level,
            status='completed'
        ).exists()
        
        if existing:
            return JsonResponse({'error': 'Vous avez déjà payé pour ce niveau'})
        
        # Créer un paiement
        import uuid
        reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment.objects.create(
            etudiant=etudiant,
            level=level,
            amount=price,
            status='pending',
            phone_number=phone,
            reference=reference
        )
        
        # INTÉGRATION MONCASH
        result = moncash_service.create_transaction(
            payment_reference=reference,
            amount=price,
            phone=phone,
            description=f"Déblocage Niveau {level} - Plateforme Concours"
        )
        
        if "error" not in result:
            payment.transaction_id = result.get('transaction_id')
            payment.save()
            
            return JsonResponse({
                'success': True,
                'reference': reference,
                'phone': phone,
                'amount': price,
                'message': f'Veuillez valider le paiement de {price}G sur votre téléphone MonCash ({phone})'
            })
        else:
            payment.status = 'failed'
            payment.save()
            return JsonResponse({'error': f"Erreur MonCash: {result['error']}"}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
```

**Pour `verifier_paiement()`:**
```python
@login_required
@require_http_methods(["GET"])
def verifier_paiement(request, reference):
    """Vérifier le statut d'un paiement"""
    try:
        payment = Payment.objects.get(reference=reference, etudiant=request.user.etudiant)
        
        if payment.transaction_id:
            # Vérifier avec MonCash
            result = moncash_service.verify_transaction(payment.transaction_id)
            
            if "error" not in result and result.get('status') == 'completed':
                payment.status = 'completed'
                payment.date_completion = timezone.now()
                payment.save()
            elif "error" not in result and result.get('status') == 'failed':
                payment.status = 'failed'
                payment.save()
        
        return JsonResponse({
            'status': payment.status,
            'level': payment.level,
            'amount': payment.amount,
        })
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Paiement introuvable'}, status=404)
```

### 7. Créer un endpoint webhook (optionnel mais recommandé)
```python
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["POST"])
def moncash_webhook(request):
    """Webhook pour les notifications MonCash"""
    try:
        data = json.loads(request.body)
        
        # Vérifier la signature (recommandé pour la sécurité)
        # Voir la documentation MonCash pour les détails
        
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        payment = Payment.objects.get(transaction_id=transaction_id)
        
        if status == 'completed':
            payment.status = 'completed'
            payment.date_completion = timezone.now()
            payment.save()
        
        return HttpResponse(status=200)
    except Payment.DoesNotExist:
        return HttpResponse(status=404)
    except Exception as e:
        return HttpResponse(status=400)
```

Puis ajouter à `urls.py`:
```python
path('api/paiement/webhook/', moncash_webhook, name='moncash_webhook'),
```

### 8. Tester en Sandbox

1. Utilisez les numéros de test MonCash fournis dans la documentation
2. Testez le flux complet (initiation → vérification → confirmation)
3. Vérifiez que les payements apparaissent correctement dans l'admin

### 9. Déployer en Production

1. Remettez `MONCASH_ENVIRONMENT = "production"` 
2. Utilisez les vraies clés API MonCash (production)
3. Testez avec de petits montants d'abord
4. Mettez en place le suivi et les alertes

## 🔐 Sécurité

- ✅ Jamais commiter vos clés API (utilisez `.env`)
- ✅ Valider les montants côté serveur
- ✅ Vérifier les signatures des webhooks
- ✅ Utiliser HTTPS partout
- ✅ Implémenter un taux de retry pour les vérifications échouées
- ✅ Logger toutes les transactions

## 📞 Support MonCash

- Documentation: https://moncash.ht/docs
- Support: support@moncash.ht
- Statut: https://status.moncash.ht
