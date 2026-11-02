
from ai_engine.auditor import audit_application

document_paths = {
    "application": "samples/application.txt",
    "identity": "samples/identity.txt",
    "certificate": "samples/certificate.txt"
}

requirements = [
    "application",
    "identity",
    "certificate",
    "income_proof"
]

# Execute the audit
result = audit_application(document_paths, requirements)

print("\n========== REJECTSHIELD AI ==========")

print("Overall status:", result["overall_status"])

print("\nExtraction methods:")
for document, method in result["extraction_methods"].items():
    print(f"- {document}: {method}")

print("\nExtracted data:")
for document, fields in result["extracted_data"].items():
    print(f"\n{document}:")
    print(fields)

print("\nAudit findings:")
for finding in result["findings"]:
    print(finding)
