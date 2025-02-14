from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import MeditationTrack, TopContent, Course, Workshop, Group, Event, FavoriteMeditation
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import transaction

class BaseListView(ListView):
    """
    Базовий клас для всіх списків з пагінацією та пошуком.
    """
    paginate_by = 12
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset.order_by(*self.get_ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class BaseDetailView(DetailView):
    """
    Базовий клас для детального перегляду контенту.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_items'] = self.model.objects.exclude(id=self.object.id)[:3]
        return context

class MeditationListView(BaseListView):
    """
    Відображення списку медитацій з можливістю пошуку та фільтрації.
    """
    model = MeditationTrack
    template_name = 'meditation/meditation_list.html'
    context_object_name = 'tracks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            favorite_tracks = set(
                FavoriteMeditation.objects.filter(user=self.request.user)
                .values_list('meditation_id', flat=True)
            )
            context['favorite_tracks'] = favorite_tracks
        now = timezone.now()
        context.update({
            'top_content': TopContent.objects.filter(featured=True)[:5],
            'courses': Course.objects.all()[:5],
            'workshops': Workshop.objects.filter(date__gte=now)[:5],
            'groups': Group.objects.all()[:5],
            'events': Event.objects.filter(date__gte=now)[:5]
        })
        return context

class MeditationDetailView(BaseDetailView):
    """
    Детальне відображення медитації.
    """
    model = MeditationTrack
    template_name = 'meditation/meditation_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_tracks'] = MeditationTrack.objects.filter(
            duration=self.object.duration
        ).exclude(id=self.object.id)[:3]
        return context

class TopContentListView(BaseListView):
    """
    Відображення списку рекомендованого контенту.
    """
    model = TopContent
    template_name = 'meditation/top_content_list.html'
    context_object_name = 'content'

class TopContentDetailView(BaseDetailView):
    """
    Детальне відображення рекомендованого контенту.
    """
    model = TopContent
    template_name = 'meditation/top_content_detail.html'

class CourseListView(BaseListView):
    """
    Відображення списку курсів.
    """
    model = Course
    template_name = 'meditation/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(BaseDetailView):
    """
    Детальне відображення курсу.
    """
    model = Course
    template_name = 'meditation/course_detail.html'

class WorkshopListView(BaseListView):
    """
    Відображення списку воркшопів.
    """
    model = Workshop
    template_name = 'meditation/workshop_list.html'
    context_object_name = 'workshops'
    ordering = ['date']

class WorkshopDetailView(BaseDetailView):
    """
    Детальне відображення воркшопу.
    """
    model = Workshop
    template_name = 'meditation/workshop_detail.html'

class GroupListView(BaseListView):
    """
    Відображення списку груп.
    """
    model = Group
    template_name = 'meditation/group_list.html'
    context_object_name = 'groups'

class GroupDetailView(BaseDetailView):
    """
    Детальне відображення групи.
    """
    model = Group
    template_name = 'meditation/group_detail.html'

class EventListView(BaseListView):
    """
    Відображення списку подій.
    """
    model = Event
    template_name = 'meditation/event_list.html'
    context_object_name = 'events'
    ordering = ['date']

class EventDetailView(BaseDetailView):
    """
    Детальне відображення події.
    """
    model = Event
    template_name = 'meditation/event_detail.html'

class BaseContentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Базовий клас для створення контенту.
    """
    template_name = 'meditation/form_base.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user.get_full_name() or self.request.user.username
        return super().form_valid(form)

class BaseContentUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    Базовий клас для оновлення контенту.
    """
    template_name = 'meditation/form_base.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user.get_full_name() or self.request.user.is_staff

class MeditationTrackCreate(BaseContentCreateView):
    """
    Створення нової медитації.
    """
    model = MeditationTrack
    fields = ['title', 'description', 'duration', 'image', 'audio_file']
    success_url = reverse_lazy('meditation:track_list')
    success_message = _('Meditation track was created successfully')

class MeditationTrackUpdate(BaseContentUpdateView):
    """
    Оновлення існуючої медитації.
    """
    model = MeditationTrack
    fields = ['title', 'description', 'duration', 'image', 'audio_file']
    success_url = reverse_lazy('meditation:track_list')
    success_message = _('Meditation track was updated successfully')

class CourseCreate(BaseContentCreateView):
    """
    Створення нового курсу.
    """
    model = Course
    fields = ['title', 'description', 'duration_weeks', 'price', 'image', 'video_url']
    success_url = reverse_lazy('meditation:course_list')
    success_message = _('Course was created successfully')

class CourseUpdate(BaseContentUpdateView):
    """
    Оновлення існуючого курсу.
    """
    model = Course
    fields = ['title', 'description', 'duration_weeks', 'price', 'image', 'video_url']
    success_url = reverse_lazy('meditation:course_list')
    success_message = _('Course was updated successfully')

class WorkshopCreate(BaseContentCreateView):
    """
    Створення нового воркшопу.
    """
    model = Workshop
    fields = ['title', 'description', 'date', 'location', 'price', 'max_participants', 'image', 'video_url']
    success_url = reverse_lazy('meditation:workshop_list')
    success_message = _('Workshop was created successfully')

class WorkshopUpdate(BaseContentUpdateView):
    """
    Оновлення існуючого воркшопу.
    """
    model = Workshop
    fields = ['title', 'description', 'date', 'location', 'price', 'max_participants', 'image', 'video_url']
    success_url = reverse_lazy('meditation:workshop_list')
    success_message = _('Workshop was updated successfully')

class GroupCreate(BaseContentCreateView):
    """
    Створення нової групи.
    """
    model = Group
    fields = ['title', 'description', 'is_private', 'image']
    success_url = reverse_lazy('meditation:group_list')
    success_message = _('Group was created successfully')

class GroupUpdate(BaseContentUpdateView):
    """
    Оновлення існуючої групи.
    """
    model = Group
    fields = ['title', 'description', 'is_private', 'image']
    success_url = reverse_lazy('meditation:group_list')
    success_message = _('Group was updated successfully')

class EventCreate(BaseContentCreateView):
    """
    Створення нової події.
    """
    model = Event
    fields = ['title', 'description', 'date', 'location', 'is_online', 'max_participants', 'image']
    success_url = reverse_lazy('meditation:event_list')
    success_message = _('Event was created successfully')

class EventUpdate(BaseContentUpdateView):
    """
    Оновлення існуючої події.
    """
    model = Event
    fields = ['title', 'description', 'date', 'location', 'is_online', 'max_participants', 'image']
    success_url = reverse_lazy('meditation:event_list')
    success_message = _('Event was updated successfully')

def login_view(request):
    """
    Представлення для входу користувача з додатковою валідацією.
    """
    if request.user.is_authenticated:
        return redirect('meditation:home')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('Successfully logged in!'))
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else 'meditation:home')
            else:
                messages.error(request, _('Invalid username or password.'))
    else:
        form = CustomAuthenticationForm()
    return render(request, 'meditation/login.html', {'form': form})

def register_view(request):
    """
    Представлення для реєстрації нового користувача з валідацією форм.
    """
    if request.user.is_authenticated:
        return redirect('meditation:home')
        
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save()
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    
                    login(request, user)
                    messages.success(request, _('Successfully registered!'))
                    return redirect('meditation:home')
            except Exception as e:
                messages.error(request, _('Registration failed. Please try again.'))
                return redirect('meditation:register')
        else:
            if user_form.errors:
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            if profile_form.errors:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'meditation/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def logout_view(request):
    """
    Обробляє вихід користувача з системи.
    Виконує logout та перенаправляє на головну сторінку.
    """
    if request.method == 'POST':
        logout(request)
        return redirect('meditation:home')
    return HttpResponseNotAllowed(['POST'])

class RulesView(TemplateView):
    """
    Відображення сторінки правил користування.
    """
    template_name = 'meditation/rules.html'

@login_required
def toggle_favorite(request, track_id):
    """
    Додає або видаляє медитацію з улюблених
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
        
    try:
        track = MeditationTrack.objects.get(id=track_id)
        favorite = FavoriteMeditation.objects.filter(
            user=request.user,
            meditation=track
        ).first()
        
        if favorite:
            favorite.delete()
            is_favorite = False
        else:
            FavoriteMeditation.objects.create(
                user=request.user,
                meditation=track
            )
            is_favorite = True
            
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite
        })
    except MeditationTrack.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': _('Meditation track not found')
        }, status=404)

class FavoriteTracksView(LoginRequiredMixin, ListView):
    """
    Відображення списку улюблених медитацій користувача.
    """
    model = MeditationTrack
    template_name = 'meditation/favorite_tracks.html'
    context_object_name = 'tracks'
    
    def get_queryset(self):
        return MeditationTrack.objects.filter(
            favorited_by__user=self.request.user
        ).order_by('-favorited_by__added_at')
