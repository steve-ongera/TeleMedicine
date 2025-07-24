from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Management pages
    path('patients/', views.patient_list, name='patient_list'),
    path('admissions/', views.admission_list, name='admission_list'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('staff/', views.staff_list, name='staff_list'),
    path('departments/', views.department_list, name='department_list'),
    path('wards/', views.ward_status, name='ward_status'),
    path('billing/', views.billing_summary, name='billing_summary'),
    
    # API endpoints for charts
    path('api/chart-data/<str:chart_type>/', views.chart_data, name='chart_data'),
]