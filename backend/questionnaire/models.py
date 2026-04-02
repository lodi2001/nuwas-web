import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


# ── Choices ─────────────────────────────────────────────────

PROJECT_TYPE_CHOICES = [
    ("mobile_app", "تطبيق جوال"),
    ("web_platform", "منصة ويب"),
    ("ai_system", "نظام ذكاء اصطناعي"),
    ("digital_transformation", "تحول رقمي"),
    ("other", "أخرى"),
]

BUDGET_CHOICES = [
    ("under_50k", "أقل من 50,000 ريال"),
    ("50k_150k", "50,000 - 150,000 ريال"),
    ("150k_500k", "150,000 - 500,000 ريال"),
    ("over_500k", "أكثر من 500,000 ريال"),
    ("undecided", "لم يتم التحديد"),
]

TIMELINE_CHOICES = [
    ("1_3_months", "1-3 أشهر"),
    ("3_6_months", "3-6 أشهر"),
    ("6_12_months", "6-12 شهر"),
    ("flexible", "مرن"),
]

PROPOSAL_STATUS_CHOICES = [
    ("new", "جديد — بانتظار المراجعة"),
    ("reviewed", "تمت المراجعة"),
    ("generating", "جاري التوليد بالذكاء الاصطناعي"),
    ("generated", "تم التوليد — بانتظار موافقة الإدارة"),
    ("approved", "معتمد — جاهز للإرسال"),
    ("sent", "تم الإرسال للعميل"),
    ("completed", "العميل أكمل الاستمارة"),
    ("closed", "مغلق"),
]

QUESTIONNAIRE_STATUS_CHOICES = [
    ("draft", "مسودة — بانتظار مراجعة الإدارة"),
    ("approved", "معتمد — جاهز للإرسال"),
    ("sent", "تم الإرسال للعميل"),
    ("rejected", "مرفوض — يحتاج إعادة توليد"),
]

AI_MODEL_CHOICES = [
    ("claude-sonnet-4-20250514", "Claude Sonnet 4"),
    ("claude-opus-4-20250514", "Claude Opus 4"),
]


# ── AI Configuration (Singleton) ───────────────────────────


class AIConfig(models.Model):
    """Admin-configurable AI settings. Singleton — only one instance."""

    api_key = models.CharField(
        max_length=200,
        help_text="مفتاح API من Anthropic",
    )
    model_name = models.CharField(
        max_length=100,
        choices=AI_MODEL_CHOICES,
        default="claude-sonnet-4-20250514",
        help_text="نموذج الذكاء الاصطناعي المستخدم",
    )
    max_tokens = models.PositiveIntegerField(default=8192)
    temperature = models.FloatField(default=0.7)

    class Meta:
        verbose_name = "AI Configuration"
        verbose_name_plural = "AI Configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"api_key": ""})
        return obj

    def __str__(self):
        return "AI Configuration"

    @property
    def masked_key(self):
        if len(self.api_key) > 12:
            return f"{'•' * (len(self.api_key) - 8)}...{self.api_key[-8:]}"
        return "•" * len(self.api_key)


# ── Proposal Request ───────────────────────────────────────


class ProposalRequest(models.Model):
    """Client project proposal submitted via the contact form."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=30, verbose_name="رقم الجوال")
    company_name = models.CharField(
        max_length=200, blank=True, verbose_name="اسم الشركة/المؤسسة"
    )
    project_type = models.CharField(
        max_length=50,
        choices=PROJECT_TYPE_CHOICES,
        verbose_name="نوع المشروع",
    )
    project_description = models.TextField(verbose_name="وصف فكرة المشروع")
    budget_range = models.CharField(
        max_length=50,
        choices=BUDGET_CHOICES,
        default="undecided",
        verbose_name="نطاق الميزانية",
    )
    timeline = models.CharField(
        max_length=50,
        choices=TIMELINE_CHOICES,
        default="flexible",
        verbose_name="الجدول الزمني",
    )

    # Status pipeline
    status = models.CharField(
        max_length=20,
        choices=PROPOSAL_STATUS_CHOICES,
        default="new",
        verbose_name="الحالة",
    )

    # Admin tracking
    admin_notes = models.TextField(
        blank=True,
        help_text="ملاحظات داخلية للإدارة — لا تظهر للعميل",
        verbose_name="ملاحظات الإدارة",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_proposals",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_proposals",
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "طلب عرض سعر"
        verbose_name_plural = "طلبات عروض الأسعار"

    def __str__(self):
        return f"{self.full_name} — {self.get_project_type_display()} ({self.created_at:%Y-%m-%d})"


# ── Generated Questionnaire ────────────────────────────────


class GeneratedQuestionnaire(models.Model):
    """AI-generated requirements questionnaire linked to a proposal."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(
        ProposalRequest,
        on_delete=models.CASCADE,
        related_name="questionnaires",
    )
    version = models.PositiveIntegerField(default=1)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    token_expires_at = models.DateTimeField()

    # AI generation
    ai_model = models.CharField(max_length=100, default="claude-sonnet-4-20250514")
    ai_prompt_used = models.TextField(blank=True)
    generated_html = models.TextField(blank=True)
    generation_metadata = models.JSONField(default=dict, blank=True)

    # Structure
    features = models.JSONField(default=list, blank=True)
    total_features = models.IntegerField(default=0)
    total_requirements = models.IntegerField(default=0)

    # Admin approval
    status = models.CharField(
        max_length=20,
        choices=QUESTIONNAIRE_STATUS_CHOICES,
        default="draft",
    )
    admin_feedback = models.TextField(
        blank=True, help_text="ملاحظات الإدارة على الاستمارة المولّدة"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_questionnaires",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "استمارة مولّدة"
        verbose_name_plural = "الاستمارات المولّدة"

    def __str__(self):
        return f"استمارة #{self.version} — {self.proposal.full_name}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.token_expires_at:
            self.token_expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.token_expires_at


# ── Questionnaire Response ─────────────────────────────────


class QuestionnaireResponse(models.Model):
    """Client's filled responses to a generated questionnaire."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questionnaire = models.ForeignKey(
        GeneratedQuestionnaire,
        on_delete=models.CASCADE,
        related_name="responses",
    )

    # Response data
    checked_requirements = models.JSONField(default=list)
    na_requirements = models.JSONField(default=list)
    sub_answers = models.JSONField(default=dict)
    summary_snapshot = models.JSONField(default=dict)

    # Respondent info
    respondent_name = models.CharField(max_length=200)
    respondent_email = models.EmailField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    completion_percentage = models.FloatField(default=0)
    time_spent_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "رد العميل"
        verbose_name_plural = "ردود العملاء"

    def __str__(self):
        return f"{self.respondent_name} — {self.completion_percentage:.0f}%"


# ── Email Log ──────────────────────────────────────────────


class EmailLog(models.Model):
    """Track all emails sent."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(
        ProposalRequest,
        on_delete=models.CASCADE,
        related_name="email_logs",
    )
    email_type = models.CharField(
        max_length=50,
        choices=[
            ("questionnaire_link", "رابط الاستمارة"),
            ("reminder", "تذكير"),
            ("thank_you", "شكر"),
            ("admin_notification", "إشعار للإدارة"),
        ],
    )
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        default="sent",
        choices=[
            ("sent", "تم الإرسال"),
            ("delivered", "تم التسليم"),
            ("opened", "تم الفتح"),
            ("bounced", "ارتداد"),
            ("failed", "فشل"),
        ],
    )
    provider_message_id = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-sent_at"]
        verbose_name = "سجل البريد"
        verbose_name_plural = "سجلات البريد"

    def __str__(self):
        return f"{self.get_email_type_display()} → {self.recipient_email}"
