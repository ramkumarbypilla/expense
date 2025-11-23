 #home/views.py
from django.shortcuts import render
from django.db.models import Sum, Count, Q
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


#

def summary(request):
    # ---------- DAILY ----------
    daily_qs = (
        Ride.objects
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(
            total_amount=Sum('amount'),
            total_rides=Count('id'),
            total_cash=Sum('amount', filter=Q(payment_type='cash')),
            total_card=Sum('amount', filter=Q(payment_type='card')),
            total_company=Sum('amount', filter=Q(payment_type='company')),
            total_tips=Sum('tips'),
        )
        .order_by('day')
    )

    daily_data = []
    for row in daily_qs:
        total_amount = row['total_amount'] or Decimal('0')
        total_tips = row['total_tips'] or Decimal('0')
        company_share = total_amount * Decimal('0.40')
        driver_share = total_amount * Decimal('0.60')

        daily_data.append({
            'day': row['day'],
            'total_amount': total_amount,
            'total_rides': row['total_rides'],
            'total_cash': row['total_cash'] or Decimal('0'),
            'total_card': row['total_card'] or Decimal('0'),
            'total_company': row['total_company'] or Decimal('0'),
            'total_tips': total_tips,
            'company_share': company_share,
            'driver_share': driver_share,
        })

    # ---------- WEEKLY ----------
    weekly_qs = (
        Ride.objects
        .annotate(
            year=ExtractYear('created_at'),
            week=ExtractWeek('created_at'),
        )
        .values('year', 'week')
        .annotate(
            total_amount=Sum('amount'),
            total_rides=Count('id'),
            total_cash=Sum('amount', filter=Q(payment_type='cash')),
            total_card=Sum('amount', filter=Q(payment_type='card')),
            total_company=Sum('amount', filter=Q(payment_type='company')),
            total_tips=Sum('tips'),
        )
        .order_by('year', 'week')
    )

    weekly_data = []
    for row in weekly_qs:
        total_amount = row['total_amount'] or Decimal('0')
        total_tips = row['total_tips'] or Decimal('0')
        company_share = total_amount * Decimal('0.40')
        driver_share = total_amount * Decimal('0.60')

        weekly_data.append({
            'year': row['year'],
            'week': row['week'],
            'total_amount': total_amount,
            'total_rides': row['total_rides'],
            'total_cash': row['total_cash'] or Decimal('0'),
            'total_card': row['total_card'] or Decimal('0'),
            'total_company': row['total_company'] or Decimal('0'),
            'total_tips': total_tips,
            'company_share': company_share,
            'driver_share': driver_share,
        })

    # ---------- MONTHLY ----------
    monthly_qs = (
        Ride.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            total_amount=Sum('amount'),
            total_rides=Count('id'),
            total_cash=Sum('amount', filter=Q(payment_type='cash')),
            total_card=Sum('amount', filter=Q(payment_type='card')),
            total_company=Sum('amount', filter=Q(payment_type='company')),
            total_tips=Sum('tips'),
        )
        .order_by('month')
    )

    monthly_data = []
    for row in monthly_qs:
        total_amount = row['total_amount'] or Decimal('0')
        total_tips = row['total_tips'] or Decimal('0')
        company_share = total_amount * Decimal('0.40')
        driver_share = total_amount * Decimal('0.60')

        monthly_data.append({
            'month': row['month'],
            'total_amount': total_amount,
            'total_rides': row['total_rides'],
            'total_cash': row['total_cash'] or Decimal('0'),
            'total_card': row['total_card'] or Decimal('0'),
            'total_company': row['total_company'] or Decimal('0'),
            'total_tips': total_tips,
            'company_share': company_share,
            'driver_share': driver_share,
        })

    # ---------- YEARLY ----------
    yearly_qs = (
        Ride.objects
        .annotate(year=ExtractYear('created_at'))
        .values('year')
        .annotate(
            total_amount=Sum('amount'),
            total_rides=Count('id'),
            total_cash=Sum('amount', filter=Q(payment_type='cash')),
            total_card=Sum('amount', filter=Q(payment_type='card')),
            total_company=Sum('amount', filter=Q(payment_type='company')),
            total_tips=Sum('tips'),
        )
        .order_by('year')
    )

    yearly_data = []
    for row in yearly_qs:
        total_amount = row['total_amount'] or Decimal('0')
        total_tips = row['total_tips'] or Decimal('0')
        company_share = total_amount * Decimal('0.40')
        driver_share = total_amount * Decimal('0.60')

        yearly_data.append({
            'year': row['year'],
            'total_amount': total_amount,
            'total_rides': row['total_rides'],
            'total_cash': row['total_cash'] or Decimal('0'),
            'total_card': row['total_card'] or Decimal('0'),
            'total_company': row['total_company'] or Decimal('0'),
            'total_tips': total_tips,
            'company_share': company_share,
            'driver_share': driver_share,
        })

    context = {
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'yearly_data': yearly_data,
    }
    return render(request, 'summary.html', context)
