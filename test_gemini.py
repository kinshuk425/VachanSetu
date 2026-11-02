from ai_engine.ocr import extract_text
from ai_engine.llm_extractor import extract_fields_with_gemini

text = extract_text("samples/application.txt")

result = extract_fields_with_gemini(text)

print("\n========== GEMINI EXTRACTION ==========")
print(result)