from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.customLoginView, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('plot_test/', views.plot_test, name='plot_test'), 
    # path("stocks/", views.index, name='stocks'),
    re_path(r"(?P<item>\d{6})/$", views.item_detail, name='dashboard_item_index_detail'),
    
]
