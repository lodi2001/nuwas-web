"""Renders AI-generated questionnaire JSON into production HTML."""

from ..models import ProposalRequest


class QuestionnaireHTMLRenderer:
    def render(self, data: dict, token: str, proposal: ProposalRequest) -> str:
        features = data.get("features", [])
        project_title = data.get("project_title_ar", "استمارة متطلبات المشروع")
        project_desc = data.get("project_description_ar", "")
        total_features = len(features)
        total_reqs = sum(
            len(r) for f in features for g in f.get("groups", []) for r in g.get("reqs", [])
        )

        features_html = self._build_features(features)
        js_block = self._build_javascript(features, token)

        return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_title} | نواس الابتكارية</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
    --teal: #2AA8DC;
    --blue: #1A5FA0;
    --ink: #1A1A2E;
    --bg: #F5F7FA;
    --card: #FFFFFF;
    --border: #E2E8F0;
    --success: #22C55E;
    --danger: #EF4444;
    --warning: #F59E0B;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Cairo',sans-serif; background:var(--bg); color:var(--ink); direction:rtl; }}

/* Header */
.sticky-header {{ position:sticky; top:0; z-index:100; background:var(--blue); color:#fff; padding:12px 20px;
    display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(0,0,0,.15); }}
.sticky-header h3 {{ font-size:1rem; }}
.progress-bar {{ width:200px; height:8px; background:rgba(255,255,255,.2); border-radius:4px; overflow:hidden; }}
.progress-fill {{ height:100%; background:var(--teal); border-radius:4px; transition:width .3s; width:0%; }}
.progress-text {{ font-size:12px; font-family:'IBM Plex Mono',monospace; }}

/* Hero */
.hero-card {{ max-width:900px; margin:30px auto; background:linear-gradient(135deg,var(--blue),var(--teal));
    color:#fff; border-radius:16px; padding:40px; text-align:center; }}
.hero-card h1 {{ font-size:1.8rem; margin-bottom:10px; font-weight:800; }}
.hero-card p {{ opacity:.9; font-size:1rem; margin-bottom:15px; }}
.hero-stats {{ display:flex; justify-content:center; gap:30px; font-family:'IBM Plex Mono',monospace; font-size:14px; }}

/* Container */
.container {{ max-width:900px; margin:0 auto; padding:0 20px 100px; }}

/* Feature Section */
.feature-section {{ background:var(--card); border-radius:16px; margin:20px 0;
    box-shadow:0 1px 4px rgba(0,0,0,.06); border:1px solid var(--border); overflow:hidden; }}
.feature-header {{ display:flex; justify-content:space-between; align-items:center; padding:18px 24px;
    cursor:pointer; user-select:none; transition:background .2s; }}
.feature-header:hover {{ background:#f8fafc; }}
.feature-header h2 {{ font-size:1.1rem; color:var(--blue); }}
.feature-counter {{ font-family:'IBM Plex Mono',monospace; font-size:13px; color:var(--teal); }}
.chevron {{ transition:transform .3s; font-size:18px; color:#94a3b8; }}
.feature-section.collapsed .feature-body {{ display:none; }}
.feature-section.collapsed .chevron {{ transform:rotate(-90deg); }}
.feature-body {{ padding:0 24px 20px; }}

/* Group */
.group-label {{ font-size:.9rem; color:var(--teal); font-weight:700; margin:16px 0 8px; padding:6px 0;
    border-bottom:1px solid var(--border); }}

/* Requirement */
.req-item {{ padding:14px 0; border-bottom:1px solid #f1f5f9; }}
.req-top {{ display:flex; align-items:flex-start; gap:12px; }}
.req-checkbox {{ width:20px; height:20px; accent-color:var(--teal); cursor:pointer; flex-shrink:0; margin-top:3px; }}
.req-content {{ flex:1; }}
.req-title {{ font-weight:700; font-size:.95rem; }}
.req-desc {{ font-size:.85rem; color:#64748b; margin-top:2px; }}

/* Priority Tags */
.p-tag {{ display:inline-block; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; margin-right:6px; }}
.p-must {{ background:#FEE2E2; color:#DC2626; }}
.p-should {{ background:#FEF3C7; color:#D97706; }}
.p-nice {{ background:#DBEAFE; color:#2563EB; }}

/* Sub Questions */
.sub-questions {{ margin-top:10px; padding:12px; background:#f8fafc; border-radius:10px; display:none; }}
.req-checkbox:checked ~ .req-content .sub-questions {{ display:block; }}
.sub-q {{ margin-bottom:12px; }}
.sub-q-label {{ font-size:.85rem; font-weight:600; margin-bottom:6px; display:block; }}
.choice-group {{ display:flex; flex-wrap:wrap; gap:8px; }}
.choice-btn {{ padding:6px 14px; border:1px solid var(--border); border-radius:8px; font-size:.85rem;
    cursor:pointer; transition:.2s; background:#fff; display:flex; align-items:center; gap:4px; }}
.choice-btn:hover {{ border-color:var(--teal); }}
.choice-btn.selected {{ background:var(--teal); color:#fff; border-color:var(--teal); }}
.choice-btn input {{ display:none; }}
.sub-input, .sub-textarea {{ width:100%; padding:10px; border:1px solid var(--border); border-radius:8px;
    font-family:'Cairo',sans-serif; font-size:.85rem; direction:rtl; }}
.sub-textarea {{ min-height:60px; resize:vertical; }}

/* N/A Toggle */
.na-toggle {{ font-size:12px; color:#94a3b8; cursor:pointer; margin-right:auto; padding:2px 8px;
    border:1px solid #e2e8f0; border-radius:6px; }}
.na-toggle.active {{ background:#f1f5f9; color:#64748b; text-decoration:line-through; }}

/* Section Summary */
.section-summary {{ display:flex; align-items:center; gap:10px; padding:12px 24px; background:#f8fafc;
    border-top:1px solid var(--border); font-size:13px; }}
.section-progress {{ flex:1; height:6px; background:#e2e8f0; border-radius:3px; overflow:hidden; }}
.section-progress-fill {{ height:100%; background:var(--teal); border-radius:3px; transition:width .3s; }}

/* Bottom Actions */
.bottom-actions {{ position:fixed; bottom:0; left:0; right:0; background:#fff; padding:12px 20px;
    box-shadow:0 -2px 8px rgba(0,0,0,.1); display:flex; justify-content:center; gap:12px; z-index:99; }}
.btn {{ padding:10px 24px; border-radius:8px; font-family:'Cairo',sans-serif; font-weight:700;
    font-size:.9rem; cursor:pointer; border:none; transition:.2s; }}
.btn-primary {{ background:var(--teal); color:#fff; }}
.btn-primary:hover {{ background:#258db8; }}
.btn-secondary {{ background:#f1f5f9; color:var(--ink); }}
.btn-danger {{ background:var(--danger); color:#fff; }}

/* Submit Section */
.submit-section {{ max-width:900px; margin:30px auto; padding:30px; background:var(--card);
    border-radius:16px; border:1px solid var(--border); }}
.submit-section h3 {{ text-align:center; margin-bottom:20px; color:var(--blue); }}
.submit-field {{ margin-bottom:15px; }}
.submit-field label {{ display:block; font-weight:600; margin-bottom:5px; }}
.submit-field input {{ width:100%; padding:10px; border:1px solid var(--border); border-radius:8px;
    font-family:'Cairo',sans-serif; }}

/* Thank you */
.thank-you {{ text-align:center; padding:80px 20px; }}
.thank-you h2 {{ color:var(--success); font-size:2rem; margin-bottom:15px; }}

/* Responsive */
@media(max-width:600px) {{
    .hero-card {{ margin:15px; padding:25px; }}
    .hero-card h1 {{ font-size:1.3rem; }}
    .hero-stats {{ flex-direction:column; gap:5px; }}
    .feature-header h2 {{ font-size:1rem; }}
    .choice-group {{ flex-direction:column; }}
}}

@media print {{
    .sticky-header, .bottom-actions {{ display:none; }}
    .feature-section.collapsed .feature-body {{ display:block; }}
    body {{ background:#fff; }}
}}
</style>
</head>
<body>

<div class="sticky-header">
    <h3>نواس | {project_title}</h3>
    <div style="display:flex;align-items:center;gap:10px">
        <span class="progress-text" id="global-progress-text">0%</span>
        <div class="progress-bar"><div class="progress-fill" id="global-progress-fill"></div></div>
    </div>
</div>

<div class="hero-card">
    <h1>{project_title}</h1>
    <p>{project_desc}</p>
    <p style="font-size:.9rem">العميل: {proposal.full_name}</p>
    <div class="hero-stats">
        <span>📊 {total_features} ميزة</span>
        <span>📋 {total_reqs} متطلب</span>
        <span>⏱ 15-20 دقيقة</span>
    </div>
</div>

<div class="container">
{features_html}

<div class="submit-section" id="submit-section">
    <h3>إرسال الاستمارة</h3>
    <div class="submit-field">
        <label>الاسم الكامل</label>
        <input type="text" id="respondent-name" value="{proposal.full_name}" required>
    </div>
    <div class="submit-field">
        <label>البريد الإلكتروني</label>
        <input type="email" id="respondent-email" value="{proposal.email}" required>
    </div>
    <div style="text-align:center;margin-top:20px">
        <button class="btn btn-primary" onclick="submitQuestionnaire()" style="font-size:1.1rem;padding:14px 50px">
            إرسال الاستمارة
        </button>
    </div>
</div>
</div>

<div class="bottom-actions">
    <button class="btn btn-secondary" onclick="toggleAll()">📂 طي/فتح الكل</button>
    <button class="btn btn-danger" onclick="resetAll()">🔄 إعادة تعيين</button>
</div>

{js_block}
</body>
</html>"""

    def _build_features(self, features: list) -> str:
        html = ""
        for feat in features:
            fid = feat["id"]
            html += f"""
<div class="feature-section" id="feat-{fid}">
    <div class="feature-header" onclick="toggleSection({fid})">
        <h2>{fid}. {feat['title']}</h2>
        <div style="display:flex;align-items:center;gap:10px">
            <span class="feature-counter" id="counter-{fid}">0 / 0</span>
            <span class="chevron">▼</span>
        </div>
    </div>
    <div class="feature-body">"""

            for group in feat.get("groups", []):
                html += f'<div class="group-label">{group["label"]}</div>'
                for req in group.get("reqs", []):
                    rid = req["id"]
                    priority = req.get("priority", "should")
                    p_class = f"p-{priority}"
                    p_label = {"must": "ضروري", "should": "مهم", "nice": "اختياري"}.get(
                        priority, "مهم"
                    )

                    subs_html = self._build_subs(req.get("subs", []), rid)

                    html += f"""
        <div class="req-item" id="req-{rid}">
            <div class="req-top">
                <input type="checkbox" class="req-checkbox" id="cb-{rid}"
                       onchange="updateProgress()">
                <div class="req-content">
                    <span class="p-tag {p_class}">{p_label}</span>
                    <span class="req-title">{req['title']}</span>
                    <div class="req-desc">{req.get('desc', '')}</div>
                    <div class="sub-questions">{subs_html}</div>
                </div>
                <span class="na-toggle" id="na-{rid}" onclick="toggleNA('{rid}')">غ/م</span>
            </div>
        </div>"""

            # Section summary bar
            html += f"""
    </div>
    <div class="section-summary">
        <span id="summary-{fid}">0 متطلب محدد</span>
        <div class="section-progress"><div class="section-progress-fill" id="spf-{fid}"></div></div>
        <span id="spct-{fid}" style="font-family:'IBM Plex Mono',monospace;font-size:12px">0%</span>
    </div>
</div>"""

        return html

    def _build_subs(self, subs: list, req_id: str) -> str:
        html = ""
        for sub in subs:
            stype = sub.get("type", "text")
            label = sub.get("label", "")
            options = sub.get("options", [])

            html += f'<div class="sub-q"><span class="sub-q-label">{label}</span>'

            if stype == "check":
                html += '<div class="choice-group">'
                for opt in options:
                    html += (
                        f'<label class="choice-btn" onclick="this.classList.toggle(\'selected\')">'
                        f'<input type="checkbox" value="{opt}"> {opt}</label>'
                    )
                html += "</div>"

            elif stype == "radio":
                name = sub.get("name", f"r-{req_id}")
                html += '<div class="choice-group">'
                for opt in options:
                    html += (
                        f'<label class="choice-btn" onclick="selectRadio(this,\'{name}\')">'
                        f'<input type="radio" name="{name}" value="{opt}"> {opt}</label>'
                    )
                html += "</div>"

            elif stype == "textarea":
                html += f'<textarea class="sub-textarea" placeholder="{label}"></textarea>'

            else:
                html += f'<input type="text" class="sub-input" placeholder="{label}">'

            html += "</div>"
        return html

    def _build_javascript(self, features: list, token: str) -> str:
        feat_totals = {}
        for f in features:
            total = sum(len(g.get("reqs", [])) for g in f.get("groups", []))
            feat_totals[f["id"]] = total

        return f"""
<script>
window._startTime = Date.now();
const FEAT_TOTALS = {feat_totals};
const SUBMIT_URL = '/api/v1/q/{token}/submit/';

function toggleSection(id) {{
    document.getElementById('feat-'+id).classList.toggle('collapsed');
}}

function toggleAll() {{
    const sections = document.querySelectorAll('.feature-section');
    const allCollapsed = [...sections].every(s => s.classList.contains('collapsed'));
    sections.forEach(s => {{ if(allCollapsed) s.classList.remove('collapsed'); else s.classList.add('collapsed'); }});
}}

function toggleNA(rid) {{
    const na = document.getElementById('na-'+rid);
    const cb = document.getElementById('cb-'+rid);
    na.classList.toggle('active');
    if(na.classList.contains('active')) {{ cb.checked = false; cb.disabled = true; }}
    else {{ cb.disabled = false; }}
    updateProgress();
}}

function selectRadio(el, name) {{
    el.closest('.choice-group').querySelectorAll('.choice-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    el.querySelector('input').checked = true;
}}

function updateProgress() {{
    let totalChecked = 0, totalReqs = 0;
    Object.keys(FEAT_TOTALS).forEach(fid => {{
        const section = document.getElementById('feat-'+fid);
        if(!section) return;
        const checked = section.querySelectorAll('.req-checkbox:checked').length;
        const total = FEAT_TOTALS[fid];
        totalChecked += checked;
        totalReqs += total;
        const pct = total > 0 ? Math.round(checked/total*100) : 0;
        const counter = document.getElementById('counter-'+fid);
        if(counter) counter.textContent = checked + ' / ' + total;
        const summary = document.getElementById('summary-'+fid);
        if(summary) summary.textContent = checked + ' متطلب محدد';
        const fill = document.getElementById('spf-'+fid);
        if(fill) fill.style.width = pct + '%';
        const pctEl = document.getElementById('spct-'+fid);
        if(pctEl) pctEl.textContent = pct + '%';
    }});
    const globalPct = totalReqs > 0 ? Math.round(totalChecked/totalReqs*100) : 0;
    document.getElementById('global-progress-fill').style.width = globalPct + '%';
    document.getElementById('global-progress-text').textContent = globalPct + '%';
}}

function resetAll() {{
    if(!confirm('هل أنت متأكد من إعادة تعيين جميع الإجابات؟')) return;
    document.querySelectorAll('.req-checkbox').forEach(cb => {{ cb.checked = false; cb.disabled = false; }});
    document.querySelectorAll('.na-toggle').forEach(na => na.classList.remove('active'));
    document.querySelectorAll('.choice-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.sub-input, .sub-textarea').forEach(t => t.value = '');
    document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
    document.querySelectorAll('input[type="checkbox"]').forEach(c => {{ if(!c.classList.contains('req-checkbox')) c.checked = false; }});
    updateProgress();
}}

function submitQuestionnaire() {{
    const name = document.getElementById('respondent-name').value.trim();
    const email = document.getElementById('respondent-email').value.trim();
    if(!name || !email) {{ alert('الرجاء إدخال الاسم والبريد الإلكتروني'); return; }}

    const data = {{
        checked_requirements: [],
        na_requirements: [],
        sub_answers: {{}},
        summary_snapshot: {{}},
        time_spent_seconds: Math.round((Date.now() - window._startTime) / 1000),
        respondent_name: name,
        respondent_email: email,
        completion_percentage: parseFloat(document.getElementById('global-progress-text').textContent)
    }};

    document.querySelectorAll('.req-checkbox:checked').forEach(cb => {{
        data.checked_requirements.push(cb.id.replace('cb-','req-'));
    }});
    document.querySelectorAll('.na-toggle.active').forEach(na => {{
        data.na_requirements.push(na.id.replace('na-','req-'));
    }});

    data.checked_requirements.forEach(reqId => {{
        const item = document.getElementById(reqId);
        if(!item) return;
        const answers = {{radios:{{}}, checks:[], texts:{{}}}};
        item.querySelectorAll('.choice-btn.selected input[type="radio"]').forEach(r => {{
            answers.radios[r.name] = r.closest('.choice-btn').textContent.trim();
        }});
        item.querySelectorAll('.choice-btn.selected input[type="checkbox"]').forEach(c => {{
            answers.checks.push(c.closest('.choice-btn').textContent.trim());
        }});
        item.querySelectorAll('.sub-input, .sub-textarea').forEach(t => {{
            if(t.value.trim()) {{
                const lbl = t.closest('.sub-q')?.querySelector('.sub-q-label')?.textContent || '';
                answers.texts[lbl] = t.value.trim();
            }}
        }});
        data.sub_answers[reqId] = answers;
    }});

    fetch(SUBMIT_URL, {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(data)
    }})
    .then(r => r.json())
    .then(result => {{
        if(result.success) {{
            document.querySelector('.container').innerHTML =
                '<div class="thank-you"><h2>✅ شكراً لكم!</h2><p>تم استلام ردكم بنجاح. سيتواصل معكم فريق نواس قريباً.</p></div>';
            document.querySelector('.bottom-actions').style.display = 'none';
        }} else {{
            alert(result.error || 'حدث خطأ. يرجى المحاولة مرة أخرى.');
        }}
    }})
    .catch(() => alert('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.'));
}}

// Initialize
updateProgress();
</script>"""
