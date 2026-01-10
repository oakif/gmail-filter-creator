from gmail_filter_converter.models import Filter, FilterActions, FilterCriteria
from gmail_filter_converter.name_generator import (
    generate_filter_name,
    _extract_domain_or_truncate,
    _get_actions_description,
    _get_criteria_description,
    _truncate,
)


def test_generate_name_from_email_and_label():
    criteria = FilterCriteria(from_="auto-confirm@amazon.com")
    actions = FilterActions(label="Shopping/Amazon")

    name = generate_filter_name(criteria, actions)
    assert name == "amazon.com → Shopping/Amazon"


def test_generate_name_without_label():
    criteria = FilterCriteria(from_="newsletter@example.com")
    actions = FilterActions(should_archive=True, should_mark_as_read=True)

    name = generate_filter_name(criteria, actions)
    assert name == "example.com → archive, mark read"


def test_generate_name_subject_only():
    criteria = FilterCriteria(subject="Your receipt")
    actions = FilterActions(label="Receipts")

    name = generate_filter_name(criteria, actions)
    assert name == "Your receipt → Receipts"


def test_generate_name_has_the_word_fallback():
    criteria = FilterCriteria(has_the_word="invoice attached")
    actions = FilterActions(label="Invoices")

    name = generate_filter_name(criteria, actions)
    assert name == "invoice attached → Invoices"


def test_generate_name_to_address():
    criteria = FilterCriteria(to="support@mycompany.com")
    actions = FilterActions(label="Support")

    name = generate_filter_name(criteria, actions)
    assert name == "to:mycompany.com → Support"


def test_generate_name_no_criteria():
    criteria = FilterCriteria()
    actions = FilterActions(label="Test")

    name = generate_filter_name(criteria, actions)
    assert name == "(no criteria) → Test"


def test_generate_name_no_action():
    criteria = FilterCriteria(from_="test@example.com")
    actions = FilterActions()

    name = generate_filter_name(criteria, actions)
    assert name == "example.com → (no action)"


def test_extract_domain():
    assert _extract_domain_or_truncate("user@domain.com") == "domain.com"
    assert _extract_domain_or_truncate("complex@sub.domain.org") == "sub.domain.org"
    assert _extract_domain_or_truncate("no-at-sign") == "no-at-sign"


def test_truncate():
    assert _truncate("short") == "short"
    assert len(_truncate("a" * 50, max_len=30)) == 30
    assert _truncate("a" * 50, max_len=30).endswith("...")


def test_truncate_strips_quotes():
    assert _truncate('"quoted text"') == "quoted text"
    assert _truncate("'single quoted'") == "single quoted"


def test_get_criteria_description_priority():
    # from_ takes priority over others
    criteria = FilterCriteria(
        from_="test@example.com",
        subject="Some subject",
        has_the_word="some words",
    )
    assert _get_criteria_description(criteria) == "example.com"


def test_get_actions_description_label_priority():
    actions = FilterActions(
        label="My Label",
        should_archive=True,
        should_mark_as_read=True,
    )
    assert _get_actions_description(actions) == "My Label"


def test_get_actions_description_boolean_actions():
    actions = FilterActions(
        should_star=True,
        should_trash=True,
    )
    assert _get_actions_description(actions) == "star, trash"


def test_get_actions_description_never_spam():
    actions = FilterActions(should_never_spam=True)
    assert _get_actions_description(actions) == "never spam"


def test_manual_name_override():
    filter_obj = Filter(
        name="My Custom Name",
        criteria=FilterCriteria(from_="test@example.com"),
        actions=FilterActions(label="Test"),
    )
    assert filter_obj.get_name() == "My Custom Name"


def test_auto_generated_name():
    filter_obj = Filter(
        criteria=FilterCriteria(from_="test@example.com"),
        actions=FilterActions(label="Test"),
    )
    assert filter_obj.get_name() == "example.com → Test"


def test_filter_name_field_is_optional():
    filter_obj = Filter(
        criteria=FilterCriteria(from_="test@example.com"),
        actions=FilterActions(label="Test"),
    )
    assert filter_obj.name is None
    # But get_name() still returns auto-generated name
    assert filter_obj.get_name() is not None
