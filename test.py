import os
from mzero import RAG

def main():
    docs_folder = "./docs"
    
    print(f"--- Initializing RAG with NVIDIA provider & docs_path='{docs_folder}' ---")
    
    # Check if NVIDIA_API_KEY or NVAPI_KEY is available in env
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NVAPI_KEY")
    if api_key:
        print(f"NVIDIA API Key detected in environment: {api_key[:8]}...")
    else:
        print("Note: Neither NVIDIA_API_KEY nor NVAPI_KEY found in environment.")
        print("Please export NVIDIA_API_KEY='nvapi-...' before running, or pass api_key parameter.")

    # Initialize RAG specifying NVIDIA provider (key automatically resolved from environment)
    rag = RAG(
        docs_path=docs_folder,
        llm_provider="nvidia",
        llm_model="meta/llama-3.1-70b-instruct"
    )

    print("\n--- Configuration Details ---")
    print(f"LLM Provider : {rag.config.llm_provider}")
    print(f"LLM Model    : {rag.config.llm_model}")
    print(f"Docs Path    : {rag.config.docs_path}")
    print(f"API Key Set  : {'Yes' if rag.config.llm_api_key else 'No'}")

    question = "What features does mzero offer?"
    print(f"\n--- Querying: '{question}' ---")
    
    result = rag.ask(question)
    print("\nResponse Answer:")
    print(result.answer)
    print(f"\nConfidence Score : {result.confidence}")
    print(f"Latency          : {result.latency_ms} ms")

if __name__ == "__main__":
    main()
