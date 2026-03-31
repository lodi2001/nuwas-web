from django.core.management.base import BaseCommand
from landing.models import (
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


class Command(BaseCommand):
    help = "Seed the database with initial landing page content from the prototype"

    def handle(self, *args, **options):
        # Site Settings
        SiteSettings.load()  # creates with defaults
        self.stdout.write("✓ SiteSettings")

        # Hero Section
        HeroSection.load()  # creates with defaults
        self.stdout.write("✓ HeroSection")

        # Stats
        stats = [
            ("+25", "سنة خبرة"),
            ("+50", "مشروع منجز"),
            ("+15", "عميل حكومي"),
            ("+10", "منتجات ذكاء اصطناعي"),
        ]
        for i, (number, label) in enumerate(stats):
            StatItem.objects.get_or_create(
                number=number, defaults={"label_ar": label, "order": i}
            )
        self.stdout.write("✓ StatItems")

        # Section Headers
        headers = [
            ("learn", "تعلّم مع نواس", "محتوى تعليمي متخصص لبناء جيل تقني مبتكر"),
            ("services", "خدماتنا", "حلول تقنية متكاملة مخصصة لاحتياجات عملك"),
            ("products", "منتجاتنا المبتكرة", "أدوات تقنية صُممت لتمكين المؤسسات"),
            ("contact", "طلب عرض سعر", "ابدأ رحلة التحول الرقمي معنا اليوم"),
        ]
        for section, title, subtitle in headers:
            SectionHeader.objects.get_or_create(
                section=section,
                defaults={"title_ar": title, "subtitle_ar": subtitle},
            )
        self.stdout.write("✓ SectionHeaders")

        # Learn Cards
        learn_cards = [
            ("fas fa-brain", "دورات الذكاء الاصطناعي", "تعلم أساسيات وتطبيقات تعلم الآلة والذكاء الاصطناعي من الخبراء."),
            ("fas fa-laptop-code", "ورش عمل تقنية", "جلسات تدريبية عملية على أحدث التقنيات البرمجية العالمية."),
            ("fas fa-newspaper", "مقالات ومدونات", "ابقَ على اطلاع بأحدث التوجهات في عالم التحول الرقمي."),
        ]
        for i, (icon, title, desc) in enumerate(learn_cards):
            LearnCard.objects.get_or_create(
                title_ar=title,
                defaults={"icon_class": icon, "description_ar": desc, "order": i},
            )
        self.stdout.write("✓ LearnCards")

        # Service Cards
        service_cards = [
            ("fas fa-code", "تطوير البرمجيات", "بناء أنظمة مخصصة وتطبيقات ويب سحابية عالية الأداء."),
            ("fas fa-robot", "حلول الذكاء الاصطناعي", "تحليل البيانات، الرؤية الحاسوبية، ومعالجة اللغات الطبيعية."),
            ("fas fa-mobile-alt", "تطبيقات الجوال", "تطبيقات مبتكرة لأنظمة iOS و Android بتجربة مستخدم متميزة."),
        ]
        for i, (icon, title, desc) in enumerate(service_cards):
            ServiceCard.objects.get_or_create(
                title_ar=title,
                defaults={"icon_class": icon, "description_ar": desc, "order": i},
            )
        self.stdout.write("✓ ServiceCards")

        # Products
        products = [
            ("NUVIDEO.AI", "منصة ذكية لتحليل واسترجاع الفيديو بالذكاء الاصطناعي.", "تعرف آلي على الوجوه\nتحليل السلوك اللحظي\nتقارير ذكاء أعمال"),
            ("NuSport.AI", "منصة ذكاء اصطناعي متخصصة في تحليل الأداء الرياضي.", "تحليل أداء اللاعبين\nإحصائيات فورية\nتوقعات ذكية"),
            ("NuChat", "مساعد ذكي للمحادثات المدعومة بالذكاء الاصطناعي.", "محادثات ذكية\nدعم متعدد اللغات\nتكامل سلس"),
            ("NuFIX", "نظام ذكي لإدارة وتتبع المشاكل التقنية.", "تتبع الأخطاء\nحلول تلقائية\nتقارير تحليلية"),
            ("Magic Report", "إنشاء تقارير احترافية تلقائياً بالذكاء الاصطناعي.", "تقارير تلقائية\nتحليل بيانات\nقوالب ذكية"),
            ("NuPedia Research", "منصة بحثية ذكية للوصول إلى المعرفة بسرعة.", "بحث ذكي\nتلخيص تلقائي\nمصادر موثوقة"),
            ("DrivUp", "منصة ذكية لإدارة وتحسين تجربة القيادة.", "تتبع المركبات\nتحليل القيادة\nتقارير الأداء"),
            ("NSB", "منصة ذكية لإدارة وتحليل البيانات المصرفية.", "تحليل مالي\nأتمتة العمليات\nتقارير ذكية"),
        ]
        for i, (name, desc, features) in enumerate(products):
            Product.objects.get_or_create(
                name=name,
                defaults={
                    "description_ar": desc,
                    "features_ar": features,
                    "order": i,
                },
            )
        self.stdout.write("✓ Products")

        # Nav Links
        nav_links = [
            ("الرئيسية", "#home"),
            ("تعلّم معنا", "#learn"),
            ("الخدمات", "#services"),
            ("المنتجات", "#products"),
            ("تواصل معنا", "#contact"),
        ]
        for i, (label, href) in enumerate(nav_links):
            NavLink.objects.get_or_create(
                label_ar=label, defaults={"href": href, "order": i}
            )
        self.stdout.write("✓ NavLinks")

        # Footer Links
        footer_links = [
            ("الرئيسية", "#home"),
            ("الخدمات", "#services"),
            ("المنتجات", "#products"),
        ]
        for i, (label, href) in enumerate(footer_links):
            FooterLink.objects.get_or_create(
                label_ar=label, defaults={"href": href, "order": i}
            )
        self.stdout.write("✓ FooterLinks")

        # Video Banner
        banner = VideoBanner.load()
        if not banner.phrase_ar or banner.phrase_ar == "نبتكر حلولاً ذكية تُشكّل المستقبل":
            banner.phrase_ar = "نبتكر حلولاً ذكية تُشكّل المستقبل"
            banner.is_active = True
            banner.save()
        self.stdout.write("✓ VideoBanner")

        self.stdout.write(self.style.SUCCESS("\nAll content seeded successfully!"))
