from rest_framework import serializers
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
    ContactSubmission,
    VideoBanner,
)


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        exclude = ["id"]


class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        exclude = ["id"]


class StatItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatItem
        exclude = ["id"]


class SectionHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionHeader
        exclude = ["id"]


class LearnCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnCard
        exclude = ["id"]


class ServiceCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCard
        exclude = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    features_list_ar = serializers.SerializerMethodField()
    features_list_en = serializers.SerializerMethodField()

    class Meta:
        model = Product
        exclude = ["id"]

    def get_features_list_ar(self, obj):
        return [f.strip() for f in obj.features_ar.split("\n") if f.strip()]

    def get_features_list_en(self, obj):
        if not obj.features_en:
            return []
        return [f.strip() for f in obj.features_en.split("\n") if f.strip()]


class NavLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavLink
        exclude = ["id"]


class FooterLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterLink
        exclude = ["id"]


class VideoBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoBanner
        exclude = ["id"]


class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = [
            "full_name", "email", "phone", "organization",
            "service_type", "project_description",
        ]
