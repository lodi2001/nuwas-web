import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_questionnaire_task(self, proposal_id: str, admin_user_id: int):
    """
    Triggered ONLY by admin clicking 'Generate Questionnaire'.
    Calls Claude API, generates HTML, stores result.
    """
    from .models import ProposalRequest
    from .services.questionnaire_generator import QuestionnaireGenerator

    try:
        proposal = ProposalRequest.objects.get(id=proposal_id)

        generator = QuestionnaireGenerator()
        questionnaire = generator.generate(proposal)

        proposal.status = "generated"
        proposal.save()

        logger.info(
            f"Questionnaire generated for {proposal.full_name}: "
            f"{questionnaire.total_features} features, "
            f"{questionnaire.total_requirements} requirements"
        )

    except Exception as e:
        logger.error(f"Failed to generate questionnaire for {proposal_id}: {e}")
        try:
            proposal = ProposalRequest.objects.get(id=proposal_id)
            proposal.status = "reviewed"
            proposal.save()
        except ProposalRequest.DoesNotExist:
            pass
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_questionnaire_email_task(self, questionnaire_id: str, admin_user_id: int):
    """
    Triggered ONLY by admin clicking 'Send to Client'.
    Sends email with tokenized questionnaire link.
    """
    from .models import GeneratedQuestionnaire, EmailLog

    try:
        q = GeneratedQuestionnaire.objects.get(id=questionnaire_id)
        proposal = q.proposal

        site_url = getattr(settings, "SITE_URL", "https://nuwas.ai")
        link = f"{site_url}/q/{q.token}/"
        subject = f"نواس | استمارة متطلبات مشروعكم — {proposal.full_name}"

        html_body = f"""
        <div dir="rtl" style="font-family:'Cairo',sans-serif;max-width:600px;margin:0 auto;padding:20px">
            <div style="text-align:center;margin-bottom:30px">
                <h2 style="color:#1A5FA0">نواس الابتكارية لتقنية المعلومات</h2>
            </div>
            <p>مرحباً {proposal.full_name},</p>
            <p>شكراً لاهتمامكم بخدمات نواس الابتكارية. قمنا بإعداد استمارة متطلبات مخصصة لمشروعكم.</p>
            <p><strong>نوع المشروع:</strong> {proposal.get_project_type_display()}</p>
            <div style="text-align:center;margin:30px 0">
                <a href="{link}"
                   style="background:#2AA8DC;color:#fff;padding:15px 40px;border-radius:8px;
                          text-decoration:none;font-weight:bold;font-size:16px">
                    ابدأ تعبئة الاستمارة
                </a>
            </div>
            <p style="color:#666;font-size:14px">
                📊 {q.total_features} ميزة رئيسية — {q.total_requirements} متطلب فرعي<br>
                ⏱ الوقت المتوقع: 15-20 دقيقة<br>
                📅 صلاحية الرابط: 30 يوم
            </p>
            <hr style="border:none;border-top:1px solid #eee;margin:30px 0">
            <p style="color:#999;font-size:12px;text-align:center">
                نواس الابتكارية لتقنية المعلومات | info@nuwas.ai
            </p>
        </div>
        """

        send_mail(
            subject=subject,
            message=f"رابط الاستمارة: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[proposal.email],
            html_message=html_body,
        )

        q.status = "sent"
        q.save()
        proposal.status = "sent"
        proposal.sent_at = timezone.now()
        proposal.save()

        EmailLog.objects.create(
            proposal=proposal,
            email_type="questionnaire_link",
            recipient_email=proposal.email,
            subject=subject,
            status="sent",
        )

        logger.info(f"Questionnaire email sent to {proposal.email}")

    except Exception as e:
        logger.error(f"Failed to send questionnaire email {questionnaire_id}: {e}")
        raise self.retry(exc=e)


@shared_task
def notify_admin_new_proposal(proposal_id: str):
    """Notify admin when a new proposal is submitted."""
    from .models import ProposalRequest

    try:
        proposal = ProposalRequest.objects.get(id=proposal_id)
        admin_email = getattr(settings, "NUWAS_ADMIN_EMAIL", "admin@nuwas.ai")
        site_url = getattr(settings, "SITE_URL", "https://nuwas.ai")

        subject = f"طلب عرض سعر جديد — {proposal.full_name} ({proposal.get_project_type_display()})"

        send_mail(
            subject=subject,
            message=(
                f"طلب جديد من {proposal.full_name}\n\n"
                f"{proposal.project_description[:300]}\n\n"
                f"رابط الإدارة: {site_url}/admin/questionnaire/proposalrequest/{proposal.id}/change/"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
        )
    except Exception as e:
        logger.error(f"Failed to notify admin for proposal {proposal_id}: {e}")
