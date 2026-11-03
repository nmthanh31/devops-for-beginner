import hashlib
import json


def generate_alert_fingerprint(
    labels: dict[str, str],
    status: str,
    starts_at: str | None = None,
) -> str:
    sorted_labels: dict[str, str] = {}
    for key in sorted(labels):
        sorted_labels[key] = str(labels[key])

    if starts_at is None:
        normalized_starts_at = ""
    else:
        normalized_starts_at = starts_at

    fingerprint_payload = {
        "labels": sorted_labels,
        "status": status.lower(),
        "starts_at": normalized_starts_at,
    }

    serialized_payload = json.dumps(
        fingerprint_payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()
