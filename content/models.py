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

    NGO_ROLES = [
        ('admin', 'Administrator'),
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

# ----------------- Project -----------------
class Project(TimeStampedModel):
    DRAFT = 'draft'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    STATUS_CHOICES = [(DRAFT, 'Draft'), (ACTIVE, 'Active'), (COMPLETED, 'Completed')]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=ACTIVE)
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

# ----------------- MembershipPayment -----------------
def current_year():
    return timezone.now().year

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
    year = models.PositiveIntegerField(default=current_year)  # migration-safe default
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

    @property
    def total_paid_this_year(self):
        return MembershipPayment.objects.filter(user=self.user, year=self.year, status='verified').aggregate(total=models.Sum('amount_paid'))['total'] or 0

    @property
    def balance(self):
        return max(ANNUAL_FEE - self.total_paid_this_year, 0)

# ----------------- MemberProfile -----------------
class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    control_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    control_number_created = models.DateTimeField(blank=True, null=True)
    is_active_member = models.BooleanField(default=False)
    last_payment_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    def generate_control_number(self):
        if not self.control_number:
            unique_part = str(uuid.uuid4().int)[:8]
            self.control_number = f"CRDB-{unique_part}"
            self.control_number_created = timezone.now()
            self.save(update_fields=['control_number', 'control_number_created'])

    def update_membership_status(self):
        current_year_val = timezone.now().year
        verified_total = MembershipPayment.objects.filter(user=self.user, status='verified', year=current_year_val).aggregate(total=models.Sum('amount_paid'))['total'] or 0
        if verified_total >= ANNUAL_FEE:
            latest_payment = MembershipPayment.objects.filter(user=self.user, status='verified').order_by('-date_paid').first()
            if latest_payment:
                self.last_payment_date = latest_payment.date_paid
                self.expiry_date = self.last_payment_date + timedelta(days=365)
                self.is_active_member = True
        else:
            self.is_active_member = False
        self.save(update_fields=['last_payment_date', 'expiry_date', 'is_active_member'])

# ----------------- Suggestion -----------------
class Suggestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="suggestions")
    message = models.TextField(verbose_name="Your Suggestion / Opinion")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Suggestion from {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
