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
    # Percentages
    COMPANY_PERCENT = Decimal('0.40')
    DRIVER_PERCENT = Decimal('0.60')

    # ---------- DAILY TOTAL + RUNNING TOTAL ----------
    daily_qs = (
        Ride.objects
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(
            total_amount=Sum('amount'),
            total_tips=Sum('tips'),
        )
        .order_by('day')
    )

    daily_data = []
    running_total = Decimal('0')
    for row in daily_qs:
        amt = row['total_amount'] or Decimal('0')
        tips = row['total_tips'] or Decimal('0')

        company_share = (amt * COMPANY_PERCENT)
        driver_share = (amt * DRIVER_PERCENT)
        take_home = driver_share + tips

        running_total += amt

        daily_data.append({
            'day': row['day'],
            'total_amount': amt,
            'running_total': running_total,
            'company_share': company_share,
            'driver_share': driver_share,
            'total_tips': tips,
            'take_home': take_home,
        })

    # ---------- WEEKLY TOTAL ----------
    weekly_qs = (
        Ride.objects
        .annotate(
            year=ExtractYear('created_at'),
            week=ExtractWeek('created_at'),
        )
        .values('year', 'week')
        .annotate(
            total_amount=Sum('amount'),
            total_tips=Sum('tips'),
        )
        .order_by('year', 'week')
    )

    weekly_data = []
    for row in weekly_qs:
        amt = row['total_amount'] or Decimal('0')
        tips = row['total_tips'] or Decimal('0')

        company_share = (amt * COMPANY_PERCENT)
        driver_share = (amt * DRIVER_PERCENT)
        take_home = driver_share + tips

        weekly_data.append({
            'year': row['year'],
            'week': row['week'],
            'total_amount': amt,
            'company_share': company_share,
            'driver_share': driver_share,
            'total_tips': tips,
            'take_home': take_home,
        })

    # ---------- MONTHLY TOTAL ----------
    monthly_qs = (
        Ride.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            total_amount=Sum('amount'),
            total_tips=Sum('tips'),
        )
        .order_by('month')
    )

    monthly_data = []
    for row in monthly_qs:
        amt = row['total_amount'] or Decimal('0')
        tips = row['total_tips'] or Decimal('0')

        company_share = (amt * COMPANY_PERCENT)
        driver_share = (amt * DRIVER_PERCENT)
        take_home = driver_share + tips

        monthly_data.append({
            'month': row['month'],
            'total_amount': amt,
            'company_share': company_share,
            'driver_share': driver_share,
            'total_tips': tips,
            'take_home': take_home,
        })

    # ---------- YEARLY TOTAL ----------
    yearly_qs = (
        Ride.objects
        .annotate(year=ExtractYear('created_at'))
        .values('year')
        .annotate(
            total_amount=Sum('amount'),
            total_tips=Sum('tips'),
        )
        .order_by('year')
    )

    yearly_data = []
    for row in yearly_qs:
        amt = row['total_amount'] or Decimal('0')
        tips = row['total_tips'] or Decimal('0')

        company_share = (amt * COMPANY_PERCENT)
        driver_share = (amt * DRIVER_PERCENT)
        take_home = driver_share + tips

        yearly_data.append({
            'year': row['year'],
            'total_amount': amt,
            'company_share': company_share,
            'driver_share': driver_share,
            'total_tips': tips,
            'take_home': take_home,
        })

    context = {
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'yearly_data': yearly_data,
    }

    return render(request, 'summary.html', context)

