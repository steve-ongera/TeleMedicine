from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, County, SubCounty, Department, StaffDepartmentAssignment, Ward, Bed,
    Patient, Admission, BedTransfer, MorgueDepartment, MorgueCompartment,
    MorgueAdmission, Appointment, MedicalRecord, VitalSigns, Medicine,
    MedicineBatch, Prescription, PrescriptionItem, Laboratory, LabTest,
    LabOrder, LabResult, Bill, BillItem
)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'employee_number', 'role', 'is_active')
    list_filter = ('role', 'employment_status', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee_number', 'national_id')
    ordering = ('last_name', 'first_name')
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': (
            'first_name', 'last_name', 'email', 'date_of_birth', 'gender',
            'profile_picture', 'national_id', 'phone_primary', 'phone_secondary'
        )}),
        ('Employment Info', {'fields': (
            'employee_number', 'role', 'secondary_role', 'employment_status',
            'employment_date', 'termination_date', 'kmpdc_license',
            'nckenya_license', 'other_licenses'
        )}),
        ('Address Info', {'fields': (
            'county_of_origin', 'sub_county', 'ward', 'address'
        )}),
        ('Next of Kin', {'fields': (
            'next_of_kin_name', 'next_of_kin_relationship',
            'next_of_kin_phone'
        )}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Model Admins
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

class SubCountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'county')
    list_filter = ('county',)
    search_fields = ('name', 'county__name')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department_type', 'head_of_department', 'location_building')
    list_filter = ('department_type', 'is_active')
    search_fields = ('name', 'code', 'head_of_department__username')
    raw_id_fields = ('head_of_department', 'deputy_head')

class StaffDepartmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('staff', 'department', 'is_primary', 'assignment_date')
    list_filter = ('department', 'is_primary', 'is_active')
    search_fields = ('staff__username', 'department__name')

class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'ward_type', 'department', 'nurse_in_charge', 'bed_capacity', 'current_occupancy')
    list_filter = ('ward_type', 'department', 'is_active')
    search_fields = ('name', 'code', 'department__name')
    raw_id_fields = ('nurse_in_charge',)

class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'ward', 'bed_type', 'status', 'last_sanitized')
    list_filter = ('ward', 'bed_type', 'status', 'is_active')
    search_fields = ('bed_number', 'ward__name')

class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_number', 'get_full_name', 'gender', 'age', 'patient_category', 'registration_date')
    list_filter = ('gender', 'patient_category', 'county', 'is_active')
    search_fields = ('patient_number', 'first_name', 'last_name', 'national_id', 'phone_primary')
    date_hierarchy = 'registration_date'
    raw_id_fields = ('county', 'sub_county')

class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'patient', 'admission_type', 'status', 'admission_date', 'length_of_stay')
    list_filter = ('admission_type', 'status', 'department', 'is_active')
    search_fields = ('admission_number', 'patient__first_name', 'patient__last_name')
    date_hierarchy = 'admission_date'
    raw_id_fields = ('patient', 'primary_doctor', 'assigned_nurse', 'assigned_bed')

# Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(County, CountyAdmin)
admin.site.register(SubCounty, SubCountyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(StaffDepartmentAssignment, StaffDepartmentAssignmentAdmin)
admin.site.register(Ward, WardAdmin)
admin.site.register(Bed, BedAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Admission, AdmissionAdmin)
admin.site.register(BedTransfer)
admin.site.register(MorgueDepartment)
admin.site.register(MorgueCompartment)
admin.site.register(MorgueAdmission)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(VitalSigns)
admin.site.register(Medicine)
admin.site.register(MedicineBatch)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
admin.site.register(Laboratory)
admin.site.register(LabTest)
admin.site.register(LabOrder)
admin.site.register(LabResult)
admin.site.register(Bill)
admin.site.register(BillItem)