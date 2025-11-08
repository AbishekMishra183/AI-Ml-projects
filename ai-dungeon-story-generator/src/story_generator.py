"""
Core generation helpers
- Provides a single function `generate_variations` that works for both local
pipeline and hosted inference
- Supports chunked generation (for very long stories) and seed control
"""
from typing import List, Dict, Optional, Any
from transformers import set_seed
import re

def _clean_generated_text(prompt: str, generated: str) -> str:
    """Remove prompt echo and trim to first coherent paragraph break."""
    if generated.startswith(prompt):
        text = generated[len(prompt):].strip()
    else:
        text = generated.strip()
    
    # remove excessive whitespace
    text = re.sub(r"\n\s+", "\n", text)
    return text

def generate_variations(
    pipe_or_hosted: Any,
    model_type: str,
    model_name: str,
    prompt: str,
    n_return: int = 3,
    max_new_tokens: int = 300,
    temperature: float = 0.9,
    top_p: float = 0.9,
    repetition_penalty: float = 1.1,
    seed: Optional[int] = None,
) -> List[Dict]:
    """
    Generate `n_return` variations using either a transformers pipeline (local) 
    or HostedInference wrapper.

    Returns list of dicts: {id, continuation, full_text}
    """
    if seed is not None:
        set_seed(seed)

    results = []

    params = {
        "max_new_tokens": max_new_tokens,
        "do_sample": True,
        "temperature": temperature,
        "top_p": top_p,
        "num_return_sequences": n_return,
        "repetition_penalty": repetition_penalty,
        "pad_token_id": getattr(getattr(pipe_or_hosted, 'tokenizer', None), 'eos_token_id', None),
    }

    if model_type == "local":
        # pipe_or_hosted is a transformers pipeline
        outputs = pipe_or_hosted(prompt, **{k: v for k, v in params.items() if v is not None})
        for i, out in enumerate(outputs):
            full = out.get("generated_text", out.get("text", ""))
            cont = _clean_generated_text(prompt, full)
            results.append({"id": i + 1, "continuation": cont, "full_text": full})

    elif model_type == "hosted":
        # pipe_or_hosted is HostedInference
        raw = pipe_or_hosted.generate(model_name, prompt, params)
        for i, text in enumerate(raw):
            cont = _clean_generated_text(prompt, text)
            results.append({"id": i + 1, "continuation": cont, "full_text": text})

    else:
        raise ValueError("model_type must be 'local' or 'hosted'")

    return results
