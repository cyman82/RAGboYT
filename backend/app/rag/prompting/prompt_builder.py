def build_prompt(
    question: str,
    context: str,
    template: str | None = None,
    confidence_hint: str | None = None,
    evidence_snippets: str | None = None,
) -> str:
    """
    Build a grounded prompt for the LLM with transcript context.
    """

    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("question is required")

    cleaned_context = context.strip()

    prompt_template = template or _default_template()

    return prompt_template.format(
        question=cleaned_question,
        context=cleaned_context,
        rules=_grounding_rules(),
        confidence_hint=confidence_hint or "unknown",
        evidence_snippets=evidence_snippets or "- None",
    )


def _default_template() -> str:
    return (
        "You are a careful assistant answering questions about a YouTube video.\n"
        "Use ONLY the transcript context provided below.\n"
        "If evidence is partial, answer briefly and say what is missing.\n\n"
        "Transcript context:\n"
        "{context}\n\n"
        "Question:\n"
        "{question}\n\n"
        "Evidence snippets (use if relevant):\n"
        "{evidence_snippets}\n\n"
        "Output format:\n"
        "Answer:\n"
        "<two concise paragraphs, about double the previous length>\n"
        "Confidence: {confidence_hint}\n"
        "Follow-up: <one suggested question>\n\n"
        "Rules:\n"
        "{rules}\n"
    )


def _grounding_rules() -> str:
    rules = [
        "Answer only from the transcript context.",
        "Do not invent facts or timestamps.",
        "If the answer is not in the context, say you do not know.",
        "Do not add timestamps inside the answer text.",
        "Grounding timestamps will be shown separately in the UI.",
        "Prefer quoting or paraphrasing the transcript when possible.",
    ]

    return "\n".join(f"- {rule}" for rule in rules)
