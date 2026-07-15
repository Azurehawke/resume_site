from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="portal/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("pages/", views.page_list, name="page_list"),
    path("pages/new/", views.page_create, name="page_create"),
    path("pages/<int:pk>/build/", views.page_builder, name="page_builder"),
    path("pages/<int:pk>/delete/", views.page_delete, name="page_delete"),
    path("pages/<int:pk>/pdf/", views.page_pdf, name="page_pdf"),
    path("analytics/", views.analytics_list, name="analytics_list"),
    path("analytics/<int:pk>/", views.analytics_detail, name="analytics_detail"),
]
