from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, County, SubCounty, Department, StaffDepartmentAssignment, Ward, Bed,
    Patient, Admission, BedTransfer, MorgueDepartment, MorgueCompartment, MorgueAdmission,
    Appointment, MedicalRecord, VitalSigns, Medicine, MedicineBatch, Prescription, PrescriptionItem,
    Laboratory, LabTest, LabOrder, LabResult, Bill, BillItem
)

# Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'employee_number', 'get_full_name', 'role', 'employment_status', 'is_active']
    list_filter = ['role', 'employment_status', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'first_name', 'last_name', 'employee_number', 'email', 'national_id']
    ordering = ['employee_number']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Information', {
            'fields': ('employee_number', 'national_id', 'phone_primary', 'phone_secondary', 
                      'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Address Information', {
            'fields': ('county_of_origin', 'sub_county', 'ward', 'address')
        }),
        ('Emergency Contact', {
            'fields': ('next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_phone')
        }),
        ('Employment Details', {
            'fields': ('role', 'secondary_role', 'employment_status', 'employment_date', 'termination_date')
        }),
        ('Professional Licenses', {
            'fields': ('kmpdc_license', 'nckenya_license', 'other_licenses')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Required Information', {
            'fields': ('employee_number', 'role', 'national_id', 'phone_primary', 'date_of_birth', 
                      'gender', 'employment_date')
        }),
    )

# Location Admin
@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'get_county_code']
    list_filter = ['county']
    search_fields = ['name', 'county__name']
    ordering = ['county__name', 'name']
    
    def get_county_code(self, obj):
        return obj.county.code
    get_county_code.short_description = 'County Code'

# Department Management
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department_type', 'head_of_department', 'location_building', 'bed_capacity']
    list_filter = ['department_type', 'location_building']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'department_type', 'description')
        }),
        ('Management', {
            'fields': ('head_of_department', 'deputy_head')
        }),
        ('Location', {
            'fields': ('location_building', 'location_floor', 'location_wing')
        }),
        ('Contact & Capacity', {
            'fields': ('phone_extension', 'email', 'established_date', 'bed_capacity', 'staff_capacity')
        }),
    )

@admin.register(StaffDepartmentAssignment)
class StaffDepartmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['staff', 'department', 'is_primary', 'assignment_date', 'position_title']
    list_filter = ['is_primary', 'department', 'assignment_date']
    search_fields = ['staff__first_name', 'staff__last_name', 'department__name']
    date_hierarchy = 'assignment_date'

# Ward Management
@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'ward_type', 'department', 'bed_capacity', 'current_occupancy', 'occupancy_rate_display']
    list_filter = ['ward_type', 'department', 'location_building']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def occupancy_rate_display(self, obj):
        rate = obj.occupancy_rate
        color = 'red' if rate > 90 else 'orange' if rate > 75 else 'green'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    occupancy_rate_display.short_description = 'Occupancy Rate'

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'ward', 'bed_type', 'status', 'last_sanitized']
    list_filter = ['status', 'bed_type', 'ward__ward_type', 'ward']
    search_fields = ['bed_number', 'ward__name']
    ordering = ['ward', 'bed_number']

# Patient Management
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_number', 'get_full_name', 'age', 'gender', 'patient_category', 'registration_date']
    list_filter = ['gender', 'patient_category', 'blood_group', 'county', 'registration_date']
    search_fields = ['patient_number', 'first_name', 'last_name', 'national_id', 'phone_primary']
    date_hierarchy = 'registration_date'
    ordering = ['-registration_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient_number', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 
                      'estimated_age', 'gender', 'marital_status', 'patient_photo')
        }),
        ('Identification', {
            'fields': ('national_id', 'passport_number', 'birth_certificate_number')
        }),
        ('Contact Information', {
            'fields': ('phone_primary', 'phone_secondary', 'email')
        }),
        ('Address', {
            'fields': ('county', 'sub_county', 'ward_location', 'village', 'physical_address', 'postal_address')
        }),
        ('Next of Kin', {
            'fields': ('next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_phone', 
                      'next_of_kin_id_number', 'next_of_kin_address')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'weight', 'height', 'chronic_conditions', 'allergies', 
                      'medications', 'disabilities')
        }),
        ('Insurance', {
            'fields': ('nhif_number', 'insurance_provider', 'insurance_number', 'insurance_expiry_date')
        }),
        ('Administrative', {
            'fields': ('patient_category', 'is_deceased', 'date_of_death')
        }),
    )
    
    readonly_fields = ['registration_date', 'last_visit_date']

# Admission Management
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'patient', 'primary_doctor', 'admission_date', 'status', 'length_of_stay']
    list_filter = ['status', 'admission_type', 'admission_date', 'primary_doctor']
    search_fields = ['admission_number', 'patient__first_name', 'patient__last_name', 'patient__patient_number']
    date_hierarchy = 'admission_date'
    ordering = ['-admission_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('admission_number', 'patient', 'admission_date', 'admission_type', 'status')
        }),
        ('Medical Team', {
            'fields': ('primary_doctor', 'consulting_doctors', 'assigned_nurse')
        }),
        ('Bed Assignment', {
            'fields': ('assigned_bed', 'previous_beds')
        }),
        ('Clinical Information', {
            'fields': ('chief_complaint', 'provisional_diagnosis', 'final_diagnosis', 'comorbidities')
        }),
        ('Referral Information', {
            'fields': ('referred_from', 'referring_doctor', 'admission_notes')
        }),
        ('Discharge Information', {
            'fields': ('discharge_date', 'discharge_type', 'discharge_summary', 'discharge_instructions', 
                      'follow_up_instructions', 'referred_to')
        }),
        ('Financial', {
            'fields': ('total_bill_amount', 'insurance_covered_amount', 'patient_payable_amount')
        }),
    )
    
    filter_horizontal = ['consulting_doctors', 'previous_beds']

@admin.register(BedTransfer)
class BedTransferAdmin(admin.ModelAdmin):
    list_display = ['admission', 'from_bed', 'to_bed', 'transfer_date', 'authorized_by']
    list_filter = ['transfer_date', 'authorized_by']
    search_fields = ['admission__patient__first_name', 'admission__patient__last_name']
    date_hierarchy = 'transfer_date'

# Morgue Management
@admin.register(MorgueDepartment)
class MorgueDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'current_occupancy', 'available_slots', 'manager']
    
@admin.register(MorgueCompartment)
class MorgueCompartmentAdmin(admin.ModelAdmin):
    list_display = ['compartment_number', 'morgue', 'status', 'temperature', 'last_sanitized']
    list_filter = ['status', 'morgue']

@admin.register(MorgueAdmission)
class MorgueAdmissionAdmin(admin.ModelAdmin):
    list_display = ['morgue_number', 'patient', 'date_of_death', 'certifying_doctor', 'status', 'days_in_morgue']
    list_filter = ['status', 'death_type', 'date_of_death']
    search_fields = ['morgue_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'date_of_death'

# Appointment Management
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_number', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_type', 'urgency_level', 'appointment_date', 'department']
    search_fields = ['appointment_number', 'patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('appointment_number', 'patient', 'doctor', 'department')
        }),
        ('Scheduling', {
            'fields': ('appointment_date', 'appointment_time', 'estimated_duration', 'appointment_type', 'status')
        }),
        ('Clinical', {
            'fields': ('chief_complaint', 'urgency_level')
        }),
        ('Management', {
            'fields': ('booked_by', 'booking_date', 'confirmed_date', 'check_in_time', 
                      'consultation_start_time', 'consultation_end_time')
        }),
        ('Follow-up', {
            'fields': ('notes', 'follow_up_required', 'follow_up_date', 'referral_required', 'referred_to_department')
        }),
        ('Payment', {
            'fields': ('consultation_fee', 'paid_amount', 'payment_status')
        }),
    )

# Medical Records
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['record_number', 'patient', 'doctor', 'record_date', 'record_type']
    list_filter = ['record_type', 'record_date', 'department', 'doctor']
    search_fields = ['record_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'record_date'

@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'recorded_date', 'temperature', 'blood_pressure', 'pulse_rate', 'recorded_by']
    list_filter = ['recorded_date', 'recorded_by']
    search_fields = ['patient__first_name', 'patient__last_name']
    date_hierarchy = 'recorded_date'

# Pharmacy Management
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'medicine_code', 'strength', 'dosage_form', 'current_stock', 'is_low_stock', 'selling_price']
    list_filter = ['dosage_form', 'therapeutic_class', 'storage_condition', 'requires_prescription']
    search_fields = ['name', 'generic_name', 'medicine_code']
    ordering = ['name']
    
    def is_low_stock_display(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">Low Stock</span>')
        return format_html('<span style="color: green;">OK</span>')
    is_low_stock_display.short_description = 'Stock Status'

@admin.register(MedicineBatch)
class MedicineBatchAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'batch_number', 'expiry_date', 'quantity_remaining', 'is_expired', 'days_to_expiry']
    list_filter = ['expiry_date', 'received_date', 'medicine__dosage_form']
    search_fields = ['batch_number', 'medicine__name']
    date_hierarchy = 'expiry_date'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_number', 'patient', 'doctor', 'prescribed_date', 'status', 'total_cost']
    list_filter = ['status', 'prescribed_date', 'doctor']
    search_fields = ['prescription_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'prescribed_date'

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

# Update Prescription admin to include inline
PrescriptionAdmin.inlines = [PrescriptionItemInline]

# Laboratory Management
@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'lab_manager', 'location']
    list_filter = ['department']
    search_fields = ['name', 'code']

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'test_code', 'category', 'laboratory', 'price', 'turnaround_time']
    list_filter = ['category', 'laboratory', 'sample_type']
    search_fields = ['test_name', 'test_code']
    ordering = ['test_name']

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'patient', 'ordering_doctor', 'order_date', 'priority', 'status']
    list_filter = ['status', 'priority', 'order_date']
    search_fields = ['order_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'order_date'

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['lab_order', 'test', 'result_value', 'is_abnormal', 'status', 'analysis_date']
    list_filter = ['status', 'is_abnormal', 'test__category']
    search_fields = ['lab_order__order_number', 'test__test_name']

# Billing Management
@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'patient', 'bill_date', 'bill_type', 'total_amount', 'paid_amount', 'balance_amount', 'status']
    list_filter = ['status', 'bill_type', 'bill_date']
    search_fields = ['bill_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'bill_date'
    
    def balance_amount_display(self, obj):
        balance = obj.balance_amount
        color = 'red' if balance > 0 else 'green'
        return format_html('<span style="color: {};">KSh {:,.2f}</span>', color, balance)
    balance_amount_display.short_description = 'Balance'

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1

# Update Bill admin to include inline
BillAdmin.inlines = [BillItemInline]

@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ['bill', 'description', 'category', 'quantity', 'service_date']
    list_filter = ['category', 'service_date']
    search_fields = ['description', 'bill__bill_number']

# Customize admin site
admin.site.site_header = "Hospital Management System"
admin.site.site_title = "HMS Admin"
admin.site.index_title = "Welcome to Hospital Management System Administration"