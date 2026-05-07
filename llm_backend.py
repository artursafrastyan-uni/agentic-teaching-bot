import os
from llama_cpp import Llama

# --- Model Documentation ---
# Model Name: Meta-Llama-3-8B-Instruct
# Quantization: Q4_K_M (4-bit quantization for CPU/small-GPU efficiency)
# Context Length: 4096 tokens (Llama-3 natively supports 8192, using 4096 here for RAM efficiency)
# Backend: llama.cpp (via the llama-cpp-python library)
# ---------------------------

# Global variable to cache the model in memory so it's only loaded once
_llm = None

def get_llm():
    """
    Initializes and returns the Llama model instance. 
    Loads the model into memory only upon the first call.
    """
    global _llm
    if _llm is None:
        # Determine the absolute path to the .gguf model file in this directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
        print("Loading local Llama-3 model into memory (this might take a few seconds)...")
        
        # Initialize the Llama model
        _llm = Llama(
            model_path=model_path,
            n_ctx=4096,           # Context window size
            n_gpu_layers=0,       # 0 means CPU-only. Increase this if you have a GPU (e.g., 30 for offloading layers)
            verbose=False         # Set to True if you want to see detailed C++ backend logs
        )
        print("Model loaded successfully!")
        
    return _llm


def generate(messages: list, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """
    Generates a response from the local Llama-3 model using a chat interface.
    
    Args:
        messages (list): A list of message dictionaries containing the conversation history.
                         Example: [{"role": "system", "content": "You are a bot."}, 
                                   {"role": "user", "content": "Hello"}]
        temperature (float): Controls the creativity/randomness of the model. 
                             Lower is more deterministic (good for data extraction).
        max_tokens (int): The maximum length of the generated output.
        
    Returns:
        str: The generated text response.
    """
    llm = get_llm()
    
    # llama-cpp-python has a built-in create_chat_completion method that automatically 
    # formats the `messages` list using the chat template embedded in the Llama-3 GGUF file.
    response = llm.create_chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    # Extract and return the generated text content
    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # A quick standalone test to verify the model is working correctly
    print("--- Testing the LLM Backend ---")
    test_messages = [
        {"role": "system", "content": "You are a concise teaching assistant."},
        {"role": "user", "content": "Explain what Natural Language Processing is in exactly one short sentence."}
    ]
    
    try:
        answer = generate(test_messages, temperature=0.3, max_tokens=100)
        print(f"\nResponse:\n{answer}")
    except Exception as e:
        print(f"\nError occurred: {e}")
