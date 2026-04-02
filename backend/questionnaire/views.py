from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    GeneratedQuestionnaire,
    ProposalRequest,
    QuestionnaireResponse,
)
from .serializers import ProposalRequestSerializer, QuestionnaireResponseSerializer


# ── Public Endpoints ───────────────────────────────────────


@method_decorator(csrf_exempt, name="dispatch")
class ProposalCreateView(CreateAPIView):
    """POST /api/v1/proposals/ — submit project proposal (public)."""

    serializer_class = ProposalRequestSerializer


class QuestionnairePublicView(APIView):
    """GET /q/<token>/ — render questionnaire HTML (public, tokenized)."""

    def get(self, request, token):
        try:
            q = GeneratedQuestionnaire.objects.get(
                token=token, is_active=True, status__in=["approved", "sent"]
            )
        except GeneratedQuestionnaire.DoesNotExist:
            return HttpResponse(
                "<h1 style='text-align:center;margin-top:100px;font-family:sans-serif'>"
                "الرابط غير صالح أو منتهي الصلاحية</h1>",
                status=404,
            )

        if q.is_expired:
            return HttpResponse(
                "<h1 style='text-align:center;margin-top:100px;font-family:sans-serif'>"
                "انتهت صلاحية هذا الرابط</h1>",
                status=410,
            )

        return HttpResponse(q.generated_html, content_type="text/html")


@method_decorator(csrf_exempt, name="dispatch")
class QuestionnaireSubmitView(APIView):
    """POST /api/v1/q/<token>/submit/ — submit questionnaire responses (public)."""

    def post(self, request, token):
        try:
            q = GeneratedQuestionnaire.objects.get(
                token=token, is_active=True, status="sent"
            )
        except GeneratedQuestionnaire.DoesNotExist:
            return Response(
                {"error": "رابط غير صالح"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if q.is_expired:
            return Response(
                {"error": "انتهت صلاحية الرابط"},
                status=status.HTTP_410_GONE,
            )

        serializer = QuestionnaireResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            questionnaire=q,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        # Update proposal status
        q.proposal.status = "completed"
        q.proposal.save()

        return Response({"success": True, "message": "تم استلام ردكم بنجاح"})


# ── Admin Endpoints ────────────────────────────────────────


class AdminGenerateView(APIView):
    """Trigger AI questionnaire generation (GET from admin links, POST from API)."""

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        return self._generate(request, pk)

    def post(self, request, pk):
        return self._generate(request, pk)

    def _generate(self, request, pk):
        from .tasks import generate_questionnaire_task

        try:
            proposal = ProposalRequest.objects.get(pk=pk)
        except ProposalRequest.DoesNotExist:
            messages.error(request, "الطلب غير موجود")
            return HttpResponseRedirect("/admin/questionnaire/proposalrequest/")

        if proposal.status not in ("new", "reviewed"):
            messages.warning(
                request,
                f"لا يمكن التوليد — الحالة: {proposal.get_status_display()}",
            )
            return HttpResponseRedirect(
                f"/admin/questionnaire/proposalrequest/{proposal.pk}/change/"
            )

        generate_questionnaire_task.delay(str(proposal.id), request.user.id)
        proposal.status = "generating"
        proposal.save()

        messages.success(request, f"جاري توليد الاستمارة لـ {proposal.full_name}...")
        return HttpResponseRedirect(
            f"/admin/questionnaire/proposalrequest/{proposal.pk}/change/"
        )


class AdminPreviewView(APIView):
    """GET /api/v1/admin/questionnaires/<uuid>/preview/ — preview HTML."""

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            q = GeneratedQuestionnaire.objects.get(pk=pk)
        except GeneratedQuestionnaire.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(q.generated_html, content_type="text/html")


class AdminApproveView(APIView):
    """POST /api/v1/admin/questionnaires/<uuid>/approve/."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            q = GeneratedQuestionnaire.objects.get(pk=pk)
        except GeneratedQuestionnaire.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        q.status = "approved"
        q.approved_by = request.user
        q.approved_at = timezone.now()
        q.save()
        q.proposal.status = "approved"
        q.proposal.save()

        return Response({"message": "تم اعتماد الاستمارة"})


class AdminSendView(APIView):
    """Send questionnaire email to client."""

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        return self._send(request, pk)

    def post(self, request, pk):
        return self._send(request, pk)

    def _send(self, request, pk):
        from .tasks import send_questionnaire_email_task

        try:
            q = GeneratedQuestionnaire.objects.get(pk=pk)
        except GeneratedQuestionnaire.DoesNotExist:
            messages.error(request, "الاستمارة غير موجودة")
            return HttpResponseRedirect("/admin/questionnaire/generatedquestionnaire/")

        if q.status not in ("draft", "approved"):
            messages.warning(request, "الاستمارة غير جاهزة للإرسال")
        else:
            send_questionnaire_email_task.delay(str(q.id), request.user.id)
            messages.success(request, f"جاري إرسال الاستمارة لـ {q.proposal.full_name}...")

        return HttpResponseRedirect(
            f"/admin/questionnaire/proposalrequest/{q.proposal.pk}/change/"
        )


class AdminRegenerateView(APIView):
    """Regenerate questionnaire with AI."""

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        return self._regenerate(request, pk)

    def post(self, request, pk):
        return self._regenerate(request, pk)

    def _regenerate(self, request, pk):
        from .tasks import generate_questionnaire_task

        try:
            q = GeneratedQuestionnaire.objects.get(pk=pk)
        except GeneratedQuestionnaire.DoesNotExist:
            messages.error(request, "الاستمارة غير موجودة")
            return HttpResponseRedirect("/admin/questionnaire/generatedquestionnaire/")

        q.is_active = False
        q.save()

        proposal = q.proposal
        proposal.status = "generating"
        proposal.save()

        generate_questionnaire_task.delay(str(proposal.id), request.user.id)
        messages.success(request, f"جاري إعادة توليد الاستمارة لـ {proposal.full_name}...")
        return HttpResponseRedirect(
            f"/admin/questionnaire/proposalrequest/{proposal.pk}/change/"
        )
