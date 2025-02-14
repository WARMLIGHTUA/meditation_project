from django.contrib import admin
from .models import MeditationTrack, TopContent, Course, Workshop, Group, Event, PageBackground

@admin.register(MeditationTrack)
class MeditationTrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'rating', 'author', 'created_at')
    search_fields = ('title', 'description', 'author')
    list_filter = ('created_at', 'rating')

@admin.register(TopContent)
class TopContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'featured', 'rating', 'author', 'created_at')
    search_fields = ('title', 'description', 'author')
    list_filter = ('featured', 'created_at', 'rating')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_weeks', 'price', 'rating', 'author', 'created_at')
    search_fields = ('title', 'description', 'author')
    list_filter = ('created_at', 'rating', 'price')

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'price', 'max_participants', 'author')
    search_fields = ('title', 'description', 'location', 'author')
    list_filter = ('date', 'price', 'max_participants')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'members_count', 'is_private', 'rating', 'author')
    search_fields = ('title', 'description', 'author')
    list_filter = ('is_private', 'created_at', 'rating')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_online', 'max_participants', 'author')
    search_fields = ('title', 'description', 'location', 'author')
    list_filter = ('is_online', 'date', 'max_participants')

@admin.register(PageBackground)
class PageBackgroundAdmin(admin.ModelAdmin):
    list_display = ('page', 'theme', 'background_color', 'background_opacity')
    list_filter = ('page', 'theme')
    fieldsets = (
        (None, {
            'fields': ('page', 'theme')
        }),
        ('Background Settings', {
            'fields': ('background_image', 'background_video', 'background_color', 'background_opacity'),
            'classes': ('wide',)
        })
    )
