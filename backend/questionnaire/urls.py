from django.urls import path
from .views import (
    ProposalCreateView,
    QuestionnairePublicView,
    QuestionnaireSubmitView,
    AdminGenerateView,
    AdminPreviewView,
    AdminApproveView,
    AdminSendView,
    AdminRegenerateView,
)

urlpatterns = [
    # Public
    path("api/v1/proposals/", ProposalCreateView.as_view()),
    path("q/<str:token>/", QuestionnairePublicView.as_view()),
    path("api/v1/q/<str:token>/submit/", QuestionnaireSubmitView.as_view()),
    # Admin (named routes for template buttons)
    path(
        "api/v1/admin/proposals/<uuid:pk>/generate/",
        AdminGenerateView.as_view(),
        name="admin-generate-questionnaire",
    ),
    path(
        "api/v1/admin/questionnaires/<uuid:pk>/preview/",
        AdminPreviewView.as_view(),
        name="admin-preview-questionnaire",
    ),
    path(
        "api/v1/admin/questionnaires/<uuid:pk>/approve/",
        AdminApproveView.as_view(),
        name="admin-approve-questionnaire",
    ),
    path(
        "api/v1/admin/questionnaires/<uuid:pk>/send/",
        AdminSendView.as_view(),
        name="admin-send-questionnaire",
    ),
    path(
        "api/v1/admin/questionnaires/<uuid:pk>/regenerate/",
        AdminRegenerateView.as_view(),
        name="admin-regenerate-questionnaire",
    ),
]
