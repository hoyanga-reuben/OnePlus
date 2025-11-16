# content/webhooks.py (very simplified)
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
from .models import MembershipPayment, MemberProfile
from django.utils import timezone

@csrf_exempt
def payment_webhook(request):
    # validate signature from provider!
    payload = json.loads(request.body.decode('utf-8'))
    tx_id = payload.get('tx_id')
    status = payload.get('status')  # provider-specific
    reference = payload.get('reference')
    amount = payload.get('amount')

    # find payment record (you might match on reference or create if not exists)
    try:
        payment = MembershipPayment.objects.get(reference=reference)
    except MembershipPayment.DoesNotExist:
        return JsonResponse({'error': 'payment not found'}, status=404)

    if status == 'success':
        payment.status = 'verified'
        payment.verified_at = timezone.now()
        payment.verified_by = None
        payment.date_paid = timezone.now().date()
        payment.save()
        profile, _ = MemberProfile.objects.get_or_create(user=payment.user)
        profile.last_payment_date = payment.date_paid
        profile.update_membership_status()
    return HttpResponse('ok')
