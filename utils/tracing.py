import os

def init_tracing():
    """
    Checks if Langfuse credentials exist in the environment.
    The Langfuse Python SDK automatically picks up:
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_HOST
    """
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    
    if secret_key and public_key:
        print("[Tracing] Langfuse credentials found. Tracing enabled.")
    else:
        print("[Tracing] Langfuse credentials missing. Tracing will be inactive.")