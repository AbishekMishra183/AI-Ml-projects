"""
Model loader module
- Supports loading a local HF model using `transformers` pipeline
- Also supports calling Hugging Face Inference API (optional) if HF_TOKEN is set
"""
from typing import Optional
import os
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from huggingface_hub import InferenceClient

@st.cache_resource
def load_local_pipeline(model_name: str, cache_dir: Optional[str] = None):
    """Load a local transformers text-generation pipeline with caching.
    Returns a pipeline ready for generation.
    """
    device = 0 if torch.cuda.is_available() else -1
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    
    # ensure pad token
    if getattr(tokenizer, "pad_token", None) is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=device
    )
    return pipe

class HostedInference:
    """Optional wrapper for Hugging Face Inference API.
    Requires HUGGINGFACE_API_TOKEN in environment or .env.
    """
    def __init__(self, token: Optional[str] = None):
        token = token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not token:
            raise RuntimeError("Hugging Face token is required for hosted inference")
        self.client = InferenceClient(token=token)

    def generate(self, model_id: str, prompt: str, params: dict) -> list:
        # Uses the inference client to call text-generation and returns list of generations
        resp = self.client.text_generation(model=model_id, inputs=prompt, parameters=params)

        # response may contain `generated_text` or list
        results = []
        if isinstance(resp, dict) and "generated_text" in resp:
            results.append(resp["generated_text"])
        elif isinstance(resp, list):
            for item in resp:
                if isinstance(item, dict) and "generated_text" in item:
                    results.append(item["generated_text"])
                elif isinstance(item, str):
                    results.append(item)
        return results
