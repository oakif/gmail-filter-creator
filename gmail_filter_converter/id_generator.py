import time
from datetime import datetime, timezone


def generate_filter_id() -> str:
    """Generate a Gmail filter ID in the expected format.

    Gmail filter IDs follow the pattern: tag:mail.google.com,2008:filter:{timestamp_ms}
    where timestamp_ms is the current time in milliseconds since epoch.
    """
    timestamp_ms = int(time.time() * 1000)
    return f'tag:mail.google.com,2008:filter:{timestamp_ms}'


def generate_timestamp() -> str:
    """Generate an ISO 8601 timestamp in UTC.

    Returns a timestamp in the format: YYYY-MM-DDTHH:MM:SSZ
    This matches Gmail's timestamp format for metadata.
    """
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
