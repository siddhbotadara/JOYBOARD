from django.contrib import admin
from .models import PlayerRecord, GameSession, UserProfile, BannedUser

@admin.register(PlayerRecord)
class PlayerRecordAdmin(admin.ModelAdmin):
    list_display = ('username', 'level_completed', 'time_taken', 'input_used')
    search_fields = ('username', 'input_used')
    list_filter = ('level_completed', 'input_used')

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('username', 'level_completed', 'time_taken')
    search_fields = ('username',)
    list_filter = ('level_completed',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'description',)
    search_fields = ('user',)

@admin.register(BannedUser)
class BannedUserAdmin(admin.ModelAdmin):
    list_display = ('username','email',)
    search_fields = ('username',)

# Register your models here.
admin.site.site_header = "JoyBoard Admin Panel"
admin.site.site_title = "JoyBoard Admin"
admin.site.index_title = "Welcome to JoyBoard Mr. Admin"