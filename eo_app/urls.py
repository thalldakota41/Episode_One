from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('about/', views.about, name='about'),
    path('comment/', views.comment, name='comment'),
    path('comment_submit/', views.comment_submit, name='comment_submit'),
    path('creator/<int:id>/', views.creator_page, name='creator'),
    path('show_page/<int:id>/', views.show_page, name='show_page'),
    path('staff_favorites/', views.get_staff_favorites, name='staff_favorites'),
    path('all_staff_favorites/', views.all_staff_favorites, name='all_staff_favorites'),
    path('influential_shows/', views.rest_of_influential_shows, name='influential_shows'),
    path('news/', views.news, name='news'),
    path('reviews/', views.reviews, name='reviews'),
    path('search/', views.search, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
