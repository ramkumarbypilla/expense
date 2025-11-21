# home/views.py
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth, ExtractWeek, ExtractYear
from decimal import Decimal
from .models import Ride


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


def rides_list(request):
    rides = Ride.objects.all().order_by('-created_at')  # Fetch all rides, latest first
    return render(request, 'rides.html', {'rides': rides})

def edit_ride(request, ride_id):
    """Edit a single ride."""
    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        ride.ride_from = request.POST.get('ride_from')
        ride.ride_to = request.POST.get('ride_to')
        ride.payment_type = request.POST.get('payment_type')
        ride.ride_type = request.POST.get('ride_type')  # if this field exists
        ride.amount = request.POST.get('amount') or 0
        ride.tips = request.POST.get('tips') or 0

        ride.save()
        return redirect('rides_list')  # go back to list page

    # GET → show form with existing values
    return render(request, 'edit_ride.html', {'ride': ride})


def delete_ride(request, ride_id):
    """Delete a single ride (with confirmation)."""
    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        ride.delete()
        return redirect('rides_list')

    # GET – show small confirmation page
    return render(request, 'confirm_delete.html', {'ride': ride})



def summary(request):
    # ---------- DAILY TOTAL + RUNNING TOTAL ----------
    daily_qs = (
        Ride.objects
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total_amount=Sum('amount'))
        .order_by('day')
    )

    daily_data = []
    running_total = Decimal('0')
    for row in daily_qs:
        total = row['total_amount'] or Decimal('0')
        running_total += total
        daily_data.append({
            'day': row['day'],
            'total_amount': total,
            'running_total': running_total,
        })

    # ---------- WEEKLY TOTAL ----------
    weekly_data = (
        Ride.objects
        .annotate(
            year=ExtractYear('created_at'),
            week=ExtractWeek('created_at'),
        )
        .values('year', 'week')
        .annotate(total_amount=Sum('amount'))
        .order_by('year', 'week')
    )

    # ---------- MONTHLY TOTAL ----------
    monthly_data = (
        Ride.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total_amount=Sum('amount'))
        .order_by('month')
    )

    # ---------- YEARLY TOTAL ----------
    yearly_data = (
        Ride.objects
        .annotate(year=ExtractYear('created_at'))
        .values('year')
        .annotate(total_amount=Sum('amount'))
        .order_by('year')
    )

    context = {
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'yearly_data': yearly_data,
    }

    return render(request, 'summary.html', context)

