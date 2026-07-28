"""Basic 1-line Python usage example for mzero."""

import os
from mzero import RAG

# 1. Create a dummy documentation folder
os.makedirs("./sample_docs", exist_ok=True)
with open("./sample_docs/policy.txt", "w", encoding="utf-8") as f:
    f.write("mzero supports a 30-day money-back refund guarantee for all subscription tiers.")

# 2. Initialize mzero with 1 line of code
rag = RAG("./sample_docs")

# 3. Ask question
response = rag.ask("What is the refund policy?")

print("\n--- Answer ---")
print(response.answer)

print("\n--- Citations ---")
for cite in response.citations:
    print(f"File: {cite.source_file} | Snippet: {cite.snippet}")

print("\n--- Telemetry Stats ---")
print(rag.stats())
