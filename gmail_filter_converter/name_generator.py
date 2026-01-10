from .models import FilterActions, FilterCriteria


def generate_filter_name(criteria: FilterCriteria, actions: FilterActions) -> str:
    criteria_part = _get_criteria_description(criteria)
    actions_part = _get_actions_description(actions)
    return f"{criteria_part} → {actions_part}"


def _get_criteria_description(criteria: FilterCriteria) -> str:
    """Build criteria description. Priority: from > to > subject > has_the_word."""
    if criteria.from_:
        return _extract_domain_or_truncate(criteria.from_)
    if criteria.to:
        return f"to:{_extract_domain_or_truncate(criteria.to)}"
    if criteria.subject:
        return _truncate(criteria.subject)
    if criteria.has_the_word:
        return _truncate(criteria.has_the_word)
    return "(no criteria)"


def _get_actions_description(actions: FilterActions) -> str:
    """Build actions description. Priority: label > boolean actions."""
    if actions.label:
        return actions.label

    action_names = []
    if actions.should_archive:
        action_names.append("archive")
    if actions.should_mark_as_read:
        action_names.append("mark read")
    if actions.should_star:
        action_names.append("star")
    if actions.should_trash:
        action_names.append("trash")
    if actions.should_never_spam:
        action_names.append("never spam")

    if action_names:
        return ", ".join(action_names)

    return "(no action)"


def _extract_domain_or_truncate(email_or_address: str) -> str:
    """Extract domain from email address, or truncate if it's a pattern."""
    if "@" in email_or_address:
        domain = email_or_address.split("@")[-1]
        return domain
    return _truncate(email_or_address)


def _truncate(text: str, max_len: int = 30) -> str:
    """Truncate text with ellipsis if too long."""
    text = text.strip('"').strip("'")
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
