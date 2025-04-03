import secrets
import os
from pathlib import Path

def generate_and_save_key():
    key = secrets.token_hex(32)
    env_path = Path(".env")

    if env_path.exists():
        if "JWT_SECRET_KEY" in env_path.read_text():
            print("JWT_SECRET_KEY already exists in .env")
            return None

    with open(env_path,"a") as f:
        f.write(f"JWT_SECRET_KEY={key}\n")
    return key

if __name__ == "__main__":
    key = generate_and_save_key()
    if key:
        print(f"Generated JWT_SECRET_KEY")

