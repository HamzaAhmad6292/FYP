import os
import psutil
from fastapi import FastAPI
from transformers import pipeline, set_seed
import torch
from typing import AsyncGenerator

app = FastAPI()

# Global variable for the model pipeline
pipe = None

# Set the number of threads to limit CPU usage to approximately 60% of available resources
def set_cpu_affinity():
    p = psutil.Process(os.getpid())
    cpu_count = psutil.cpu_count()
    p.cpu_affinity(list(range(int(cpu_count * 0.6))))  # Use 60% of available CPU cores

async def lifespan(app: FastAPI) -> AsyncGenerator:
    global pipe
    set_cpu_affinity()  # Set CPU affinity on startup
    # Initialize the model pipeline
    pipe = pipeline(
        "text-generation",
        model="meta-llama/Llama-3.2-3B-Instruct",
        device=-1,  # Use CPU only
        torch_dtype=torch.float32,
        max_length=2048,  # Set maximum length for generation
    )
    yield  # This indicates that the application is running
    # Cleanup on shutdown
    if pipe is not None:
        del pipe  # Release the pipeline resource

app = FastAPI(lifespan=lifespan)

@app.get("/llama3_3b/get_response/")
async def get_response(system: str, user: str, temperature: float = 1.0, max_tokens: int = 2048):
    global pipe  # Use the global pipe variable

    messages = [
        {
            "role": "system",
            "content": system
        },
        {
            "role": "user",
            "content": user
        },
    ]

    # Set seed for reproducibility (optional)
    set_seed(42)

    # Generate the response with reduced memory usage
    response = pipe(
        messages,
        max_new_tokens=max_tokens,
        temperature=temperature,
        return_full_text=False,  # Only return generated text
        pad_token_id=50256,  # Use the pad token ID for padding (Llama specific)
        top_k=50,  # Limit sampling to top-k tokens
        top_p=0.95,  # Limit sampling to top-p tokens (nucleus sampling)
    )

    response_text = response[0]['generated_text']  # Extract the generated text
    return {"response": response_text}
