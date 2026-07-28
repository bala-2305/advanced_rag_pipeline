from mzero import RAG

# Zero-configuration initialization: automatically loads .env and resolves NVIDIA_API_KEY
rag = RAG(docs_path="./docs")

# Ask question using knowledge base
result = rag.ask("What is your name?")

print("Answer:")
print(result.answer)
print(f"\nConfidence: {result.confidence}")
print(f"Latency: {result.latency_ms} ms")
