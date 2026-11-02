
from ai_engine.ocr import extract_text
from ai_engine.extractor import extract_fields
from ai_engine.llm_extractor import extract_fields_with_gemini
from ai_engine.comparator import compare_documents


def audit_application(document_paths, requirements):
    """
    Main RejectShield audit function.

    Uses Gemini for intelligent extraction.
    Falls back to the existing rule-based extractor
    if the API is unavailable.
    """

    documents = {}
    findings = []
    extraction_methods = {}

    # Step 1: Extract and understand uploaded documents
    for document_name, file_path in document_paths.items():

        try:
            text = extract_text(file_path)

            if not text.strip():
                raise ValueError("Document contains no readable text.")

            # Existing deterministic extraction
            fallback_fields = extract_fields(text)

            # Try Gemini extraction
            try:
                ai_fields = extract_fields_with_gemini(text)
                extraction_methods[document_name] = "gemini"

            except Exception:
                ai_fields = {}
                extraction_methods[document_name] = "rule_based_fallback"

                findings.append({
                    "type": "ai_extraction_fallback",
                    "document": document_name,
                    "severity": "warning",
                    "explanation": (
                        "AI extraction was unavailable. "
                        "Rule-based extraction was used instead."
                    )
                })

            # Prefer AI values; use deterministic extraction
            # when the AI did not return a field.
            fields = {}

            for field in ["name", "date_of_birth", "address"]:
                fields[field] = (
                    ai_fields.get(field)
                    or fallback_fields.get(field)
                )

            fields["document_type"] = (
                ai_fields.get("document_type")
                or document_name
            )

            # Remove fields that could not be extracted
            fields = {
                key: value
                for key, value in fields.items()
                if value is not None
            }

            if not any(
                fields.get(field)
                for field in ["name", "date_of_birth", "address"]
            ):
                findings.append({
                    "type": "extraction_incomplete",
                    "document": document_name,
                    "severity": "warning",
                    "explanation": (
                        "No supported fields could be extracted. "
                        "Manual review is recommended."
                    )
                })

            documents[document_name] = fields

        except Exception:
            findings.append({
                "type": "document_processing_error",
                "document": document_name,
                "severity": "warning",
                "explanation": (
                    "The document could not be processed. "
                    "Please check the file and try again."
                )
            })

    # Step 2: Check required documents
    for required_document in requirements:

        if required_document not in document_paths:
            findings.append({
                "type": "missing_document",
                "document": required_document,
                "severity": "error",
                "explanation": (
                    f"Required document '{required_document}' "
                    "was not uploaded."
                )
            })

        elif required_document not in documents:
            findings.append({
                "type": "document_unreadable",
                "document": required_document,
                "severity": "error",
                "explanation": (
                    f"Required document '{required_document}' "
                    "could not be processed."
                )
            })

    # Step 3: Compare successfully processed documents
    findings.extend(compare_documents(documents))

    # Step 4: Prepare audit report
    return {
        "overall_status": (
            "NEEDS_REVIEW" if findings else "READY_FOR_REVIEW"
        ),
        "documents_received": list(document_paths.keys()),
        "documents_processed": list(documents.keys()),
        "extraction_methods": extraction_methods,
        "extracted_data": documents,
        "findings": findings
    }
