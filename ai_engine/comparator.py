
import re
from difflib import SequenceMatcher
from datetime import datetime


def normalize_text(value):
    """Normalize text for comparison."""

    if not value:
        return ""

    value = str(value).lower().strip()
    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_date(value):
    """Convert common date formats into YYYY-MM-DD."""

    if not value:
        return ""

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d.%m.%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return normalize_text(value)


def similarity(a, b):
    """Calculate similarity between two normalized values."""

    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b)
    ).ratio()


def compare_documents(extracted_documents, threshold=0.90):
    """
    Compare extracted fields across documents.

    extracted_documents format:
    {
        "application": {"name": "...", "date_of_birth": "..."},
        "identity": {"name": "...", "date_of_birth": "..."}
    }
    """

    findings = []

    fields = ["name", "date_of_birth", "address"]

    for field in fields:

        values = []

        for document, data in extracted_documents.items():
            value = data.get(field)

            if value:
                values.append((document, str(value)))

        if len(values) < 2:
            continue

        reference_document, reference_value = values[0]

        for document, current_value in values[1:]:

            if field == "date_of_birth":
                first = normalize_date(reference_value)
                second = normalize_date(current_value)
                score = 1.0 if first == second else 0.0
            else:
                score = similarity(reference_value, current_value)

            if score < threshold:
                findings.append({
                    "type": "cross_document_mismatch",
                    "field": field,
                    "documents": [
                        reference_document,
                        document
                    ],
                    "values": [
                        reference_value,
                        current_value
                    ],
                    "similarity": round(score, 2),
                    "severity": "warning",
                    "explanation": (
                        f"Possible {field} discrepancy "
                        f"between {reference_document} "
                        f"and {document}."
                    )
                })

    return findings
