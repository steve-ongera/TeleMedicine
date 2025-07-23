from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class BaseModel(models.Model):
    """Abstract base model with common fields for audit trail"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class User(AbstractUser):
    """System users with comprehensive profile"""
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('medical_superintendent', 'Medical Superintendent'),
        ('clinical_officer', 'Clinical Officer'),
        ('medical_officer', 'Medical Officer'),
        ('consultant', 'Consultant Doctor'),
        ('registrar', 'Registrar'),
        ('intern', 'Medical Intern'),
        ('nurse_manager', 'Nurse Manager'),
        ('senior_nurse', 'Senior Nurse'),
        ('registered_nurse', 'Registered Nurse'),
        ('enrolled_nurse', 'Enrolled Nurse'),
        ('midwife', 'Midwife'),
        ('lab_manager', 'Laboratory Manager'),
        ('lab_technologist', 'Medical Laboratory Technologist'),
        ('lab_technician', 'Laboratory Technician'),
        ('pharmacist', 'Pharmacist'),
        ('pharmaceutical_technologist', 'Pharmaceutical Technologist'),
        ('radiographer', 'Radiographer'),
        ('physiotherapist', 'Physiotherapist'),
        ('nutritionist', 'Nutritionist'),
        ('social_worker', 'Medical Social Worker'),
        ('records_officer', 'Medical Records Officer'),
        ('cashier', 'Hospital Cashier'),
        ('receptionist', 'Receptionist'),
        ('security', 'Security Officer'),
        ('cleaner', 'Hospital Cleaner'),
        ('driver', 'Ambulance Driver'),
    ]
    
    EMPLOYMENT_STATUS = [
        ('permanent', 'Permanent Employee'),
        ('contract', 'Contract Employee'),
        ('locum', 'Locum'),
        ('intern', 'Intern'),
        ('volunteer', 'Volunteer'),
        ('retired', 'Retired'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    secondary_role = models.CharField(max_length=30, choices=ROLE_CHOICES, blank=True)
    national_id = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^\d{7,8}$')])
    phone_primary = models.CharField(max_length=15, validators=[RegexValidator(r'^(\+254|0)[1-9]\d{8}$')])
    phone_secondary = models.CharField(max_length=15, blank=True, validators=[RegexValidator(r'^(\+254|0)[1-9]\d{8}$')])
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    county_of_origin = models.CharField(max_length=50)
    sub_county = models.CharField(max_length=50)
    ward = models.CharField(max_length=50)
    address = models.TextField()
    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_relationship = models.CharField(max_length=50)
    next_of_kin_phone = models.CharField(max_length=15, validators=[RegexValidator(r'^(\+254|0)[1-9]\d{8}$')])
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='permanent')
    employment_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    kmpdc_license = models.CharField(max_length=50, blank=True, help_text="Kenya Medical Practitioners & Dentists Council License")
    nckenya_license = models.CharField(max_length=50, blank=True, help_text="Nursing Council of Kenya License")
    other_licenses = models.TextField(blank=True, help_text="Other professional licenses")
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_number})"
    
    def get_primary_department(self):
        return self.department_assignments.filter(is_primary=True, is_active=True).first()


class County(models.Model):
    """Kenya Counties"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=3, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Counties"


class SubCounty(models.Model):
    """Kenya Sub-Counties"""
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='sub_counties')
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name}, {self.county.name}"
    
    class Meta:
        verbose_name_plural = "Sub Counties"
        unique_together = ['county', 'name']


class Department(BaseModel):
    """Hospital departments with detailed management"""
    DEPARTMENT_TYPES = [
        ('clinical', 'Clinical Department'),
        ('diagnostic', 'Diagnostic Department'),
        ('support', 'Support Department'),
        ('administrative', 'Administrative Department'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    department_type = models.CharField(max_length=20, choices=DEPARTMENT_TYPES)
    description = models.TextField()
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='departments_headed')
    deputy_head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='departments_deputy_headed')
    location_building = models.CharField(max_length=50)
    location_floor = models.CharField(max_length=20)
    location_wing = models.CharField(max_length=50, blank=True)
    phone_extension = models.CharField(max_length=10, blank=True)
    email = models.EmailField(blank=True)
    established_date = models.DateField()
    bed_capacity = models.PositiveIntegerField(default=0)
    staff_capacity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class StaffDepartmentAssignment(BaseModel):
    """Staff assignments to departments"""
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='department_assignments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='staff_assignments')
    is_primary = models.BooleanField(default=True)
    assignment_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    position_title = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['staff', 'department', 'is_primary']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.department.name}"


class Ward(BaseModel):
    """Hospital wards with detailed management"""
    WARD_TYPES = [
        ('general_male', 'General Male Ward'),
        ('general_female', 'General Female Ward'),
        ('pediatric', 'Pediatric Ward'),
        ('maternity', 'Maternity Ward'),
        ('surgical_male', 'Surgical Male Ward'),
        ('surgical_female', 'Surgical Female Ward'),
        ('orthopedic', 'Orthopedic Ward'),
        ('medical', 'Medical Ward'),
        ('icu', 'Intensive Care Unit'),
        ('hdu', 'High Dependency Unit'),
        ('nicu', 'Neonatal ICU'),
        ('burns', 'Burns Unit'),
        ('isolation', 'Isolation Ward'),
        ('psychiatric', 'Psychiatric Ward'),
        ('private', 'Private Ward'),
        ('emergency', 'Emergency Ward'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='wards')
    location_building = models.CharField(max_length=50)
    location_floor = models.CharField(max_length=20)
    bed_capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    nurse_in_charge = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='wards_managed', limit_choices_to={'role__in': ['nurse_manager', 'senior_nurse']}
    )
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.TextField(blank=True)
    visiting_hours = models.CharField(max_length=100, default="2:00 PM - 6:00 PM")
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def available_beds(self):
        return self.bed_capacity - self.current_occupancy
    
    @property
    def occupancy_rate(self):
        if self.bed_capacity == 0:
            return 0
        return (self.current_occupancy / self.bed_capacity) * 100


class Bed(BaseModel):
    """Individual beds in wards"""
    BED_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('isolation', 'Isolation'),
    ]
    
    bed_number = models.CharField(max_length=20)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_type = models.CharField(max_length=50, choices=[
        ('standard', 'Standard Bed'),
        ('electric', 'Electric Bed'),
        ('icu', 'ICU Bed'),
        ('isolation', 'Isolation Bed'),
        ('pediatric', 'Pediatric Bed'),
    ])
    status = models.CharField(max_length=20, choices=BED_STATUS, default='available')
    last_sanitized = models.DateTimeField(null=True, blank=True)
    equipment_attached = models.TextField(blank=True, help_text="List of equipment attached to this bed")
    
    class Meta:
        unique_together = ['ward', 'bed_number']
    
    def __str__(self):
        return f"{self.ward.name} - Bed {self.bed_number}"


class Patient(BaseModel):
    """Patient information - separate from User model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('I', 'Intersex'),
    ]
    
    MARITAL_STATUS = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ('unknown', 'Unknown'),
    ]
    
    PATIENT_CATEGORIES = [
        ('general', 'General Patient'),
        ('nhif', 'NHIF Patient'),
        ('private', 'Private Patient'),
        ('corporate', 'Corporate Patient'),
        ('charity', 'Charity Patient'),
        ('staff', 'Staff/Dependant'),
        ('emergency', 'Emergency Patient'),
    ]
    
    # Basic Information
    patient_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    estimated_age = models.PositiveIntegerField(null=True, blank=True, help_text="If DOB unknown")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS, blank=True)
    
    # Identification
    national_id = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\d{7,8}$')])
    passport_number = models.CharField(max_length=20, blank=True)
    birth_certificate_number = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    phone_primary = models.CharField(max_length=15, blank=True, validators=[RegexValidator(r'^(\+254|0)[1-9]\d{8}$')])
    phone_secondary = models.CharField(max_length=15, blank=True, validators=[RegexValidator(r'^(\+254|0)[1-9]\d{8}$')])
    email = models.EmailField(blank=True)
    
    # Address Information
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.SET_NULL, null=True, blank=True)
    ward_location = models.CharField(max_length=50, blank=True)
    village = models.CharField(max_length=50, blank=True)
    physical_address = models.TextField(blank=True)
    postal_address = models.CharField(max_length=100, blank=True)
    
    # Next of Kin Information
    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_relationship = models.CharField(max_length=50)
    next_of_kin_phone = models.CharField(max_length=15, validators=[RegexValidator(r'^(\+254|0)[1-9]\d{8}$')])
    next_of_kin_id_number = models.CharField(max_length=20, blank=True)
    next_of_kin_address = models.TextField(blank=True)
    
    # Medical Information
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='unknown')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chronic_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True, help_text="Current medications")
    disabilities = models.TextField(blank=True)
    
    # Administrative Information
    patient_category = models.CharField(max_length=20, choices=PATIENT_CATEGORIES, default='general')
    registration_date = models.DateTimeField(default=timezone.now)
    last_visit_date = models.DateTimeField(null=True, blank=True)
    is_deceased = models.BooleanField(default=False)
    date_of_death = models.DateTimeField(null=True, blank=True)
    
    # Insurance Information
    nhif_number = models.CharField(max_length=20, blank=True)
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    insurance_expiry_date = models.DateField(null=True, blank=True)
    
    # Photos
    patient_photo = models.ImageField(upload_to='patient_photos/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.patient_number})"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        if self.estimated_age and not self.date_of_birth:
            return self.estimated_age
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def get_current_admission(self):
        return self.admissions.filter(status='admitted').first()
    
    def get_assigned_doctor(self):
        current_admission = self.get_current_admission()
        if current_admission:
            return current_admission.primary_doctor
        return None
    
    def get_assigned_nurse(self):
        current_admission = self.get_current_admission()
        if current_admission and current_admission.assigned_bed:
            return current_admission.assigned_bed.ward.nurse_in_charge
        return None


class Admission(BaseModel):
    """Patient admissions with detailed tracking"""
    ADMISSION_STATUS = [
        ('admitted', 'Currently Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
        ('absconded', 'Absconded'),
        ('died', 'Deceased'),
        ('referred', 'Referred to Another Facility'),
    ]
    
    ADMISSION_TYPES = [
        ('emergency', 'Emergency Admission'),
        ('elective', 'Elective Admission'),
        ('maternity', 'Maternity Admission'),
        ('surgical', 'Surgical Admission'),
        ('medical', 'Medical Admission'),
        ('pediatric', 'Pediatric Admission'),
        ('psychiatric', 'Psychiatric Admission'),
        ('transfer_in', 'Transfer from Another Facility'),
    ]
    
    DISCHARGE_TYPES = [
        ('normal', 'Normal Discharge'),
        ('against_advice', 'Against Medical Advice'),
        ('referred', 'Referred'),
        ('transferred', 'Transferred'),
        ('absconded', 'Absconded'),
        ('died', 'Deceased'),
    ]
    
    admission_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateTimeField(default=timezone.now)
    admission_type = models.CharField(max_length=20, choices=ADMISSION_TYPES)
    
    # Medical Team Assignment
    primary_doctor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='primary_admissions',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar', 'clinical_officer']}
    )
    consulting_doctors = models.ManyToManyField(
        User, blank=True, related_name='consulting_admissions',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar', 'clinical_officer']}
    )
    assigned_nurse = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_admissions',
        limit_choices_to={'role__in': ['registered_nurse', 'enrolled_nurse', 'senior_nurse']}
    )
    
    # Bed Assignment
    assigned_bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True, related_name='admissions')
    previous_beds = models.ManyToManyField(Bed, blank=True, related_name='previous_admissions')
    
    # Clinical Information
    chief_complaint = models.TextField()
    provisional_diagnosis = models.TextField()
    final_diagnosis = models.TextField(blank=True)
    comorbidities = models.TextField(blank=True)
    
    # Admission Details
    referred_from = models.CharField(max_length=200, blank=True)
    referring_doctor = models.CharField(max_length=100, blank=True)
    admission_notes = models.TextField(blank=True)
    
    # Status Information
    status = models.CharField(max_length=20, choices=ADMISSION_STATUS, default='admitted')
    
    # Discharge Information
    discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_type = models.CharField(max_length=20, choices=DISCHARGE_TYPES, blank=True)
    discharge_summary = models.TextField(blank=True)
    discharge_instructions = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    referred_to = models.CharField(max_length=200, blank=True)
    
    # Financial Information
    total_bill_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_covered_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patient_payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.admission_number} - {self.patient.get_full_name()}"
    
    @property
    def length_of_stay(self):
        if self.discharge_date:
            return (self.discharge_date - self.admission_date).days
        return (timezone.now() - self.admission_date).days
    
    @property
    def current_ward(self):
        if self.assigned_bed:
            return self.assigned_bed.ward
        return None


class BedTransfer(BaseModel):
    """Track patient bed transfers"""
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE, related_name='bed_transfers')
    from_bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='transfers_from', null=True, blank=True)
    to_bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='transfers_to')
    transfer_date = models.DateTimeField(default=timezone.now)
    reason_for_transfer = models.TextField()
    authorized_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authorized_transfers')
    
    def __str__(self):
        from_bed_str = f"from {self.from_bed}" if self.from_bed else "from admission"
        return f"{self.admission.patient.get_full_name()}: {from_bed_str} to {self.to_bed}"


class MorgueDepartment(BaseModel):
    """Morgue department management"""
    name = models.CharField(max_length=100, default="Hospital Morgue")
    location_building = models.CharField(max_length=50)
    location_floor = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='morgue_managed'
    )
    phone_extension = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def available_slots(self):
        return self.capacity - self.current_occupancy


class MorgueCompartment(BaseModel):
    """Individual morgue compartments"""
    COMPARTMENT_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]
    
    compartment_number = models.CharField(max_length=20)
    morgue = models.ForeignKey(MorgueDepartment, on_delete=models.CASCADE, related_name='compartments')
    status = models.CharField(max_length=20, choices=COMPARTMENT_STATUS, default='available')
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    last_sanitized = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['morgue', 'compartment_number']
    
    def __str__(self):
        return f"{self.morgue.name} - Compartment {self.compartment_number}"


class MorgueAdmission(BaseModel):
    """Dead body admissions to morgue"""
    DEATH_TYPES = [
        ('natural', 'Natural Death'),
        ('accident', 'Accident'),
        ('suicide', 'Suicide'),
        ('homicide', 'Homicide'),
        ('unknown', 'Unknown'),
        ('medical', 'Medical Complication'),
    ]
    
    BODY_STATUS = [
        ('stored', 'Stored in Morgue'),
        ('released', 'Released to Family'),
        ('buried', 'Buried (Unclaimed)'),
        ('transferred', 'Transferred to Another Morgue'),
        ('autopsy', 'Under Autopsy'),
    ]
    
    morgue_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='morgue_admissions')
    hospital_admission = models.ForeignKey(
        Admission, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='morgue_admission'
    )
    
    # Death Information
    date_of_death = models.DateTimeField()
    time_of_death = models.TimeField()
    place_of_death = models.CharField(max_length=200)
    cause_of_death = models.TextField()
    death_type = models.CharField(max_length=20, choices=DEATH_TYPES)
    certifying_doctor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='certified_deaths',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar']}
    )
    
    # Morgue Assignment
    assigned_compartment = models.ForeignKey(
        MorgueCompartment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='morgue_admissions'
    )
    admission_to_morgue_date = models.DateTimeField(default=timezone.now)
    
    # Body Details
    body_condition = models.TextField(blank=True)
    personal_effects = models.TextField(blank=True)
    identification_marks = models.TextField(blank=True)
    
    # Legal Requirements
    death_certificate_issued = models.BooleanField(default=False)
    death_certificate_number = models.CharField(max_length=50, blank=True)
    police_case_number = models.CharField(max_length=50, blank=True)
    requires_autopsy = models.BooleanField(default=False)
    autopsy_completed = models.BooleanField(default=False)
    autopsy_report = models.TextField(blank=True)
    
    # Release Information
    status = models.CharField(max_length=20, choices=BODY_STATUS, default='stored')
    release_date = models.DateTimeField(null=True, blank=True)
    released_to_name = models.CharField(max_length=100, blank=True)
    released_to_relationship = models.CharField(max_length=50, blank=True)
    released_to_id_number = models.CharField(max_length=20, blank=True)
    released_to_phone = models.CharField(max_length=15, blank=True)
    release_authorization = models.CharField(max_length=100, blank=True)
    
    # Charges
    morgue_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    autopsy_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    certificate_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.morgue_number} - {self.patient.get_full_name()}"
    
    @property
    def days_in_morgue(self):
        if self.release_date:
            return (self.release_date - self.admission_to_morgue_date).days
        return (timezone.now() - self.admission_to_morgue_date).days


class Appointment(BaseModel):
    """Patient appointments with comprehensive tracking"""
    APPOINTMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    APPOINTMENT_TYPES = [
        ('consultation', 'General Consultation'),
        ('follow_up', 'Follow-up Visit'),
        ('specialist', 'Specialist Consultation'),
        ('procedure', 'Minor Procedure'),
        ('vaccination', 'Vaccination'),
        ('antenatal', 'Antenatal Visit'),
        ('family_planning', 'Family Planning'),
        ('counseling', 'Counseling Session'),
        ('emergency', 'Emergency Consultation'),
    ]
    
    appointment_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='doctor_appointments',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar', 'clinical_officer']}
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='appointments')
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    estimated_duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='scheduled')
    
    # Clinical Information
    chief_complaint = models.TextField()
    urgency_level = models.CharField(max_length=20, choices=[
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    ], default='routine')
    
    # Appointment Management
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_appointments')
    booking_date = models.DateTimeField(default=timezone.now)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    consultation_start_time = models.DateTimeField(null=True, blank=True)
    consultation_end_time = models.DateTimeField(null=True, blank=True)
    
    # Follow-up and Notes
    notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    referral_required = models.BooleanField(default=False)
    referred_to_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='referral_appointments'
    )
    
    # Payment Information
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Payment Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('waived', 'Fee Waived'),
    ], default='pending')
    
    class Meta:
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.appointment_number} - {self.patient.get_full_name()} with {self.doctor.get_full_name()}"


class MedicalRecord(BaseModel):
    """Comprehensive patient medical records"""
    RECORD_TYPES = [
        ('consultation', 'Consultation Record'),
        ('admission', 'Admission Record'),
        ('procedure', 'Procedure Record'),
        ('emergency', 'Emergency Record'),
        ('discharge', 'Discharge Summary'),
        ('referral', 'Referral Letter'),
    ]
    
    record_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_medical_records',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar', 'clinical_officer']}
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    admission = models.ForeignKey(Admission, on_delete=models.SET_NULL, null=True, blank=True)
    
    record_date = models.DateTimeField(default=timezone.now)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    
    # Clinical Assessment
    chief_complaint = models.TextField()
    history_of_presenting_illness = models.TextField()
    past_medical_history = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    social_history = models.TextField(blank=True)
    drug_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    
    # Physical Examination
    general_appearance = models.TextField(blank=True)
    vital_signs = models.JSONField(default=dict, blank=True)  # Temperature, BP, Pulse, RR, SpO2, etc.
    systemic_examination = models.TextField(blank=True)
    
    # Investigations and Results
    investigations_ordered = models.TextField(blank=True)
    investigation_results = models.TextField(blank=True)
    
    # Diagnosis and Management
    provisional_diagnosis = models.TextField()
    differential_diagnosis = models.TextField(blank=True)
    final_diagnosis = models.TextField(blank=True)
    icd_10_codes = models.CharField(max_length=200, blank=True)
    
    # Treatment Plan
    treatment_plan = models.TextField()
    medications_prescribed = models.TextField(blank=True)
    procedures_performed = models.TextField(blank=True)
    
    # Follow-up and Referrals
    follow_up_instructions = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    referrals_made = models.TextField(blank=True)
    patient_education = models.TextField(blank=True)
    
    # Record Management
    is_confidential = models.BooleanField(default=False)
    access_restrictions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.record_number} - {self.patient.get_full_name()} ({self.record_date.date()})"


class VitalSigns(BaseModel):
    """Patient vital signs tracking"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, null=True, blank=True)
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE, null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_vitals')
    
    recorded_date = models.DateTimeField(default=timezone.now)
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="°C")
    systolic_bp = models.PositiveIntegerField(null=True, blank=True, help_text="mmHg")
    diastolic_bp = models.PositiveIntegerField(null=True, blank=True, help_text="mmHg")
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="beats per minute")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="breaths per minute")
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True, help_text="SpO2 %")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    
    # Additional Measurements
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="mmol/L")
    pain_score = models.PositiveIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Pain scale 0-10"
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.recorded_date.date()}"
    
    @property
    def blood_pressure(self):
        if self.systolic_bp and self.diastolic_bp:
            return f"{self.systolic_bp}/{self.diastolic_bp}"
        return None
    
    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = self.height / 100
            return round(self.weight / (height_m * height_m), 1)
        return None


class Medicine(BaseModel):
    """Medicine inventory with detailed tracking"""
    DOSAGE_FORMS = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('drops', 'Drops'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('inhaler', 'Inhaler'),
        ('suppository', 'Suppository'),
        ('powder', 'Powder'),
    ]
    
    STORAGE_CONDITIONS = [
        ('room_temp', 'Room Temperature'),
        ('cool_dry', 'Cool and Dry Place'),
        ('refrigerated', 'Refrigerated (2-8°C)'),
        ('frozen', 'Frozen'),
        ('controlled_substance', 'Controlled Substance Storage'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    medicine_code = models.CharField(max_length=50, unique=True)
    
    # Clinical Information
    dosage_form = models.CharField(max_length=20, choices=DOSAGE_FORMS)
    strength = models.CharField(max_length=50)
    therapeutic_class = models.CharField(max_length=100)
    pharmacological_class = models.CharField(max_length=100, blank=True)
    
    # Regulatory Information
    manufacturer = models.CharField(max_length=100)
    distributor = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    
    # Storage and Handling
    storage_condition = models.CharField(max_length=30, choices=STORAGE_CONDITIONS)
    storage_location = models.CharField(max_length=100, blank=True)
    requires_prescription = models.BooleanField(default=True)
    is_controlled_substance = models.BooleanField(default=False)
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Stock Management
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock_level = models.PositiveIntegerField(default=10)
    maximum_stock_level = models.PositiveIntegerField(default=1000)
    reorder_level = models.PositiveIntegerField(default=20)
    
    def __str__(self):
        return f"{self.name} ({self.strength}) - {self.medicine_code}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock_level
    
    @property
    def needs_reorder(self):
        return self.current_stock <= self.reorder_level


class MedicineBatch(BaseModel):
    """Individual medicine batches for expiry tracking"""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    quantity_received = models.PositiveIntegerField()
    quantity_remaining = models.PositiveIntegerField()
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100)
    received_date = models.DateField(default=timezone.now)
    
    class Meta:
        unique_together = ['medicine', 'batch_number']
    
    def __str__(self):
        return f"{self.medicine.name} - Batch {self.batch_number}"
    
    @property
    def is_expired(self):
        from datetime import date
        return date.today() > self.expiry_date
    
    @property
    def days_to_expiry(self):
        from datetime import date
        return (self.expiry_date - date.today()).days


class Prescription(BaseModel):
    """Medicine prescriptions with detailed tracking"""
    PRESCRIPTION_STATUS = [
        ('pending', 'Pending'),
        ('partially_dispensed', 'Partially Dispensed'),
        ('fully_dispensed', 'Fully Dispensed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    prescription_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='doctor_prescriptions',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar', 'clinical_officer']}
    )
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    
    prescribed_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=PRESCRIPTION_STATUS, default='pending')
    
    # Prescription Details
    diagnosis = models.TextField()
    patient_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    allergies_noted = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    
    # Dispensing Information
    dispensed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dispensed_prescriptions',
        limit_choices_to={'role__in': ['pharmacist', 'pharmaceutical_technologist']}
    )
    dispensing_date = models.DateTimeField(null=True, blank=True)
    dispensing_notes = models.TextField(blank=True)
    
    # Financial
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_covered = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    patient_pays = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.prescription_number} - {self.patient.get_full_name()}"


class PrescriptionItem(BaseModel):
    """Individual medicine items in prescription"""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    
    # Prescription Details
    quantity_prescribed = models.PositiveIntegerField()
    quantity_dispensed = models.PositiveIntegerField(default=0)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    route_of_administration = models.CharField(max_length=50, default='Oral')
    special_instructions = models.TextField(blank=True)
    
    # Dispensing Information
    batch_dispensed = models.ForeignKey(MedicineBatch, on_delete=models.SET_NULL, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity_dispensed * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.medicine.name} - {self.quantity_prescribed} units"
    
    @property
    def is_fully_dispensed(self):
        return self.quantity_dispensed >= self.quantity_prescribed


class Laboratory(BaseModel):
    """Laboratory department"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='laboratories')
    lab_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='managed_labs',
        limit_choices_to={'role': 'lab_manager'}
    )
    location = models.CharField(max_length=100)
    phone_extension = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LabTest(BaseModel):
    """Available laboratory tests"""
    TEST_CATEGORIES = [
        ('hematology', 'Hematology'),
        ('biochemistry', 'Clinical Biochemistry'),
        ('microbiology', 'Microbiology'),
        ('parasitology', 'Parasitology'),
        ('immunology', 'Immunology'),
        ('histopathology', 'Histopathology'),
        ('cytology', 'Cytology'),
        ('molecular', 'Molecular Biology'),
        ('endocrinology', 'Endocrinology'),
        ('toxicology', 'Toxicology'),
    ]
    
    SAMPLE_TYPES = [
        ('blood', 'Blood'),
        ('serum', 'Serum'),
        ('plasma', 'Plasma'),
        ('urine', 'Urine'),
        ('stool', 'Stool'),
        ('csf', 'Cerebrospinal Fluid'),
        ('sputum', 'Sputum'),
        ('swab', 'Swab'),
        ('tissue', 'Tissue'),
        ('fluid', 'Body Fluid'),
    ]
    
    test_name = models.CharField(max_length=200)
    test_code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=TEST_CATEGORIES)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='tests')
    
    # Sample Requirements
    sample_type = models.CharField(max_length=20, choices=SAMPLE_TYPES)
    sample_volume = models.CharField(max_length=50, blank=True)
    container_type = models.CharField(max_length=100, blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Test Information
    normal_range_male = models.CharField(max_length=100, blank=True)
    normal_range_female = models.CharField(max_length=100, blank=True)
    normal_range_pediatric = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    methodology = models.CharField(max_length=100, blank=True)
    
    # Operational Details
    turnaround_time = models.PositiveIntegerField(help_text="Hours")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_urgent_available = models.BooleanField(default=True)
    urgent_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Patient Preparation
    fasting_required = models.BooleanField(default=False)
    preparation_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.test_name} ({self.test_code})"


class LabOrder(BaseModel):
    """Laboratory test orders"""
    ORDER_STATUS = [
        ('ordered', 'Test Ordered'),
        ('sample_collected', 'Sample Collected'),
        ('sample_received', 'Sample Received in Lab'),
        ('in_progress', 'Analysis in Progress'),
        ('completed', 'Analysis Completed'),
        ('verified', 'Results Verified'),
        ('reported', 'Results Reported'),
        ('cancelled', 'Order Cancelled'),
        ('rejected', 'Sample Rejected'),
    ]
    
    PRIORITY_LEVELS = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT (Immediate)'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_orders')
    ordering_doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ordered_lab_tests',
        limit_choices_to={'role__in': ['medical_officer', 'consultant', 'registrar', 'clinical_officer']}
    )
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, null=True, blank=True)
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE, null=True, blank=True)
    
    # Order Information
    order_date = models.DateTimeField(default=timezone.now)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='routine')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='ordered')
    clinical_information = models.TextField(blank=True)
    provisional_diagnosis = models.TextField(blank=True)
    
    # Sample Information
    sample_collected_date = models.DateTimeField(null=True, blank=True)
    sample_collected_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='collected_samples'
    )
    sample_received_date = models.DateTimeField(null=True, blank=True)
    sample_condition = models.TextField(blank=True)
    
    # Results Information
    analysis_start_date = models.DateTimeField(null=True, blank=True)
    analysis_completion_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_lab_orders',
        limit_choices_to={'role__in': ['lab_manager', 'lab_technologist']}
    )
    verified_date = models.DateTimeField(null=True, blank=True)
    reported_date = models.DateTimeField(null=True, blank=True)
    
    # Financial
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.order_number} - {self.patient.get_full_name()}"


class LabResult(BaseModel):
    """Individual lab test results"""
    RESULT_STATUS = [
        ('pending', 'Result Pending'),
        ('preliminary', 'Preliminary Result'),
        ('final', 'Final Result'),
        ('amended', 'Amended Result'),
        ('cancelled', 'Result Cancelled'),
    ]
    
    lab_order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    
    # Result Information
    result_value = models.TextField()
    reference_range = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=RESULT_STATUS, default='pending')
    
    # Flags and Interpretation
    is_abnormal = models.BooleanField(default=False)
    abnormal_flag = models.CharField(max_length=10, blank=True, help_text="H, L, HH, LL, etc.")
    interpretation = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    
    # Technical Information
    analyzed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='analyzed_results',
        limit_choices_to={'role__in': ['lab_technologist', 'lab_technician']}
    )
    analysis_date = models.DateTimeField(null=True, blank=True)
    equipment_used = models.CharField(max_length=100, blank=True)
    
    # Quality Control
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_results',
        limit_choices_to={'role__in': ['lab_manager', 'lab_technologist']}
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.test.test_name}: {self.result_value}"


class Bill(BaseModel):
    """Comprehensive patient billing"""
    BILL_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Payment'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('waived', 'Fee Waived'),
    ]
    
    BILL_TYPES = [
        ('consultation', 'Consultation Bill'),
        ('admission', 'Admission Bill'),
        ('pharmacy', 'Pharmacy Bill'),
        ('laboratory', 'Laboratory Bill'),
        ('radiology', 'Radiology Bill'),
        ('procedure', 'Procedure Bill'),
        ('comprehensive', 'Comprehensive Bill'),
    ]
    
    bill_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Bill Information
    bill_date = models.DateTimeField(default=timezone.now)
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=BILL_STATUS, default='pending')
    
    # Financial Summary
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Insurance Information
    insurance_claim_number = models.CharField(max_length=50, blank=True)
    insurance_approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Administrative
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_bills')
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_bills'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.bill_number} - {self.patient.get_full_name()}"
    
    @property
    def balance_amount(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        from datetime import date
        return self.status in ['pending', 'partially_paid'] and date.today() > self.due_date


class BillItem(BaseModel):
    """Individual items in patient bills"""
    ITEM_CATEGORIES = [
        ('consultation', 'Doctor Consultation'),
        ('bed_charges', 'Bed Charges'),
        ('nursing_care', 'Nursing Care'),
        ('medicine', 'Medicine'),
        ('laboratory', 'Laboratory Test'),
        ('radiology', 'Radiology'),
        ('procedure', 'Medical Procedure'),
        ('surgery', 'Surgery'),
        ('therapy', 'Therapy Session'),
        ('supplies', 'Medical Supplies'),
        ('ambulance', 'Ambulance Service'),
        ('other', 'Other Charges'),
    ]
    
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    
    # Item Details
    item_code = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ITEM_CATEGORIES)
    service_date = models.DateField()
    
    # Quantity and Pricing
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    # unit_price = models.