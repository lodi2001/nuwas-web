from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    SiteSettings,
    HeroSection,
    StatItem,
    SectionHeader,
    LearnCard,
    ServiceCard,
    Product,
    NavLink,
    FooterLink,
    VideoBanner,
)
from .serializers import (
    SiteSettingsSerializer,
    HeroSectionSerializer,
    StatItemSerializer,
    SectionHeaderSerializer,
    LearnCardSerializer,
    ServiceCardSerializer,
    ProductSerializer,
    NavLinkSerializer,
    FooterLinkSerializer,
    ContactSubmissionSerializer,
    VideoBannerSerializer,
)


class LandingPageView(APIView):
    """GET /api/landing/ — returns all landing page content."""

    def get(self, request):
        data = {
            "site_settings": SiteSettingsSerializer(
                SiteSettings.load(), context={"request": request}
            ).data,
            "hero": HeroSectionSerializer(
                HeroSection.load(), context={"request": request}
            ).data,
            "stats": StatItemSerializer(StatItem.objects.all(), many=True).data,
            "section_headers": SectionHeaderSerializer(
                SectionHeader.objects.all(), many=True
            ).data,
            "learn_cards": LearnCardSerializer(
                LearnCard.objects.all(), many=True
            ).data,
            "service_cards": ServiceCardSerializer(
                ServiceCard.objects.all(), many=True
            ).data,
            "products": ProductSerializer(Product.objects.all(), many=True).data,
            "nav_links": NavLinkSerializer(NavLink.objects.all(), many=True).data,
            "footer_links": FooterLinkSerializer(
                FooterLink.objects.all(), many=True
            ).data,
            "video_banner": VideoBannerSerializer(
                VideoBanner.load(), context={"request": request}
            ).data,
        }
        return Response(data)


class ContactSubmissionView(CreateAPIView):
    """POST /api/contact/ — submit a contact form."""

    serializer_class = ContactSubmissionSerializer
