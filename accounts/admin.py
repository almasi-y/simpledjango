from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'get_user_type', 'get_is_verified')
    list_filter = ('is_active', 'is_staff', 'userprofile__user_type', 'userprofile__is_verified')
    
    def get_user_type(self, obj):
        return obj.userprofile.get_user_type_display()
    get_user_type.short_description = 'User Type'
    
    def get_is_verified(self, obj):
        return obj.userprofile.is_verified
    get_is_verified.short_description = 'Verified'
    get_is_verified.boolean = True


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'is_verified', 'phone_number', 'created_at')
    list_filter = ('user_type', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('verification_token', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address', 'profile_picture')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
