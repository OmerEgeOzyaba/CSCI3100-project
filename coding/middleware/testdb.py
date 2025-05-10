import base64
import os
import hashlib

def generate_scrypt_hash(password):
    # Generate a random salt (16 bytes recommended)
    salt = os.urandom(16)
    
    # Derive the key using scrypt
    derived_key = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt,
        n=32768,  # CPU/memory cost
        r=8,      # Block size
        p=1,      # Parallelization
        dklen=64  # Length of the derived key
    )
    
    # Format as "scrypt:N:r:p$salt$hash"
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    hash_b64 = base64.b64encode(derived_key).decode('utf-8')
    
    return f"scrypt:32768:8:1${salt_b64}${hash_b64}"

# Generate hash for your password
password = "Kennyho050505!"
hashed_password = generate_scrypt_hash(password)
print(hashed_password)