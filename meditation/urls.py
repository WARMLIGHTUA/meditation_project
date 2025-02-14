from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'meditation'

urlpatterns = [
    path('', views.MeditationListView.as_view(), name='home'),
    
    # Meditation Tracks
    path('tracks/', views.MeditationListView.as_view(template_name='meditation/track_list.html'), name='track_list'),
    path('track/<int:pk>/', views.MeditationDetailView.as_view(), name='track_detail'),
    path('track/create/', views.MeditationTrackCreate.as_view(), name='track_create'),
    path('track/<int:pk>/update/', views.MeditationTrackUpdate.as_view(), name='track_update'),
    
    # Favorite meditation
    path('track/<int:track_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.FavoriteTracksView.as_view(), name='favorite_tracks'),
    
    # Rules page
    path('rules/', views.RulesView.as_view(), name='rules'),
    
    # Top Content
    path('top/', views.TopContentListView.as_view(), name='top_list'),
    path('top/<int:pk>/', views.TopContentDetailView.as_view(), name='top_detail'),
    
    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', views.CourseCreate.as_view(), name='course_create'),
    path('courses/<int:pk>/update/', views.CourseUpdate.as_view(), name='course_update'),
    
    # Workshops
    path('workshops/', views.WorkshopListView.as_view(), name='workshop_list'),
    path('workshops/<int:pk>/', views.WorkshopDetailView.as_view(), name='workshop_detail'),
    path('workshops/create/', views.WorkshopCreate.as_view(), name='workshop_create'),
    path('workshops/<int:pk>/update/', views.WorkshopUpdate.as_view(), name='workshop_update'),
    
    # Groups
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/create/', views.GroupCreate.as_view(), name='group_create'),
    path('groups/<int:pk>/update/', views.GroupUpdate.as_view(), name='group_update'),
    
    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/create/', views.EventCreate.as_view(), name='event_create'),
    path('events/<int:pk>/update/', views.EventUpdate.as_view(), name='event_update'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
] 