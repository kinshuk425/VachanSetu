
import re


def _extract_line(text, labels):
    """
    Extract a value appearing after a field label.
    Supports English and selected Hindi labels.
    """

    label_pattern = "|".join(labels)

    pattern = (
        rf"(?im)^\s*(?:{label_pattern})\s*[:\-]\s*(.*?)\s*$"
    )

    match = re.search(pattern, text)

    if match:
        value = match.group(1).strip()
        return value if value else None

    return None


def extract_fields(text):
    """
    Extract basic structured fields from document text.

    This is the deterministic baseline extractor.
    Pretrained AI extraction will be added separately.
    """

    if not isinstance(text, str) or not text.strip():
        return {}

    fields = {}

    # Applicant name
    name = _extract_line(
        text,
        [
            r"Name",
            r"Full Name",
            r"Applicant Name",
            r"नाम",
            r"पूरा नाम"
        ]
    )

    if name:
        fields["name"] = name

    # Date of birth
    dob = _extract_line(
        text,
        [
            r"Date of Birth",
            r"DOB",
            r"Birth Date",
            r"जन्म तिथि",
            r"जन्म दिनांक"
        ]
    )

    if dob:
        fields["date_of_birth"] = dob

    # Address
    address = _extract_line(
        text,
        [
            r"Address",
            r"Residential Address",
            r"Permanent Address",
            r"पता",
            r"स्थायी पता"
        ]
    )

    if address:
        fields["address"] = address

    return fields
