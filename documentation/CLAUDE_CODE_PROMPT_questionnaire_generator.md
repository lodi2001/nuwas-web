# Claude Code Prompt: AI-Powered Requirements Questionnaire Generator for Nuwas.ai

## Project Overview

Build a full-stack feature for the **Nuwas.ai** platform that generates professional Arabic requirements elicitation questionnaires (HTML forms) using AI. The workflow is **admin-driven** — NOT automatic:

### Workflow (Critical — Admin-Controlled Pipeline)

```
1. CLIENT submits project idea via Nuwas.ai contact form
          ↓
2. ADMIN receives notification + sees new proposal in Django Admin
          ↓
3. ADMIN reviews the project description, edits if needed
          ↓
4. ADMIN clicks "🤖 Generate Questionnaire" button → AI generates the form
          ↓
5. ADMIN previews the generated HTML questionnaire in Django Admin
          ↓
6. ADMIN can: Edit / Regenerate / Approve
          ↓
7. ADMIN clicks "📧 Send to Client" → email with tokenized link is sent
          ↓
8. CLIENT receives email → opens link → fills questionnaire → submits
          ↓
9. ADMIN reviews responses in Django Admin dashboard
```

**Key principle**: The AI generation and email sending are NEVER automatic. The Nuwas admin (Dr. Khalid or his team) always reviews and approves before anything reaches the client.

---

## System Context

- **Platform**: Nuwas.ai (landing page with an RFP/proposal request contact form)
- **Tech Stack**: Django (backend) + React or Next.js (frontend) + PostgreSQL
- **Language**: Arabic-first (RTL), with English fallback
- **AI Provider**: Anthropic Claude API (claude-sonnet-4-20250514)
- **Email Service**: SendGrid, Mailgun, or AWS SES (configurable)
- **Domain**: nuwas.ai (Cloudflare DNS)

---

## Reference Templates

Two production-quality HTML questionnaire templates have been created and should be used as the **gold standard** for AI-generated output. These are located in the project:

1. `templates/questionnaires/transport-app-checklist.html` — Intercity passenger transport app (12 features, 56 requirements)
2. `templates/questionnaires/ai-surveillance-checklist.html` — AI surveillance system (10 features, 37 requirements)

### Template Structure (AI Must Replicate)

Each questionnaire follows this exact structure:

```
├── Sticky Header (Nuwas logo + progress bar)
├── Hero Card (project title + description + stats)
├── Instructions Card
├── Feature Sections (collapsible, numbered)
│   ├── Feature Header (number + title + counter + chevron)
│   └── Feature Body
│       ├── Requirement Groups (labeled with emoji + category)
│       │   └── Requirement Items
│       │       ├── Checkbox (main toggle)
│       │       ├── Priority Tag (Must / Should / Nice)
│       │       ├── Title + Description
│       │       ├── Sub-Questions (shown when checked)
│       │       │   ├── Checkbox Groups (multi-select)
│       │       │   ├── Radio Groups (single-select)
│       │       │   ├── Text Inputs
│       │       │   └── Textareas
│       │       └── N/A Toggle
│       └── Section Summary Bar (count + progress bar + percentage)
├── Fixed Bottom Actions Bar (reset + expand all + summary)
└── Summary Modal (overview of all selections)
```

### CSS Design System (Must Be Preserved)

```css
Colors: --teal: #2AA8DC, --blue: #1A5FA0, --ink: #1A1A2E
Font: 'Cairo' (Arabic), 'IBM Plex Mono' (numbers)
Priority Tags: .p-must (red), .p-should (gold), .p-nice (blue)
Cards: border-radius: 16px, box-shadow system (sm/md/lg)
Direction: RTL (right-to-left)
```

### JavaScript Functionality (Must Be Preserved)

- Real-time progress tracking (per-feature + global)
- Checkbox/radio toggle with visual pill selection
- N/A toggle that unchecks and grays out requirement
- Collapsible feature sections
- Summary modal showing all selections + filled text fields
- Reset all functionality
- Print-friendly CSS (@media print)

---

## Feature Requirements

### 1. Contact Form Enhancement (Frontend)

Modify the existing Nuwas.ai RFP contact form to capture:

```
Fields:
- full_name (required) — الاسم الكامل
- email (required) — البريد الإلكتروني  
- phone (required) — رقم الجوال
- company_name (optional) — اسم الشركة/المؤسسة
- project_type (dropdown: mobile app, web platform, AI system, other) — نوع المشروع
- project_description (textarea, required, min 50 chars) — وصف فكرة المشروع
- budget_range (dropdown: <50K, 50-150K, 150-500K, 500K+, undecided) — نطاق الميزانية
- timeline (dropdown: 1-3 months, 3-6 months, 6-12 months, flexible) — الجدول الزمني
```

On submit → call backend API → store in DB → notify admin (email/Telegram). **NO automatic AI generation.**

### 2. Backend API & Data Models (Django)

#### Models

```python
# models.py

class ProposalRequest(models.Model):
    """Initial contact form submission"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)
    project_description = models.TextField()
    budget_range = models.CharField(max_length=50, choices=BUDGET_CHOICES)
    timeline = models.CharField(max_length=50, choices=TIMELINE_CHOICES)
    
    # Admin-controlled status pipeline
    status = models.CharField(max_length=20, default='new', choices=[
        ('new', 'جديد — بانتظار المراجعة'),
        ('reviewed', 'تمت المراجعة'),
        ('generating', 'جاري التوليد بالذكاء الاصطناعي'),
        ('generated', 'تم التوليد — بانتظار موافقة الإدارة'),
        ('approved', 'معتمد — جاهز للإرسال'),
        ('sent', 'تم الإرسال للعميل'),
        ('completed', 'العميل أكمل الاستمارة'),
        ('closed', 'مغلق'),
    ])
    
    # Admin notes
    admin_notes = models.TextField(blank=True, help_text="ملاحظات داخلية للإدارة — لا تظهر للعميل")
    reviewed_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_proposals')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='sent_proposals')
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GeneratedQuestionnaire(models.Model):
    """AI-generated questionnaire linked to a proposal request"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    proposal = models.ForeignKey(ProposalRequest, on_delete=models.CASCADE, related_name='questionnaires')
    version = models.PositiveIntegerField(default=1)  # allows multiple generations (regenerate)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    token_expires_at = models.DateTimeField()
    
    # AI Generation
    ai_model = models.CharField(max_length=50, default='claude-sonnet-4-20250514')
    ai_prompt_used = models.TextField()
    generated_html = models.TextField()  # the full HTML questionnaire
    generation_metadata = models.JSONField(default=dict)
    
    # Structure
    features = models.JSONField(default=list)
    total_features = models.IntegerField(default=0)
    total_requirements = models.IntegerField(default=0)
    
    # Admin review workflow
    status = models.CharField(max_length=20, default='draft', choices=[
        ('draft', 'مسودة — بانتظار مراجعة الإدارة'),
        ('approved', 'معتمد — جاهز للإرسال'),
        ('sent', 'تم الإرسال للعميل'),
        ('rejected', 'مرفوض — يحتاج إعادة توليد'),
    ])
    admin_feedback = models.TextField(blank=True, help_text="ملاحظات الإدارة على الاستمارة المولّدة")
    approved_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_questionnaires')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class QuestionnaireResponse(models.Model):
    """User's response to a generated questionnaire"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    questionnaire = models.ForeignKey(GeneratedQuestionnaire, on_delete=models.CASCADE, related_name='responses')
    
    # Response data
    checked_requirements = models.JSONField(default=list)   # ["req-1-1", "req-1-2", ...]
    na_requirements = models.JSONField(default=list)        # ["req-3-5", ...]
    sub_answers = models.JSONField(default=dict)            # {"req-1-1": {"radio": {...}, "checks": [...], "text": {...}}}
    summary_snapshot = models.JSONField(default=dict)       # per-feature summary at submission time
    
    # Meta
    respondent_name = models.CharField(max_length=200)
    respondent_email = models.EmailField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    completion_percentage = models.FloatField(default=0)
    time_spent_seconds = models.IntegerField(null=True)  # tracked via JS


class EmailLog(models.Model):
    """Track all emails sent"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    proposal = models.ForeignKey(ProposalRequest, on_delete=models.CASCADE)
    email_type = models.CharField(max_length=50)  # questionnaire_link, reminder, thank_you
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # sent, delivered, opened, bounced
    provider_message_id = models.CharField(max_length=200, blank=True)
```

#### API Endpoints

```python
# urls.py
urlpatterns = [
    # Public — Client-facing
    path('api/v1/proposals/', ProposalCreateView.as_view()),                    # POST: submit contact form (public)
    path('q/<str:token>/', QuestionnairePublicView.as_view()),                  # GET: render questionnaire (public, tokenized)
    path('api/v1/q/<str:token>/submit/', QuestionnaireSubmitView.as_view()),    # POST: submit responses (public)
    
    # Admin — All admin actions are via Django Admin custom actions + these endpoints
    path('api/v1/admin/proposals/<uuid:pk>/generate/', AdminGenerateView.as_view()),    # POST: trigger AI generation (admin only)
    path('api/v1/admin/questionnaires/<uuid:pk>/preview/', AdminPreviewView.as_view()), # GET: preview generated HTML (admin only)
    path('api/v1/admin/questionnaires/<uuid:pk>/approve/', AdminApproveView.as_view()), # POST: approve questionnaire (admin only)
    path('api/v1/admin/questionnaires/<uuid:pk>/send/', AdminSendView.as_view()),       # POST: send email to client (admin only)
    path('api/v1/admin/questionnaires/<uuid:pk>/regenerate/', AdminRegenerateView.as_view()),  # POST: regenerate with AI (admin only)
    path('api/v1/admin/responses/<uuid:pk>/', AdminResponseDetailView.as_view()),       # GET: view client responses (admin only)
]
```

### 3. Django Admin — The Central Control Panel (CRITICAL)

The Django Admin is where the Nuwas team manages the entire pipeline. This must be a rich, functional admin interface — NOT just default Django admin.

#### ProposalRequestAdmin

```python
# admin.py

@admin.register(ProposalRequest)
class ProposalRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company_name', 'project_type', 'status', 'status_badge', 'created_at', 'has_questionnaire']
    list_filter = ['status', 'project_type', 'budget_range', 'created_at']
    search_fields = ['full_name', 'email', 'company_name', 'project_description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'sent_by', 'sent_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('بيانات العميل', {
            'fields': ('full_name', 'email', 'phone', 'company_name')
        }),
        ('تفاصيل المشروع', {
            'fields': ('project_type', 'project_description', 'budget_range', 'timeline')
        }),
        ('حالة الطلب', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at', 'sent_by', 'sent_at')
        }),
    )
    
    # ── Custom Admin Actions ──────────────────────────────────
    actions = ['generate_questionnaire', 'mark_reviewed']
    
    def generate_questionnaire(self, request, queryset):
        """Admin action: Generate AI questionnaire for selected proposals"""
        for proposal in queryset:
            if proposal.status not in ('new', 'reviewed'):
                self.message_user(request, f"⚠️ لا يمكن التوليد لـ {proposal.full_name} — الحالة: {proposal.get_status_display()}", level='warning')
                continue
            # Trigger async generation
            generate_questionnaire_task.delay(str(proposal.id), request.user.id)
            proposal.status = 'generating'
            proposal.save()
            self.message_user(request, f"🤖 جاري توليد الاستمارة لـ {proposal.full_name}...")
    generate_questionnaire.short_description = "🤖 توليد استمارة بالذكاء الاصطناعي"
    
    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed', reviewed_by=request.user, reviewed_at=timezone.now())
    mark_reviewed.short_description = "✅ تحديد كمُراجَع"
    
    # ── Custom display methods ────────────────────────────────
    def has_questionnaire(self, obj):
        return obj.questionnaires.filter(is_active=True).exists()
    has_questionnaire.boolean = True
    has_questionnaire.short_description = "استمارة"
    
    def status_badge(self, obj):
        colors = {
            'new': '#3B82F6', 'reviewed': '#8B5CF6', 'generating': '#F59E0B',
            'generated': '#F97316', 'approved': '#10B981', 'sent': '#06B6D4',
            'completed': '#22C55E', 'closed': '#6B7280'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:bold">{}</span>', color, obj.get_status_display())
    status_badge.short_description = "الحالة"
    
    # ── Custom change_form template with action buttons ───────
    change_form_template = 'admin/questionnaire/proposal_change_form.html'
    # This template adds buttons:
    # - "🤖 توليد الاستمارة" (if status is new/reviewed)
    # - "👁️ معاينة الاستمارة" (if questionnaire exists)
    # - "📧 إرسال للعميل" (if questionnaire is approved)
    # - "🔄 إعادة التوليد" (if questionnaire exists)


@admin.register(GeneratedQuestionnaire)
class GeneratedQuestionnaireAdmin(admin.ModelAdmin):
    list_display = ['proposal_name', 'version', 'status', 'total_features', 'total_requirements', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'token', 'created_at', 'approved_by', 'approved_at', 'generation_metadata']
    
    actions = ['approve_and_send', 'approve_only', 'reject_questionnaire']
    
    def proposal_name(self, obj):
        return obj.proposal.full_name
    proposal_name.short_description = "العميل"
    
    def approve_and_send(self, request, queryset):
        """Approve the questionnaire AND send email to client in one step"""
        for q in queryset:
            if q.status != 'draft':
                continue
            q.status = 'sent'
            q.approved_by = request.user
            q.approved_at = timezone.now()
            q.save()
            # Send email
            send_questionnaire_email_task.delay(str(q.id), request.user.id)
            q.proposal.status = 'sent'
            q.proposal.sent_by = request.user
            q.proposal.sent_at = timezone.now()
            q.proposal.save()
            self.message_user(request, f"✅📧 تم اعتماد وإرسال الاستمارة لـ {q.proposal.full_name}")
    approve_and_send.short_description = "✅📧 اعتماد + إرسال للعميل"
    
    def approve_only(self, request, queryset):
        """Approve without sending — admin will send manually later"""
        queryset.filter(status='draft').update(
            status='approved', approved_by=request.user, approved_at=timezone.now()
        )
        for q in queryset:
            q.proposal.status = 'approved'
            q.proposal.save()
    approve_only.short_description = "✅ اعتماد فقط (بدون إرسال)"
    
    def reject_questionnaire(self, request, queryset):
        """Reject — needs regeneration"""
        queryset.update(status='rejected')
    reject_questionnaire.short_description = "❌ رفض (يحتاج إعادة توليد)"
    
    # ── Preview button in change form ─────────────────────────
    # Custom template shows an iframe preview of the generated HTML
    change_form_template = 'admin/questionnaire/questionnaire_change_form.html'


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ['respondent_name', 'respondent_email', 'completion_percentage', 'submitted_at', 'proposal_link']
    readonly_fields = ['id', 'submitted_at', 'ip_address', 'user_agent', 'time_spent_seconds']
    
    def proposal_link(self, obj):
        url = reverse('admin:questionnaire_proposalrequest_change', args=[obj.questionnaire.proposal.id])
        return format_html('<a href="{}">📋 {}</a>', url, obj.questionnaire.proposal.full_name)
    proposal_link.short_description = "الطلب الأصلي"
    
    # Custom template shows a rich view of all responses, not raw JSON
    change_form_template = 'admin/questionnaire/response_detail.html'
```

#### Custom Admin Templates

Create these templates for the rich admin experience:

**`templates/admin/questionnaire/proposal_change_form.html`**
```html
{% extends "admin/change_form.html" %}
{% block after_field_sets %}
<div style="margin:20px 0;padding:20px;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0">
  <h3 style="margin-bottom:15px">🎛️ إجراءات الاستمارة</h3>
  
  {% if original.status == 'new' or original.status == 'reviewed' %}
  <a href="{% url 'admin:generate-questionnaire' original.pk %}" 
     class="button" style="background:#2563eb;color:#fff;padding:10px 20px;border-radius:8px;margin-left:10px"
     onclick="return confirm('هل تريد توليد استمارة بالذكاء الاصطناعي لهذا الطلب؟')">
    🤖 توليد الاستمارة
  </a>
  {% endif %}
  
  {% if original.questionnaires.exists %}
    {% with latest_q=original.questionnaires.last %}
    <a href="{% url 'admin:preview-questionnaire' latest_q.pk %}" target="_blank"
       class="button" style="background:#7c3aed;color:#fff;padding:10px 20px;border-radius:8px;margin-left:10px">
      👁️ معاينة الاستمارة
    </a>
    
    {% if latest_q.status == 'draft' or latest_q.status == 'approved' %}
    <a href="{% url 'admin:send-questionnaire' latest_q.pk %}"
       class="button" style="background:#059669;color:#fff;padding:10px 20px;border-radius:8px;margin-left:10px"
       onclick="return confirm('هل تريد إرسال الاستمارة للعميل عبر البريد الإلكتروني؟')">
      📧 إرسال للعميل
    </a>
    {% endif %}
    
    <a href="{% url 'admin:regenerate-questionnaire' latest_q.pk %}"
       class="button" style="background:#d97706;color:#fff;padding:10px 20px;border-radius:8px;margin-left:10px"
       onclick="return confirm('هل تريد إعادة توليد الاستمارة؟ سيتم إنشاء نسخة جديدة.')">
      🔄 إعادة التوليد
    </a>
    
    {% if latest_q.responses.exists %}
    <a href="{% url 'admin:questionnaire_questionnaireresponse_changelist' %}?questionnaire__id={{ latest_q.pk }}"
       class="button" style="background:#0891b2;color:#fff;padding:10px 20px;border-radius:8px">
      📊 عرض ردود العميل ({{ latest_q.responses.count }})
    </a>
    {% endif %}
    
    <div style="margin-top:15px;padding:10px;background:#fff;border-radius:8px;font-size:13px">
      <strong>آخر استمارة:</strong> الإصدار {{ latest_q.version }} — 
      {{ latest_q.total_features }} ميزة — {{ latest_q.total_requirements }} متطلب — 
      الحالة: {{ latest_q.get_status_display }}
    </div>
    {% endwith %}
  {% else %}
    <p style="color:#64748b;margin-top:10px">لم يتم توليد استمارة بعد لهذا الطلب.</p>
  {% endif %}
</div>
{% endblock %}
```

**`templates/admin/questionnaire/questionnaire_change_form.html`**
```html
{% extends "admin/change_form.html" %}
{% block after_field_sets %}
<div style="margin:20px 0">
  <h3>👁️ معاينة الاستمارة المولّدة</h3>
  <iframe srcdoc="{{ original.generated_html|escape }}" 
          style="width:100%;height:700px;border:2px solid #e2e8f0;border-radius:12px;margin-top:10px">
  </iframe>
</div>
{% endblock %}
```

### 3. AI Questionnaire Generation Engine

This is the core module. It takes the project description and generates a complete, professional HTML questionnaire.

#### Generation Pipeline

```python
# services/questionnaire_generator.py

class QuestionnaireGenerator:
    """
    Pipeline:
    1. Analyze project description with Claude
    2. Generate structured questionnaire data (JSON)
    3. Render JSON into the HTML template
    4. Inject JavaScript, CSS, and Nuwas branding
    5. Add submission endpoint (POST to our API)
    6. Validate and store
    """
    
    def generate(self, proposal: ProposalRequest) -> GeneratedQuestionnaire:
        # Step 1: AI Analysis & Structure Generation
        structured_data = self._generate_structure(proposal)
        
        # Step 2: Render HTML from structure
        html = self._render_html(structured_data, proposal)
        
        # Step 3: Create token and store
        token = secrets.token_urlsafe(48)
        questionnaire = GeneratedQuestionnaire.objects.create(
            proposal=proposal,
            token=token,
            token_expires_at=timezone.now() + timedelta(days=30),
            generated_html=html,
            features=structured_data['features'],
            total_features=len(structured_data['features']),
            total_requirements=sum(f['req_count'] for f in structured_data['features']),
            ai_prompt_used=structured_data['prompt_used'],
            generation_metadata=structured_data['metadata']
        )
        return questionnaire
```

#### Claude API Prompt for Structure Generation

```python
SYSTEM_PROMPT = """You are an expert requirements analyst at Nuwas Innovative IT (نواس الابتكارية لتقنية المعلومات), 
a Saudi AI and digital transformation company. Your job is to analyze a client's project idea and generate 
a comprehensive requirements elicitation questionnaire in Arabic.

You MUST output valid JSON with this exact structure:

{
  "project_title_ar": "عنوان المشروع بالعربية",
  "project_description_ar": "وصف مختصر للمشروع وأهدافه",
  "features": [
    {
      "id": 1,
      "title": "عنوان الميزة بالعربية",
      "groups": [
        {
          "label": "📂 تصنيف المجموعة",
          "reqs": [
            {
              "id": "1-1",
              "priority": "must",  // must | should | nice
              "title": "عنوان المتطلب",
              "desc": "وصف تفصيلي للمتطلب",
              "subs": [
                {
                  "type": "check",  // check | radio | text | textarea
                  "label": "نص السؤال",
                  "required": true,
                  "options": ["خيار 1", "خيار 2", "خيار 3"]
                },
                {
                  "type": "radio",
                  "label": "نص السؤال",
                  "name": "r-1-1-unique",  // unique radio group name
                  "options": ["خيار أ", "خيار ب"]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}

RULES:
1. Generate 8-12 features covering ALL aspects of the project
2. Each feature should have 3-6 requirements
3. Total requirements should be 35-60
4. Priority distribution: ~40% Must, ~35% Should, ~25% Nice
5. ALL text MUST be in Arabic (فصحى)
6. Each requirement MUST have 1-3 sub-questions
7. Sub-questions should be actionable and help translate to dev specs
8. Use relevant emojis for group labels
9. Radio group names must be globally unique (format: r-{feat_id}-{req_id}-{short_key})
10. Consider Saudi market context (ZATCA, PDPL, local payment gateways, Arabic RTL, etc.)
11. Include technical infrastructure and post-launch support as features
12. Think about integrations, security, compliance, and scalability
"""

USER_PROMPT_TEMPLATE = """Analyze the following project idea and generate a comprehensive requirements questionnaire:

**Project Type**: {project_type}
**Description**: {project_description}
**Budget Range**: {budget_range}
**Timeline**: {timeline}
**Company**: {company_name}

Generate the JSON structure now. Remember: ALL content in Arabic, 8-12 features, 35-60 total requirements."""
```

#### HTML Renderer

```python
# services/html_renderer.py

class QuestionnaireHTMLRenderer:
    """
    Takes the AI-generated JSON structure and renders it into 
    the production HTML template matching the Nuwas questionnaire design.
    
    The renderer:
    1. Loads the base HTML template (CSS + JS skeleton)
    2. Injects the Nuwas logo (base64 embedded)
    3. Builds feature sections from the JSON structure
    4. Adds the submission form (POST to /api/v1/q/{token}/submit/)
    5. Adds response collection JavaScript
    """
    
    def render(self, data: dict, token: str, proposal: ProposalRequest) -> str:
        # Load base template with CSS
        template = self._load_base_template()
        
        # Build sections HTML
        features_html = self._build_features(data['features'])
        
        # Build JavaScript with FEAT_TOTALS and FEAT_TITLES
        js_block = self._build_javascript(data['features'], token)
        
        # Assemble final HTML
        return template.format(
            project_title=data['project_title_ar'],
            project_description=data['project_description_ar'],
            client_name=proposal.full_name,
            features_html=features_html,
            js_block=js_block,
            token=token,
            submit_url=f'/api/v1/q/{token}/submit/',
            total_features=len(data['features']),
            total_reqs=sum(len(r) for f in data['features'] for g in f['groups'] for r in g['reqs'])
        )
```

### 4. Submission Handler

Modify the questionnaire HTML to include a submission form. When the user clicks "إرسال الاستمارة", JavaScript collects all responses and POSTs them:

```javascript
// Added to the generated HTML questionnaire
function submitQuestionnaire() {
    const data = {
        checked: [],      // all checked requirement IDs
        na: [],           // all N/A requirement IDs  
        sub_answers: {},   // {req_id: {radios: {name: value}, checks: [values], texts: {label: value}}}
        summary: {},       // per-feature summary
        time_spent: Math.round((Date.now() - window._startTime) / 1000),
        respondent_name: document.getElementById('respondent-name').value,
        respondent_email: document.getElementById('respondent-email').value
    };
    
    // Collect checked requirements
    document.querySelectorAll('.req-checkbox:checked').forEach(cb => {
        data.checked.push(cb.id.replace('cb-', 'req-'));
    });
    
    // Collect N/A items
    document.querySelectorAll('.na-toggle.active').forEach(na => {
        data.na.push(na.id.replace('na-', 'req-'));
    });
    
    // Collect sub-answers for each checked requirement
    data.checked.forEach(reqId => {
        const item = document.getElementById(reqId);
        if (!item) return;
        const answers = {radios: {}, checks: [], texts: {}};
        
        item.querySelectorAll('.choice-btn.selected input[type="radio"]').forEach(r => {
            answers.radios[r.name] = r.closest('.choice-btn').textContent.trim();
        });
        item.querySelectorAll('.choice-btn.selected input[type="checkbox"]').forEach(c => {
            answers.checks.push(c.closest('.choice-btn').textContent.trim());
        });
        item.querySelectorAll('.sub-input, .sub-textarea').forEach(t => {
            if (t.value.trim()) {
                const label = t.closest('.sub-q')?.querySelector('.sub-q-label')?.textContent || '';
                answers.texts[label] = t.value.trim();
            }
        });
        
        data.sub_answers[reqId] = answers;
    });
    
    // POST to API
    fetch(SUBMIT_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken()},
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) showThankYouScreen();
        else showError(result.message);
    });
}
```

### 5. Email Service

```python
# services/email_service.py

class QuestionnaireEmailService:
    
    def send_questionnaire_link(self, proposal: ProposalRequest, questionnaire: GeneratedQuestionnaire):
        """Send the tokenized questionnaire link to the prospect"""
        
        link = f"https://nuwas.ai/q/{questionnaire.token}/"
        
        subject = f"نواس | استمارة متطلبات مشروعكم — {proposal.full_name}"
        
        html_body = self._render_email_template({
            'client_name': proposal.full_name,
            'project_type': proposal.get_project_type_display(),
            'questionnaire_link': link,
            'expires_at': questionnaire.token_expires_at,
            'total_features': questionnaire.total_features,
            'total_requirements': questionnaire.total_requirements,
        })
        
        # Send via configured provider (SendGrid/Mailgun/SES)
        self._send(
            to=proposal.email,
            subject=subject,
            html=html_body,
            from_name="نواس الابتكارية",
            from_email="rfp@nuwas.ai",
            reply_to="info@nuwas.ai"
        )
        
        # Log
        EmailLog.objects.create(
            proposal=proposal,
            email_type='questionnaire_link',
            recipient_email=proposal.email,
            subject=subject,
            status='sent'
        )
    
    def send_reminder(self, proposal, questionnaire):
        """Send reminder if not completed after 3 days"""
        pass
    
    def send_thank_you(self, proposal, response):
        """Send thank you after submission"""
        pass
    
    def notify_nuwas_team(self, proposal, response):
        """Notify Nuwas team that a questionnaire was completed"""
        pass
```

### 6. Celery Tasks (Admin-Triggered, NOT Automatic)

**IMPORTANT**: These tasks are ONLY triggered by admin actions in Django Admin — never automatically on form submission.

```python
# tasks.py

@shared_task
def generate_questionnaire_task(proposal_id: str, admin_user_id: int):
    """
    Triggered ONLY by admin clicking '🤖 Generate Questionnaire' in Django Admin.
    NEVER triggered automatically on form submission.
    """
    proposal = ProposalRequest.objects.get(id=proposal_id)
    admin_user = User.objects.get(id=admin_user_id)
    
    proposal.status = 'generating'
    proposal.save()
    
    try:
        generator = QuestionnaireGenerator()
        questionnaire = generator.generate(proposal)
        
        proposal.status = 'generated'  # NOT 'sent' — admin must review first
        proposal.save()
        
        # Notify admin that generation is complete (they need to review)
        notify_admin_generation_complete(proposal, questionnaire, admin_user)
        
    except Exception as e:
        proposal.status = 'reviewed'  # revert to reviewed so admin can retry
        proposal.save()
        logger.error(f"Failed to generate questionnaire for {proposal_id}: {e}")
        notify_admin_generation_failed(proposal, str(e), admin_user)
        raise


@shared_task
def send_questionnaire_email_task(questionnaire_id: str, admin_user_id: int):
    """
    Triggered ONLY by admin clicking '📧 Send to Client' in Django Admin.
    Admin has already reviewed and approved the questionnaire.
    """
    questionnaire = GeneratedQuestionnaire.objects.get(id=questionnaire_id)
    admin_user = User.objects.get(id=admin_user_id)
    proposal = questionnaire.proposal
    
    email_service = QuestionnaireEmailService()
    email_service.send_questionnaire_link(proposal, questionnaire)
    
    questionnaire.status = 'sent'
    questionnaire.save()
    
    proposal.status = 'sent'
    proposal.sent_by = admin_user
    proposal.sent_at = timezone.now()
    proposal.save()


@shared_task
def send_reminder_emails():
    """
    Periodic task (daily): send reminders for sent but uncompleted questionnaires.
    Only sends reminders for questionnaires that were already SENT by admin.
    """
    cutoff = timezone.now() - timedelta(days=3)
    pending = GeneratedQuestionnaire.objects.filter(
        status='sent',
        created_at__lte=cutoff,
        responses__isnull=True,
        is_active=True,
    )
    for q in pending:
        QuestionnaireEmailService().send_reminder(q.proposal, q)


@shared_task  
def notify_admin_new_proposal(proposal_id: str):
    """
    Triggered when a client submits the contact form.
    Sends notification to Nuwas admin (email + optional Telegram/WhatsApp).
    """
    proposal = ProposalRequest.objects.get(id=proposal_id)
    
    # Email to admin
    admin_email = settings.NUWAS_ADMIN_EMAIL  # e.g., khalid@nuwas.ai
    subject = f"طلب عرض سعر جديد — {proposal.full_name} ({proposal.get_project_type_display()})"
    
    # Include link to Django Admin change page
    admin_url = f"{settings.SITE_URL}/admin/questionnaire/proposalrequest/{proposal.id}/change/"
    
    send_mail(
        subject=subject,
        message=f"طلب جديد من {proposal.full_name}\n\n{proposal.project_description[:200]}\n\nرابط الإدارة: {admin_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        html_message=render_to_string('emails/admin_new_proposal.html', {
            'proposal': proposal, 'admin_url': admin_url
        })
    )
```

---

## File Structure

```
nuwas-questionnaire/
├── apps/
│   └── questionnaire/
│       ├── models.py              # ProposalRequest, GeneratedQuestionnaire, QuestionnaireResponse, EmailLog
│       ├── views.py               # Public API views (form submit, questionnaire render, response submit)
│       ├── admin_views.py         # Admin-only views (generate, preview, approve, send)
│       ├── admin.py               # Rich Django Admin with custom actions + templates
│       ├── serializers.py         # DRF serializers
│       ├── urls.py                # URL routing (public + admin)
│       ├── tasks.py               # Celery tasks (admin-triggered generation + notifications)
│       └── services/
│           ├── questionnaire_generator.py   # AI generation pipeline
│           ├── html_renderer.py             # JSON → HTML renderer
│           ├── email_service.py             # Email sending (admin-triggered only)
│           └── token_service.py             # Token generation & validation
├── templates/
│   ├── admin/
│   │   └── questionnaire/
│   │       ├── proposal_change_form.html      # Custom admin form with action buttons
│   │       ├── questionnaire_change_form.html # Admin form with iframe preview
│   │       └── response_detail.html           # Rich response viewer (not raw JSON)
│   ├── questionnaires/
│   │   ├── base_template.html     # Base HTML/CSS/JS skeleton for generated forms
│   │   ├── transport-app-checklist.html    # Reference template 1
│   │   └── ai-surveillance-checklist.html  # Reference template 2
│   └── emails/
│       ├── questionnaire_link.html       # Email to client with questionnaire link
│       ├── reminder.html                 # Reminder email to client
│       ├── thank_you.html                # Thank you email after submission
│       ├── admin_new_proposal.html       # Notify admin: new proposal received
│       ├── admin_generation_complete.html # Notify admin: AI generation done, review needed
│       └── admin_response_received.html  # Notify admin: client submitted responses
├── static/
│   └── img/
│       └── nuwas-logo.png
├── config/
│   └── settings.py                # ANTHROPIC_API_KEY, EMAIL config, CELERY config, NUWAS_ADMIN_EMAIL
└── requirements.txt               # anthropic, celery, django-rest-framework, etc.
```

---

## Implementation Order

1. **Phase 1**: Create Django models + migrations
2. **Phase 2**: Build Django Admin with custom actions (generate, preview, approve, send) + custom templates
3. **Phase 3**: Build the AI generation service (Claude API integration)
4. **Phase 4**: Build the HTML renderer (JSON → HTML matching template design)
5. **Phase 5**: Create public API endpoints (contact form submit, questionnaire render, response submit)
6. **Phase 6**: Build email service (SendGrid/Mailgun integration) — admin-triggered only
7. **Phase 7**: Set up Celery tasks (async generation + admin notifications + reminders)
8. **Phase 8**: Frontend contact form enhancement (React component)
9. **Phase 9**: Admin response viewer (rich display of client answers, not raw JSON)
10. **Phase 10**: Testing + deployment

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Model | claude-sonnet-4-20250514 | Best balance of quality, speed, and cost for structured generation |
| Token Format | `secrets.token_urlsafe(48)` | 64-char URL-safe token, collision-resistant |
| Token Expiry | 30 days | Enough time for client to respond |
| HTML Storage | Full HTML in DB TextField | Self-contained, no external dependencies |
| Response Format | JSON in JSONField | Flexible, queryable in PostgreSQL |
| Async Processing | Celery + Redis | AI generation takes 10-30s, don't block HTTP |
| Email | Configurable (SendGrid default) | Flexibility for deployment |
| Logo | Base64-embedded in HTML | No external image dependencies |

---

## Security Considerations

1. **Token-based access**: No login required — questionnaire accessible via unique token only
2. **Rate limiting**: Max 5 submissions per email per day
3. **Input sanitization**: All user inputs sanitized before storage
4. **CSRF protection**: For questionnaire submission API
5. **Token expiry**: 30-day window, then link becomes invalid
6. **No PII in URL**: Token is opaque, doesn't contain email or name
7. **HTTPS only**: All questionnaire links use HTTPS
8. **Response immutability**: Once submitted, responses cannot be modified

---

## Email Template (Arabic)

The questionnaire link email should follow Nuwas branding:

```
Subject: نواس | استمارة متطلبات مشروعكم — {client_name}

Body:
- Nuwas logo header
- Greeting: "مرحباً {client_name}"
- Thank you for interest message
- Project type mentioned
- CTA button: "ابدأ تعبئة الاستمارة" → link to /q/{token}/
- Stats: "{N} ميزة رئيسية — {M} متطلب فرعي — الوقت المتوقع: 15-20 دقيقة"
- Expiry notice: "صلاحية الرابط: 30 يوم"
- Nuwas contact footer
```

---

## Testing Checklist

### Client-Facing
- [ ] Contact form submission creates ProposalRequest with status 'new'
- [ ] Contact form does NOT trigger AI generation automatically
- [ ] Admin receives notification of new proposal (email)
- [ ] Tokenized link renders the questionnaire correctly
- [ ] All checkboxes, radios, text inputs work in questionnaire
- [ ] Progress tracking updates in real-time
- [ ] Summary modal shows correct data
- [ ] Submit button collects all responses correctly
- [ ] POST to API stores responses in QuestionnaireResponse
- [ ] Token expiry is enforced (expired token → error page)
- [ ] Thank you email sends after client submission
- [ ] Mobile responsive (RTL Arabic)
- [ ] Print-friendly output

### Admin Workflow (Django Admin)
- [ ] New proposals appear in admin list with status 'new'
- [ ] Admin can review and edit project description before generation
- [ ] "🤖 Generate Questionnaire" action triggers Celery task
- [ ] Status transitions: new → reviewed → generating → generated
- [ ] Generated questionnaire appears with status 'draft'
- [ ] Admin can preview generated HTML in iframe within admin
- [ ] Admin can approve questionnaire (draft → approved)
- [ ] Admin can reject and add feedback (draft → rejected)
- [ ] Admin can regenerate (creates new version, preserves old)
- [ ] "📧 Send to Client" sends email and updates status to 'sent'
- [ ] "✅📧 Approve + Send" does both in one step
- [ ] Admin is notified when client submits responses
- [ ] Admin can view rich response detail (not raw JSON)
- [ ] Admin can compare responses across versions
- [ ] Admin notes are preserved and never shown to client
- [ ] All admin actions are logged (who did what, when)

### Security
- [ ] Admin endpoints require authentication
- [ ] Public endpoints are rate-limited
- [ ] Tokens are cryptographically random and URL-safe
- [ ] No automatic AI generation or email sending without admin action
