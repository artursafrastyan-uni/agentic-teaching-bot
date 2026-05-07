import os
from llama_cpp import Llama
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'Meta-Llama-3-8B-Instruct.Q4_K_M.gguf')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f'Model file not found at: {model_path}')
        print('Loading local Llama-3 model into memory (this might take a few seconds)...')
        _llm = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=0, verbose=False)
        print('Model loaded successfully!')
    return _llm

def generate(messages: list, temperature: float=0.7, max_tokens: int=1024) -> str:
    llm = get_llm()
    response = llm.create_chat_completion(messages=messages, temperature=temperature, max_tokens=max_tokens)
    return response['choices'][0]['message']['content']
