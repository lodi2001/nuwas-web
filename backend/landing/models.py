from django.db import models


class SingletonModel(models.Model):
    """Abstract base — ensures only one instance exists."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── Singletons ──────────────────────────────────────────────


class SiteSettings(SingletonModel):
    site_name_ar = models.CharField(max_length=200, default="نواس الابتكارية")
    site_name_en = models.CharField(max_length=200, default="Nuwas Innovative", blank=True)
    logo = models.ImageField(upload_to="branding/", blank=True)
    email = models.EmailField(default="info@nuwas.sa")
    phone = models.CharField(max_length=30, default="+966 500 000 000")
    address_ar = models.CharField(max_length=300, default="جدة - الرياض، السعودية")
    address_en = models.CharField(max_length=300, blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    copyright_text_ar = models.CharField(
        max_length=300,
        default="جميع الحقوق محفوظة © 2026 نواس الابتكارية لتقنية المعلومات",
    )
    copyright_text_en = models.CharField(max_length=300, blank=True)
    footer_description_ar = models.TextField(
        default="شركة رائدة في تقديم الحلول البرمجية والذكاء الاصطناعي، نساهم في تحقيق رؤية المملكة 2030 من خلال الابتكار التقني.",
        blank=True,
    )
    footer_description_en = models.TextField(blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


class HeroSection(SingletonModel):
    heading_ar = models.CharField(max_length=300, default="نبتكر حلولاً ذكية تُشكّل المستقبل")
    heading_en = models.CharField(max_length=300, blank=True)
    subheading_ar = models.TextField(
        default="نواس الابتكارية — شريكك الموثوق في المملكة العربية السعودية للتحول الرقمي وتطوير حلول الذكاء الاصطناعي المتطورة."
    )
    subheading_en = models.TextField(blank=True)
    cta_primary_text_ar = models.CharField(max_length=100, default="اكتشف خدماتنا")
    cta_primary_text_en = models.CharField(max_length=100, blank=True)
    cta_primary_link = models.CharField(max_length=200, default="#services")
    cta_secondary_text_ar = models.CharField(max_length=100, default="تواصل معنا")
    cta_secondary_text_en = models.CharField(max_length=100, blank=True)
    cta_secondary_link = models.CharField(max_length=200, default="#contact")
    background_image = models.ImageField(upload_to="hero/", blank=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return "Hero Section"


# ── Ordered List Models ─────────────────────────────────────


class StatItem(models.Model):
    number = models.CharField(max_length=20)
    label_ar = models.CharField(max_length=100)
    label_en = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.number} - {self.label_ar}"


class SectionHeader(models.Model):
    SECTION_CHOICES = [
        ("learn", "Learn"),
        ("services", "Services"),
        ("products", "Products"),
        ("contact", "Contact"),
    ]
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, unique=True)
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    subtitle_ar = models.CharField(max_length=300)
    subtitle_en = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.get_section_display()}: {self.title_ar}"


class LearnCard(models.Model):
    icon_class = models.CharField(
        max_length=100, help_text="Font Awesome class, e.g. 'fas fa-brain'"
    )
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    description_ar = models.TextField()
    description_en = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar


class ServiceCard(models.Model):
    icon_class = models.CharField(
        max_length=100, help_text="Font Awesome class, e.g. 'fas fa-code'"
    )
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    description_ar = models.TextField()
    description_en = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar


class Product(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="products/", blank=True)
    description_ar = models.TextField()
    description_en = models.TextField(blank=True)
    features_ar = models.TextField(help_text="One feature per line")
    features_en = models.TextField(blank=True, help_text="One feature per line")
    link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class NavLink(models.Model):
    label_ar = models.CharField(max_length=100)
    label_en = models.CharField(max_length=100, blank=True)
    href = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label_ar


class FooterLink(models.Model):
    label_ar = models.CharField(max_length=100)
    label_en = models.CharField(max_length=100, blank=True)
    href = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label_ar


# ── Video Banner ────────────────────────────────────────────


class VideoBanner(SingletonModel):
    video = models.FileField(upload_to="videos/", blank=True)
    phrase_ar = models.CharField(
        max_length=300,
        default="نبتكر حلولاً ذكية تُشكّل المستقبل",
    )
    phrase_en = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Video Banner"
        verbose_name_plural = "Video Banner"

    def __str__(self):
        return "Video Banner"


# ── Submissions ─────────────────────────────────────────────


class ContactSubmission(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    organization = models.CharField(max_length=200, blank=True)
    service_type = models.CharField(max_length=100)
    project_description = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.service_type} ({self.created_at:%Y-%m-%d})"
