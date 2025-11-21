from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import EmailChangeView
from .views import DeleteAccountView
from .views import UserListView,MeetingListView, MeetingDetailView, MeetingCreateView, MeetingUpdateView, MeetingDeleteView


urlpatterns = [
    # Blog
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/add/', views.PostCreateView.as_view(), name='blog_add'),
    path('blog/<int:pk>/edit/', views.PostUpdateView.as_view(), name='blog_edit'),
    path('blog/<int:pk>/delete/', views.PostDeleteView.as_view(), name='blog_delete'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),

    # News
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),

    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/add/', views.ProjectCreateView.as_view(), name='project_add'),
    # urls.py
   path('project/<slug:slug>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
   path('project/<slug:slug>/delete/',views.ProjectDeleteView.as_view(), name='project_delete'),


    # Payments
    path('payments/<int:payment_pk>/verify/', views.verify_payment, name='verify_payment'),
    path('payments/', views.payments_list, name='payment_list'),

    # Authentication
    path('signup/', views.SignupView.as_view(), name='account_signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='account_logout'),

    # Dashboard & profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('volunteers/', views.VolunteerListView.as_view(), name='volunteer_list'),
    path("email/change/", EmailChangeView.as_view(), name="email_change"),
    path("account/delete/", DeleteAccountView.as_view(), name="delete_account"),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('suggestions/', views.suggestion_list, name='suggestion_list'),
    path('members/all/', UserListView.as_view(), name='user_list'),
    

    # URLs za Mikutano
    path('meetings/', MeetingListView.as_view(), name='meeting_list'),
    path('meetings/create/', MeetingCreateView.as_view(), name='meeting_create'),
    path('meetings/<int:pk>/', MeetingDetailView.as_view(), name='meeting_detail'),
    path('meetings/<int:pk>/edit/', MeetingUpdateView.as_view(), name='meeting_update'),
    path('meetings/<int:pk>/delete/', MeetingDeleteView.as_view(), name='meeting_delete'),
]
