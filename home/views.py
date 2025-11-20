from django.shortcuts import render
from .models import Ride   # ⬅️ import the model we created

def home(request):
    if request.method == 'POST':
        # 1. Get data from form
        ride_from = request.POST.get('ride_from')
        ride_to = request.POST.get('ride_to')
        payment_type = request.POST.get('payment_type')
        ride_type = request.POST.get('ride_type')
        amount = request.POST.get('amount')
        tips = request.POST.get('tips')

        # 2. Convert amount and tips to numbers (optional safety)
        amount = amount or "0"
        tips = tips or "0"

        # 3. Save to database
        ride = Ride.objects.create(
            ride_from=ride_from,
            ride_to=ride_to,
            payment_type=payment_type,
            ride_type=ride_type,
            amount=amount,
            tips=tips,
        )

        # 4. Prepare data to send back to template
        params = {
            'ride_from': ride_from,
            'ride_to': ride_to,
            'payment_type': payment_type,
            'ride_type': ride_type,
            'amount': amount,
            'tips': tips,
            'saved': True,
            'ride': ride,
        }

        print("Ride saved:", params)
        return render(request, 'home.html', params)

    # If GET request (first time page load)
    return render(request, 'home.html')
