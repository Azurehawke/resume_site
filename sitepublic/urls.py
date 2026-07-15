from django.urls import path

from . import views

app_name = "sitepublic"

urlpatterns = [
    path("<slug:slug>/", views.resume, name="resume"),
]
