from fastapi import FastAPI
from transformers import pipeline
import torch

app = FastAPI()

# Define the pipeline globally to avoid reloading on each request
pipe = None

def gemma_pipeline(temperature=1, max_tokens=2048):
    global pipe  # Use the global pipe variable
    if pipe is None:
        device = 0 if torch.cuda.is_available() else -1  # Set device based on GPU availability
        pipe = pipeline(
            "text-generation",
            model="google/gemma-2-2b",
            device=device,
            temperature=temperature
        )
    return pipe

@app.get("/get_response/")
def get_response(prompt: str, temperature: float = 1.0, max_tokens: int = 2048):
    # Get the pipeline
    pipe = gemma_pipeline(temperature=temperature, max_tokens=max_tokens)
    
    # Generate a response using the prompt
    response = pipe(prompt, max_length=max_tokens)
    
    return {"response": response}
