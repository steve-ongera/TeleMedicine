from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
import json

from .models import (
    User, Patient, Admission, Department, Ward, Bed, 
    Appointment, MedicalRecord, Prescription, LabOrder,
    Bill, MorgueAdmission
)


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == 'admin':
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Access denied. Admin privileges required.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'hospital/login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Main admin dashboard with statistics and charts"""
    # Basic counts
    total_patients = Patient.objects.filter(is_active=True).count()
    total_staff = User.objects.filter(is_active=True).exclude(role='admin').count()
    total_departments = Department.objects.filter(is_active=True).count()
    total_beds = Bed.objects.filter(is_active=True).count()
    
    # Current admissions
    current_admissions = Admission.objects.filter(status='admitted').count()
    available_beds = Bed.objects.filter(status='available', is_active=True).count()
    bed_occupancy_rate = round((current_admissions / total_beds * 100), 1) if total_beds > 0 else 0
    
    # Today's statistics
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        appointment_date=today,
        status__in=['scheduled', 'confirmed', 'checked_in', 'in_progress']
    ).count()
    
    today_admissions = Admission.objects.filter(
        admission_date__date=today
    ).count()
    
    today_discharges = Admission.objects.filter(
        discharge_date__date=today
    ).count()
    
    # Financial summary (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    total_revenue = Bill.objects.filter(
        bill_date__date__gte=thirty_days_ago,
        status='fully_paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    pending_bills = Bill.objects.filter(
        status__in=['pending', 'partially_paid']
    ).aggregate(total=Sum('balance_amount'))['total'] or 0
    
    # Department-wise patient distribution
    dept_patients = Department.objects.annotate(
        patient_count=Count('admissions__patient', filter=Q(admissions__status='admitted'))
    ).values('name', 'patient_count')[:5]
    
    # Monthly admissions for line chart (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_admissions = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        count = Admission.objects.filter(
            admission_date__date__range=[month_start, month_end]
        ).count()
        monthly_admissions.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_admissions.reverse()
    
    # Ward occupancy for bar chart
    ward_occupancy = Ward.objects.filter(is_active=True).values(
        'name', 'bed_capacity', 'current_occupancy'
    )[:6]
    
    # Recent activities
    recent_admissions = Admission.objects.select_related('patient').order_by('-admission_date')[:5]
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-booking_date')[:5]
    
    # Staff by role distribution
    staff_by_role = User.objects.exclude(role='admin').values('role').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    context = {
        # Basic counts
        'total_patients': total_patients,
        'total_staff': total_staff,
        'total_departments': total_departments,
        'total_beds': total_beds,
        'current_admissions': current_admissions,
        'available_beds': available_beds,
        'bed_occupancy_rate': bed_occupancy_rate,
        
        # Today's stats
        'today_appointments': today_appointments,
        'today_admissions': today_admissions,
        'today_discharges': today_discharges,
        
        # Financial
        'total_revenue': total_revenue,
        'pending_bills': pending_bills,
        
        # Chart data
        'dept_patients': list(dept_patients),
        'monthly_admissions': monthly_admissions,
        'ward_occupancy': list(ward_occupancy),
        'staff_by_role': list(staff_by_role),
        
        # Recent activities
        'recent_admissions': recent_admissions,
        'recent_appointments': recent_appointments,
    }
    
    return render(request, 'hospital/dashboard.html', context)


@login_required
def patient_list(request):
    """List all patients"""
    patients = Patient.objects.filter(is_active=True).order_by('-created_at')[:50]
    return render(request, 'hospital/patient_list.html', {'patients': patients})


@login_required
def admission_list(request):
    """List current admissions"""
    admissions = Admission.objects.filter(status='admitted').select_related(
        'patient', 'primary_doctor', 'assigned_bed__ward'
    ).order_by('-admission_date')
    return render(request, 'hospital/admission_list.html', {'admissions': admissions})


@login_required
def appointment_list(request):
    """List today's appointments"""
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient', 'doctor', 'department').order_by('appointment_time')
    
    return render(request, 'hospital/appointment_list.html', {
        'appointments': appointments,
        'date': today
    })


@login_required
def staff_list(request):
    """List all staff members"""
    staff = User.objects.filter(is_active=True).exclude(role='admin').order_by('first_name')
    return render(request, 'hospital/staff_list.html', {'staff': staff})


@login_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.filter(is_active=True).select_related(
        'head_of_department'
    ).order_by('name')
    return render(request, 'hospital/department_list.html', {'departments': departments})


@login_required  
def ward_status(request):
    """Ward occupancy status"""
    wards = Ward.objects.filter(is_active=True).order_by('name')
    return render(request, 'hospital/ward_status.html', {'wards': wards})


@login_required
def billing_summary(request):
    """Billing and financial summary"""
    today = timezone.now().date()
    
    # Today's billing
    today_bills = Bill.objects.filter(bill_date__date=today)
    today_revenue = today_bills.filter(status='fully_paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Pending bills
    pending_bills = Bill.objects.filter(
        status__in=['pending', 'partially_paid']
    ).order_by('-bill_date')[:10]
    
    # Monthly revenue (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        revenue = Bill.objects.filter(
            bill_date__date__range=[month_start, month_end],
            status='fully_paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue)
        })
    
    monthly_revenue.reverse()
    
    context = {
        'today_revenue': today_revenue,
        'pending_bills': pending_bills,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'hospital/billing_summary.html', context)


# API endpoints for charts
@login_required
def chart_data(request, chart_type):
    """API endpoint for chart data"""
    today = timezone.now().date()
    
    if chart_type == 'monthly_admissions':
        monthly_admissions = []
        for i in range(6):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            count = Admission.objects.filter(
                admission_date__date__range=[month_start, month_end]
            ).count()
            monthly_admissions.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        monthly_admissions.reverse()
        return JsonResponse({'data': monthly_admissions})
    
    elif chart_type == 'department_patients':
        dept_patients = Department.objects.annotate(
            patient_count=Count('admissions__patient', filter=Q(admissions__status='admitted'))
        ).values('name', 'patient_count')[:5]
        return JsonResponse({'data': list(dept_patients)})
    
    elif chart_type == 'ward_occupancy':
        ward_occupancy = Ward.objects.filter(is_active=True).values(
            'name', 'bed_capacity', 'current_occupancy'
        )[:6]
        return JsonResponse({'data': list(ward_occupancy)})
    
    return JsonResponse({'error': 'Invalid chart type'}, status=400)