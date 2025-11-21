from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone # <-- Added this import
from django.db.models import Q # Import Q for complex lookups

from .models import (
    CustomUser, TimeStampedModel, Category, Tag, Post, Project, 
    ProjectStatus, ProjectDocument, Volunteer, MembershipPayment, 
    MemberProfile, Suggestion
)

# ----------------- User and Profile Admin -----------------

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser."""
    fieldsets = UserAdmin.fieldsets + (
        ('NGO Information', {'fields': ('phone_number', 'profile_image', 'ngo_role',)}),
    )
    list_display = UserAdmin.list_display + ('ngo_role',)
    list_filter = UserAdmin.list_filter + ('ngo_role',)

# content/admin.py


# --- 1. CUSTOM LIST FILTER KWA AJILI YA is_active_member ---
class MemberActiveFilter(admin.SimpleListFilter):
    """
    Custom filter inayoangalia hadhi ya uanachama kwa kutumia expiry_date
    badala ya field ya is_active_member.
    """
    title = 'Membership Status'
    parameter_name = 'membership_status'

    def lookups(self, request, model_admin):
        # Orodha ya chaguo za filter
        return [
            ('active', 'Active (Not Expired)'),
            ('expired', 'Expired'),
            ('partial_paid_expired', 'Expired but Partially Paid'),
        ]

    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'active':
            # Active = expiry_date ipo NA haijaisha
            return queryset.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today
            )
        
        if self.value() == 'expired':
            # Expired = expiry_date ni None au imepita NA hajalipa chochote mwaka huu
            return queryset.filter(
                Q(expiry_date__isnull=True) | Q(expiry_date__lt=today),
                user__payments__status='verified'
            ).exclude(
                user__payments__status='verified',
                user__payments__amount_paid__gt=0,
                user__payments__year=timezone.now().year
            ).distinct()
            
        if self.value() == 'partial_paid_expired':
            # Expired but Paid Partially = expiry_date imepita LAKINI amefanya malipo yaliyothibitishwa mwaka huu.
            # Hawa ndio wanaotakiwa kuwasiliana na admin.
            from .models import ANNUAL_FEE
            
            return queryset.filter(
                Q(expiry_date__isnull=True) | Q(expiry_date__lt=today),
                user__payments__status='verified',
                user__payments__amount_paid__gt=0,
                user__payments__year=timezone.now().year
            ).exclude(
                # Ondoa wale ambao malipo yao yamefika au kuzidi ANNUAL_FEE
                user__memberprofile__total_verified_paid_this_year__gte=ANNUAL_FEE 
            ).distinct()
            
        return queryset

# --- 2. KUREKEBISHA MEMBERPROFILEADMIN ---
@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    """Admin configuration for MemberProfile."""
    list_display = (
        'user', 
        'is_active_member',  # Hii bado inaweza kuonyeshwa kwa sababu ni @property
        'last_payment_date', 
        'expiry_date', 
        'control_number'
    )
    search_fields = ('user__username', 'user__email', 'control_number')
    
    # Kosa lilitoka hapa: Tumebadilisha 'is_active_member' kuwa CUSTOM FILTER
    list_filter = [
        MemberActiveFilter, # TUMIA CLASS MPYA HII
    ] 
    
    readonly_fields = ('control_number', 'control_number_created')
    actions = ['update_membership_status']

    def update_membership_status(self, request, queryset):
        for profile in queryset:
            # Hapa bado tunatumia method ya models.py ambayo tumeirekebisha
            profile.update_membership_status() 
        self.message_user(request, "Selected membership statuses have been updated.")
    update_membership_status.short_description = "Update selected member's payment status"
# ----------------- Content Admin -----------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category."""
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag."""
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Posts."""
    list_display = ('title', 'type', 'is_published', 'category', 'published_at')
    list_filter = ('type', 'is_published', 'category', 'tags')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    # Use filter_horizontal for ManyToMany fields (Tags)
    filter_horizontal = ('tags',)


# ----------------- Project Admin (UPDATED) -----------------

class ProjectDocumentInline(admin.TabularInline):
    """Allows ProjectDocuments to be managed directly within the Project admin."""
    model = ProjectDocument
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model using the new ProjectStatus."""
    list_display = ('title', 'status', 'start_date', 'end_date', 'created_at')
    
    # Crucial update: Allows easy filtering by the new ProjectStatus
    list_filter = ('status',)
    
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    # Defines the fields in the form and ensures 'status' is visible
    fieldsets = (
        (None, {
            'fields': (('title', 'slug'), 'description', 'hero_image')
        }),
        ('Schedule and Status', {
            # Display status field clearly in the admin form
            'fields': ('status', ('start_date', 'end_date'))
        }),
    )
    inlines = [ProjectDocumentInline]


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    """Admin configuration for Volunteer opportunities."""
    list_display = ('name', 'start_date', 'end_date')


# ----------------- Financial Admin -----------------

@admin.register(MembershipPayment)
class MembershipPaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Membership Payments."""
    list_display = (
        'user', 'year', 'amount_paid', 'status', 'date_paid', 'verified_by'
    )
    list_filter = ('status', 'year', 'payment_method')
    search_fields = ('user__username', 'reference')
    date_hierarchy = 'date_submitted'
    actions = ['mark_verified']

    def mark_verified(self, request, queryset):
        """Action to mark selected payments as 'verified'."""
        verified_count = queryset.filter(status='verified').count()
        if verified_count > 0:
            self.message_user(request, f"Skipped {verified_count} payments that were already verified.", level='warning')
        
        # Filter for payments that are not yet verified
        to_verify = queryset.exclude(status='verified')
        
        # Update the status, verified_by, and verified_at fields
        updated_count = to_verify.update(
            status='verified',
            verified_by=request.user,
            verified_at=timezone.now(),
            date_paid=timezone.now().date() # Assume date_paid is now for verification
        )
        
        # After updating, trigger the membership status update for affected users
        user_ids = to_verify.values_list('user', flat=True).distinct()
        for user_id in user_ids:
            try:
                profile = MemberProfile.objects.get(user_id=user_id)
                profile.update_membership_status()
            except MemberProfile.DoesNotExist:
                # Handle case where profile might not exist (optional)
                pass 

        self.message_user(request, f"Successfully verified {updated_count} payments and updated associated member profiles.")
    
    mark_verified.short_description = "Mark selected payments as Verified"


# ----------------- Suggestions Admin -----------------

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    """Admin configuration for user suggestions."""
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'