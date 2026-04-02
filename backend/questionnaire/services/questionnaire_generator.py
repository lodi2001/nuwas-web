import json
import logging
import re

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
1. Generate 6-8 features covering the main aspects of the project
2. Each feature should have 2-4 requirements
3. Total requirements should be 25-40
4. Priority distribution: ~40% Must, ~35% Should, ~25% Nice
5. ALL text MUST be in Arabic (فصحى)
6. Each requirement MUST have 1-2 sub-questions
7. Sub-questions should be actionable
8. Use relevant emojis for group labels
9. Radio group names must be globally unique (format: r-{feat_id}-{req_id}-{short_key})
10. Keep descriptions concise (under 50 words each)
11. Output ONLY the JSON — no markdown, no code blocks, no explanation
"""

USER_PROMPT_TEMPLATE = """Analyze the following project idea and generate a requirements questionnaire:

**Project Type**: {project_type}
**Description**: {project_description}
**Budget Range**: {budget_range}
**Timeline**: {timeline}
**Company**: {company_name}

Generate the JSON now. Output ONLY valid JSON, nothing else."""


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

        total_reqs = 0
        for f in structured_data.get("features", []):
            for g in f.get("groups", []):
                total_reqs += len(g.get("reqs", []))

        questionnaire = GeneratedQuestionnaire(
            proposal=proposal,
            version=version,
            ai_model=config.model_name,
            ai_prompt_used=structured_data.get("prompt_used", ""),
            features=structured_data.get("features", []),
            total_features=len(structured_data.get("features", [])),
            total_requirements=total_reqs,
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

        # Use at least 16384 tokens to avoid truncation
        max_tokens = max(config.max_tokens, 16384)

        message = client.messages.create(
            model=config.model_name,
            max_tokens=max_tokens,
            temperature=config.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text

        # Check if output was truncated
        if message.stop_reason == "max_tokens":
            logger.warning("AI output truncated (max_tokens reached). Attempting JSON repair.")

        # Extract JSON from response
        json_text = self._extract_json(response_text)

        # Try parsing, with repair on failure
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            logger.warning("JSON parse failed, attempting repair...")
            repaired = self._repair_json(json_text)
            data = json.loads(repaired)

        data["prompt_used"] = user_prompt
        data["metadata"] = {
            "model": config.model_name,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "stop_reason": message.stop_reason,
        }

        return data

    def _extract_json(self, text: str) -> str:
        """Extract JSON from response text, handling code blocks."""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]

        # Find the JSON object
        text = text.strip()
        start = text.find("{")
        if start > 0:
            text = text[start:]

        return text

    def _repair_json(self, text: str) -> str:
        """Attempt to repair truncated JSON by closing open structures."""
        # Remove trailing incomplete strings
        # Find the last complete structure
        text = text.rstrip()

        # Remove trailing partial content after last complete value
        # Look for last complete array item or object
        for i in range(len(text) - 1, -1, -1):
            if text[i] in ('}', ']', '"', 'e', 'l'):  # end of value
                text = text[:i + 1]
                break

        # Count open/close brackets
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')

        # Check if we're inside a string
        in_string = False
        escaped = False
        for ch in text:
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string

        # Close open string
        if in_string:
            text += '"'

        # Remove trailing comma
        text = re.sub(r',\s*$', '', text)

        # Close open brackets and braces
        text += ']' * open_brackets
        text += '}' * open_braces

        return text
