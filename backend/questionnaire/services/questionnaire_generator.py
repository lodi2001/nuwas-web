import json
import logging

import anthropic

from ..models import AIConfig, GeneratedQuestionnaire, ProposalRequest

logger = logging.getLogger(__name__)

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
              "priority": "must",
              "title": "عنوان المتطلب",
              "desc": "وصف تفصيلي للمتطلب",
              "subs": [
                {
                  "type": "check",
                  "label": "نص السؤال",
                  "required": true,
                  "options": ["خيار 1", "خيار 2", "خيار 3"]
                },
                {
                  "type": "radio",
                  "label": "نص السؤال",
                  "name": "r-1-1-unique",
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


class QuestionnaireGenerator:
    """Pipeline: Analyze → Generate JSON → Render HTML → Store."""

    def generate(self, proposal: ProposalRequest) -> GeneratedQuestionnaire:
        config = AIConfig.load()
        if not config.api_key:
            raise ValueError("API key not configured. Set it in Django Admin → AI Configuration.")

        # Step 1: Generate structure via Claude API
        structured_data = self._generate_structure(proposal, config)

        # Step 2: Render HTML
        from .html_renderer import QuestionnaireHTMLRenderer

        renderer = QuestionnaireHTMLRenderer()
        version = proposal.questionnaires.count() + 1

        questionnaire = GeneratedQuestionnaire(
            proposal=proposal,
            version=version,
            ai_model=config.model_name,
            ai_prompt_used=structured_data["prompt_used"],
            features=structured_data["features"],
            total_features=len(structured_data["features"]),
            total_requirements=sum(
                len(r)
                for f in structured_data["features"]
                for g in f["groups"]
                for r in g["reqs"]
            ),
            generation_metadata=structured_data.get("metadata", {}),
        )
        questionnaire.save()

        html = renderer.render(structured_data, questionnaire.token, proposal)
        questionnaire.generated_html = html
        questionnaire.save()

        return questionnaire

    def _generate_structure(self, proposal: ProposalRequest, config: AIConfig) -> dict:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            project_type=proposal.get_project_type_display(),
            project_description=proposal.project_description,
            budget_range=proposal.get_budget_range_display(),
            timeline=proposal.get_timeline_display(),
            company_name=proposal.company_name or "غير محدد",
        )

        client = anthropic.Anthropic(api_key=config.api_key)

        message = client.messages.create(
            model=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]

        data = json.loads(json_text.strip())

        data["prompt_used"] = user_prompt
        data["metadata"] = {
            "model": config.model_name,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "stop_reason": message.stop_reason,
        }

        return data
