from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import ExtractYear
from django.db.models import Sum
from decimal import Decimal
import uuid
ANNUAL_FEE = 50000  # membership annual fee

# ----------------- Custom User -----------------
class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser.
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now, blank=True)

    NGO_ROLES = [
        ('admin', 'Administrator'),
        ('accountant', 'Accountant'),
        ('manager', 'Project Manager'),
        ('staff', 'Staff'),
        ('volunteer', 'Volunteer'),
        ('member', 'Member'),
    ]
    ngo_role = models.CharField(max_length=50, choices=NGO_ROLES, default='member')

    # Fix related_name clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username or self.email

# ----------------- Timestamped Abstract Model -----------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ----------------- Category -----------------
class Category(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:90]
            slug_candidate = base_slug
            counter = 1
            while Category.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ----------------- Tag -----------------
class Tag(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:50]
            slug_candidate = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ----------------- Post -----------------
class Post(TimeStampedModel):
    BLOG = 'blog'
    NEWS = 'news'
    TYPE_CHOICES = [(BLOG, 'Blog'), (NEWS, 'News')]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=BLOG)
    summary = models.TextField(max_length=300, blank=True)
    body = CKEditor5Field('Body', config_name='default', blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)
    cover_image = ProcessedImageField(
        upload_to='posts/',
        processors=[ResizeToFill(720, 480)],
        format='JPEG',
        options={'quality': 80},
        blank=True
    )
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            slug_candidate = base_slug
            counter = 1
            while Post.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.type == Post.NEWS:
            return reverse('news_detail', args=[self.slug])
        return reverse('blog_detail', args=[self.slug])




# Defines the available status options for a project using TextChoices
class ProjectStatus(models.TextChoices):
    ONGOING = 'OG', 'Ongoing'
    COMPLETED = 'CP', 'Completed'
    PLANNED = 'PL', 'Planned'
    SUSPENDED = 'SS', 'Suspended'
# ----------------- Project -----------------
class Project(TimeStampedModel):

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    # Status field now references the new ProjectStatus choices
    status = models.CharField(
        max_length=2, # Reduced length as we are using 2-char codes (OG, CP, PL, SS)
        choices=ProjectStatus.choices, 
        default=ProjectStatus.ONGOING, 
        verbose_name="Project Status"
    )
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    hero_image = ProcessedImageField(
        upload_to='projects/',
        processors=[ResizeToFill(1280, 720)],
        format='JPEG',
        options={'quality': 80},
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            slug_candidate = base_slug
            counter = 1
            while Project.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[self.slug])
# ----------------- ProjectDocument -----------------
class ProjectDocument(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to='project_docs/', blank=True)
    content = CKEditor5Field('Content', config_name='default', blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    



    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"{self.project.title} — {self.title}"

# ----------------- Volunteer -----------------
class Volunteer(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

def current_year():
    return timezone.now().year

# CONSTANT YA ADA YA MWAKA
# Tumetumia Decimal('50000.00') badala ya 50000.00 (float) ili kuendana na DecimalField ya malipo.
ANNUAL_FEE = Decimal('50000.00') # TZS 50,000
MINIMUM_INSTALLMENT_FEE = Decimal('12500.00') # TZS 50,000 / 4
DAYS_PER_INSTALLMENT = 90 # Miezi 3 kwa kila awamu

# ----------------- MembershipPayment -----------------
class MembershipPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_paid = models.DateField(blank=True, null=True)
    year = models.PositiveIntegerField(default=current_year)
    payment_method = models.CharField(max_length=50, default='bank_transfer')
    reference = models.CharField(max_length=120, blank=True, null=True)
    proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_submitted']

    def __str__(self):
        return f"{self.user.username} - {self.year} - {self.amount_paid} ({self.status})"

# content/models.py (Sehemu ya MemberProfile na Functions Zake)



# ----------------- MemberProfile -----------------
class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    control_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    control_number_created = models.DateTimeField(blank=True, null=True)
    # is_active_member FIELD IMEONDOLEWA KABISA
    last_payment_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True) # Hutumika kuweka status

    # ------------------- Financial Properties -------------------
    @property
    def total_verified_paid_this_year(self):
        """Kiasi chote kilichothibitishwa kulipwa kwa mwaka wa sasa."""
        current_year_val = timezone.now().year
        total = MembershipPayment.objects.filter(
            user=self.user, 
            status='verified', 
            year=current_year_val
        ).aggregate(total=Sum('amount_paid'))['total']
        
        return total if total is not None else Decimal('0.00') 
    
    @property
    def has_pending_payments(self): 
        """Angalia kama kuna malipo ya mwaka huu yenye status 'pending'."""
        current_year_val = timezone.now().year
        return MembershipPayment.objects.filter(
            user=self.user, 
            status='pending', 
            year=current_year_val
        ).exists()
    
    @property
    def current_balance(self):
        """Salio anayodaiwa (positive) au ziada (negative) dhidi ya ANNUAL_FEE."""
        return ANNUAL_FEE - self.total_verified_paid_this_year
        
    @property
    def is_overpaid(self):
        """Angalia kama malipo yaliyothibitishwa yanazidi ANNUAL_FEE."""
        return self.current_balance < Decimal('0.00')

    @property
    def is_active_member(self):
        """Hucheki kama tarehe ya uanachama haijaisha (Hii ndio getter)."""
        # Active: Tarehe ya kumalizika ni kubwa kuliko au sawa na leo
        return self.expiry_date and self.expiry_date >= timezone.now().date()
        
    @property
    def current_status_label(self):
        """Rudiisha label ya hadhi ya uanachama kulingana na malipo na expiry_date."""
        if self.is_active_member:
            if self.total_verified_paid_this_year >= ANNUAL_FEE:
                 return "Active (Full Fee Paid)"
            else:
                 # Hii inatokea kwa member wa awamu ambaye siku zake bado hazijaisha
                 return "Active (Partial/Installment Paid)"
        
        elif self.has_pending_payments: 
            return "Pending Verification"
        
        elif self.total_verified_paid_this_year > Decimal('0.00'):
            # Amelipa awamu lakini uanachama umeisha
            return f"Expired (Balance: TZS {self.current_balance:,.2f})"
        else:
            return "Inactive (Fee Pending)" 
            
    # ------------------- Utility Methods -------------------
    def generate_control_number(self):
        # ... (logic ya generate_control_number inabaki jinsi ilivyo) ...
        if not self.control_number:
            unique_part = str(uuid.uuid4().int)[:10] 
            self.control_number = f"ONEPLUS-{unique_part}" 
            self.control_number_created = timezone.now()
            self.save(update_fields=['control_number', 'control_number_created'])

    def update_membership_status(self):
        """
        Hurekebisha expiry_date na last_payment_date.
        HAWEKI (SET) is_active_member kwa sababu ni property.
        """
        
        verified_total = self.total_verified_paid_this_year
        
        # 1. Pata tarehe ya malipo ya mwisho yaliyothibitishwa (kwa hali zote)
        latest_payment = MembershipPayment.objects.filter(
            user=self.user, 
            status='verified'
        ).order_by('-date_paid').first()
        
        if latest_payment and latest_payment.date_paid:
            self.last_payment_date = latest_payment.date_paid
        else:
            self.last_payment_date = None

        # 2. Mantiki ya Ada Kamili (Full Fee)
        if verified_total >= ANNUAL_FEE:
            
            # Tafuta tarehe ya kuanzia kuongeza muda (ya mwisho iliyoisha au leo)
            current_expiry = self.expiry_date
            today = timezone.now().date()
            
            if current_expiry and current_expiry > today:
                start_date = current_expiry
            else:
                start_date = today

            self.expiry_date = start_date + timedelta(days=365)
            
        else:
            # Mantiki ya Malipo ya Awamu (Partial Payment)
            # TUNAIACHA expiry_date jinsi ilivyowekwa na Admin kwenye verify_payment view.
            # Ikiwa malipo ni < 50,000, `expiry_date` itajumuisha siku za awamu (90/180/270).
            # Ikiwa hakuna malipo, itaendelea kuwa None.
            pass


        # 3. Hifadhi (save) mabadiliko
        # is_active_member imeondolewa kutoka update_fields
        self.save(update_fields=['last_payment_date', 'expiry_date']) 
        
    def __str__(self):
        return f"Profile for {self.user.username}"


# ----------------- Suggestion -----------------
class Suggestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="suggestions")
    subject = models.CharField(max_length=255, verbose_name="Subject / Title of Suggestion", default="No Subject Provided")
    message = models.TextField(verbose_name="Your Suggestion / Opinion")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Suggestion from {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    



# content/models.py (Ongeza hii baada ya Suggestion Model)

# ----------------- Meeting -----------------
class Meeting(TimeStampedModel):
    title = models.CharField(max_length=200)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='organized_meetings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    # Hapa ndio unaweza kuweka link ya Google Meet, Zoom, au Jitsi
    conference_link = models.URLField(max_length=200, blank=True, null=True) 
    
    # Washiriki wote wanaweza kuwa members wote au tuwalike
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='meetings_attended', blank=True)
    
    class Meta:
        ordering = ['start_time']
        verbose_name_plural = "Meetings"

    def __str__(self):
        return f"{self.title} @ {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_current(self):
        """Hurejesha True ikiwa mkutano unafanyika sasa (LIVE)."""
        now = timezone.now()
        return self.start_time <= now and self.end_time >= now

    @property
    def is_past(self):
        """Hurejesha True ikiwa mkutano umepita."""
        return self.end_time < timezone.now()

    @property
    def is_today(self):
        """Hurejesha True ikiwa mkutano ni leo."""
        return self.start_time.date() == timezone.localdate()

    @property
    def is_tomorrow(self):
        """Hurejesha True ikiwa mkutano ni kesho."""
        return self.start_time.date() == timezone.localdate() + timezone.timedelta(days=1)

    @property
    def is_current(self):
        return self.start_time <= timezone.now() < self.end_time

    @property
    def is_past(self):
        return timezone.now() >= self.end_time
