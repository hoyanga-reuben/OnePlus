from django.contrib import admin
from .models import Category, Tag, Post, Project, ProjectDocument
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils import timezone

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'profile_image', 'ngo_role')}),
    )
    list_display = ('username', 'email', 'ngo_role', 'is_staff', 'is_active')
    list_filter = ('ngo_role', 'is_staff', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'category', 'is_published', 'published_at')
    list_filter = ('type', 'category', 'is_published', 'tags')
    search_fields = ('title', 'summary', 'body')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'published_at', 'created_at')
    list_filter = ('project',)
    search_fields = ('title', 'content')



# content/admin.py
from django.contrib import admin
from .models import MembershipPayment, MemberProfile

@admin.register(MembershipPayment)
class MembershipPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_paid', 'year', 'status', 'date_submitted', 'verified_by', 'verified_at')
    list_filter = ('status', 'year', 'payment_method')
    search_fields = ('user__username', 'reference')
    actions = ['mark_verified']

    def mark_verified(self, request, queryset):
        for p in queryset.filter(status='pending'):
            p.status = 'verified'
            p.verified_by = request.user
            p.verified_at = timezone.now()
            if not p.date_paid:
                p.date_paid = p.verified_at.date()
            p.save()
            # update profile
            profile, _ = MemberProfile.objects.get_or_create(user=p.user)
            profile.last_payment_date = p.date_paid
            profile.update_membership_status()
        self.message_user(request, "Selected payments have been verified.")
    mark_verified.short_description = "Mark selected payments as verified"
