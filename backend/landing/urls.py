from django.urls import path
from .views import LandingPageView, ContactSubmissionView

urlpatterns = [
    path("landing/", LandingPageView.as_view()),
    path("contact/", ContactSubmissionView.as_view()),
]
