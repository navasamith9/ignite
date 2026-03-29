# Create your views here.
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Transaction

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def initiate_payment(request):
    if request.method == "POST":
        amount = float(request.POST.get('amount'))
        service = request.POST.get('service', 'General') # e.g., 'Bus Booking'
        
        # 1. Create Order in Razorpay (Amount in paise)
        razorpay_order = client.order.create({
            "amount": int(amount * 100),
            "currency": "INR",
            "payment_capture": "1"
        })

        # 2. Record Transaction in Database
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            razorpay_order_id=razorpay_order['id'],
            service_type=service
        )

        context = {
            'order_id': razorpay_order['id'],
            'amount': amount,
            'key_id': settings.RAZORPAY_KEY_ID,
            'service': service,
            'user_email': request.user.email
        }
        return render(request, 'payments/checkout.html', context)