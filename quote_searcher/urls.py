from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_box, name='user-quote-search-box'),
    path('search/<str:query_text>', views.search_on_quotes, name='user-quote-search-by-url')
]
