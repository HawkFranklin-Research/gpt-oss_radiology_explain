import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
from gpt_oss.tokenizer import get_tokenizer
import config

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_initialized = False

def init_llm_client():
    """Initializes the LLM client by loading the model and tokenizer."""
    global _model, _tokenizer, _initialized
    if _initialized:
        return

    try:
        if not config.HF_TOKEN:
            logger.warning("HF_TOKEN is not set. Model download may fail if it's gated.")

        logger.info(f"Loading model from local path: {config.MODEL_CACHE_DIR}")

        # Load the gpt-oss model
        _model = AutoModelForCausalLM.from_pretrained(
            config.MODEL_CACHE_DIR,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True # Required by some models
        )
        
        # gpt-oss uses a specific tokenizer provided by its package
        _tokenizer = get_tokenizer()

        _initialized = True
        logger.info("LLM client initialized successfully with gpt-oss model.")
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}", exc_info=True)
        _initialized = False

def is_initialized():
    return _initialized

def generate_completion_stream(input_ids: list, max_new_tokens: int = 250, temperature: float = 0.0):
    """
    Generates a stream of tokens from the model.
    """
    if not _initialized:
        logger.error("LLM client not initialized.")
        raise RuntimeError("LLM client not initialized.")

    if temperature == 0.0:
        temperature = 1.0 # Transformers uses temp=1.0 for greedy with do_sample=False
        do_sample = False
    else:
        do_sample = True
        
    input_tensor = torch.tensor([input_ids], device=_model.device)
    streamer = TextStreamer(_tokenizer, skip_prompt=True, skip_special_tokens=True)

    # Use a separate thread for generation to stream the output
    from threading import Thread

    generation_kwargs = dict(
        input_ids=input_tensor,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=temperature,
        pad_token_id=_tokenizer.eot_token,
    )
    
    # This is a simple streaming implementation. In a real application,
    # you might want a more robust queue-based approach.
    def generate_and_stream():
        _model.generate(**generation_kwargs)

    thread = Thread(target=generate_and_stream)
    thread.start()

    # In a real-world streaming scenario, you'd yield from the streamer.
    # For this app's structure, we'll collect the full text and return it.
    # The original app processed a stream but ultimately joined it.
    # Let's adapt to that by generating the full text.
    
    output_ids = _model.generate(
        input_ids=input_tensor,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=temperature,
        pad_token_id=_tokenizer.eot_token,
    )
    
    # Decode the generated tokens, skipping the prompt
    response_text = _tokenizer.decode(output_ids[0][len(input_ids):], skip_special_tokens=True)
    return response_text
