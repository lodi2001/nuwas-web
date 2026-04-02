from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    AIConfig,
    ProposalRequest,
    GeneratedQuestionnaire,
    QuestionnaireResponse,
    EmailLog,
)


# ── AI Config (Singleton) ──────────────────────────────────


@admin.register(AIConfig)
class AIConfigAdmin(admin.ModelAdmin):
    list_display = ["__str__", "model_name", "display_masked_key"]
    fieldsets = [
        ("API Settings", {"fields": ("api_key", "model_name")}),
        ("Generation Parameters", {"fields": ("max_tokens", "temperature")}),
    ]

    def display_masked_key(self, obj):
        return obj.masked_key

    display_masked_key.short_description = "API Key"

    def has_add_permission(self, request):
        return not AIConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ── Proposal Request ───────────────────────────────────────


@admin.register(ProposalRequest)
class ProposalRequestAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "company_name",
        "project_type",
        "status_badge",
        "created_at",
        "has_questionnaire",
    ]
    list_filter = ["status", "project_type", "budget_range", "created_at"]
    search_fields = ["full_name", "email", "company_name", "project_description"]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "reviewed_by",
        "reviewed_at",
        "sent_by",
        "sent_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "بيانات العميل",
            {"fields": ("full_name", "email", "phone", "company_name")},
        ),
        (
            "تفاصيل المشروع",
            {
                "fields": (
                    "project_type",
                    "project_description",
                    "budget_range",
                    "timeline",
                )
            },
        ),
        (
            "حالة الطلب",
            {
                "fields": (
                    "status",
                    "admin_notes",
                    "reviewed_by",
                    "reviewed_at",
                    "sent_by",
                    "sent_at",
                )
            },
        ),
    )

    actions = ["mark_reviewed", "generate_questionnaire_action"]

    def status_badge(self, obj):
        colors = {
            "new": "#3B82F6",
            "reviewed": "#8B5CF6",
            "generating": "#F59E0B",
            "generated": "#F97316",
            "approved": "#10B981",
            "sent": "#06B6D4",
            "completed": "#22C55E",
            "closed": "#6B7280",
        }
        color = colors.get(obj.status, "#6B7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:bold">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "الحالة"

    def has_questionnaire(self, obj):
        return obj.questionnaires.filter(is_active=True).exists()

    has_questionnaire.boolean = True
    has_questionnaire.short_description = "استمارة"

    @admin.action(description="✅ تحديد كمُراجَع")
    def mark_reviewed(self, request, queryset):
        queryset.update(
            status="reviewed",
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )

    @admin.action(description="🤖 توليد استمارة بالذكاء الاصطناعي")
    def generate_questionnaire_action(self, request, queryset):
        from .tasks import generate_questionnaire_task

        for proposal in queryset:
            if proposal.status not in ("new", "reviewed"):
                self.message_user(
                    request,
                    f"لا يمكن التوليد لـ {proposal.full_name} — الحالة: {proposal.get_status_display()}",
                    level="warning",
                )
                continue
            generate_questionnaire_task.delay(str(proposal.id), request.user.id)
            proposal.status = "generating"
            proposal.save()
            self.message_user(
                request,
                f"جاري توليد الاستمارة لـ {proposal.full_name}...",
            )

    change_form_template = "admin/questionnaire/proposal_change_form.html"


# ── Generated Questionnaire ────────────────────────────────


@admin.register(GeneratedQuestionnaire)
class GeneratedQuestionnaireAdmin(admin.ModelAdmin):
    list_display = [
        "proposal_name",
        "version",
        "status",
        "total_features",
        "total_requirements",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    readonly_fields = [
        "id",
        "token",
        "created_at",
        "approved_by",
        "approved_at",
        "generation_metadata",
    ]

    actions = ["approve_and_send", "approve_only", "reject_questionnaire"]

    def proposal_name(self, obj):
        return obj.proposal.full_name

    proposal_name.short_description = "العميل"

    @admin.action(description="✅📧 اعتماد + إرسال للعميل")
    def approve_and_send(self, request, queryset):
        from .tasks import send_questionnaire_email_task

        for q in queryset:
            if q.status not in ("draft", "approved"):
                continue
            q.status = "sent"
            q.approved_by = request.user
            q.approved_at = timezone.now()
            q.save()
            send_questionnaire_email_task.delay(str(q.id), request.user.id)
            q.proposal.status = "sent"
            q.proposal.sent_by = request.user
            q.proposal.sent_at = timezone.now()
            q.proposal.save()
            self.message_user(
                request,
                f"تم اعتماد وإرسال الاستمارة لـ {q.proposal.full_name}",
            )

    @admin.action(description="✅ اعتماد فقط (بدون إرسال)")
    def approve_only(self, request, queryset):
        queryset.filter(status="draft").update(
            status="approved",
            approved_by=request.user,
            approved_at=timezone.now(),
        )

    @admin.action(description="❌ رفض (يحتاج إعادة توليد)")
    def reject_questionnaire(self, request, queryset):
        queryset.update(status="rejected")

    change_form_template = "admin/questionnaire/questionnaire_change_form.html"


# ── Questionnaire Response ─────────────────────────────────


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = [
        "respondent_name",
        "respondent_email",
        "completion_percentage",
        "submitted_at",
    ]
    readonly_fields = [
        "id",
        "questionnaire",
        "respondent_name",
        "respondent_email",
        "checked_requirements",
        "na_requirements",
        "sub_answers",
        "summary_snapshot",
        "submitted_at",
        "ip_address",
        "user_agent",
        "completion_percentage",
        "time_spent_seconds",
    ]

    def has_add_permission(self, request):
        return False


# ── Email Log ──────────────────────────────────────────────


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ["recipient_email", "email_type", "subject", "status", "sent_at"]
    list_filter = ["email_type", "status", "sent_at"]
    search_fields = ["recipient_email", "subject"]
    readonly_fields = [
        "id",
        "proposal",
        "email_type",
        "recipient_email",
        "subject",
        "sent_at",
        "status",
        "provider_message_id",
    ]

    def has_add_permission(self, request):
        return False
