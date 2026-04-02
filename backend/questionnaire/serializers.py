from rest_framework import serializers
from .models import ProposalRequest, QuestionnaireResponse


class ProposalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalRequest
        fields = [
            "full_name",
            "email",
            "phone",
            "company_name",
            "project_type",
            "project_description",
            "budget_range",
            "timeline",
        ]


class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireResponse
        fields = [
            "checked_requirements",
            "na_requirements",
            "sub_answers",
            "summary_snapshot",
            "respondent_name",
            "respondent_email",
            "completion_percentage",
            "time_spent_seconds",
        ]
