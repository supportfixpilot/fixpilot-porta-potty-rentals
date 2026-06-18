#!/usr/bin/env python3
"""
Quick test: paste ONE Groq key and run this to verify your key works.
Usage: python3 test_groq_key.py YOUR_GROQ_API_KEY
"""
import sys, json
from urllib import request, error

if len(sys.argv) < 2:
    print("Usage: python3 test_groq_key.py YOUR_GROQ_API_KEY")
    sys.exit(1)

key = sys.argv[1].strip()
url = "https://api.groq.com/openai/v1/chat/completions"
payload = json.dumps({
    "model": "llama3-8b-8192",
    "messages": [{"role": "user", "content": "Say: KEY WORKS"}],
    "max_tokens": 20
}).encode()

req = request.Request(url, data=payload, headers={
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
})

try:
    with request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        reply = data["choices"][0]["message"]["content"].strip()
        print(f"✓ Key works! Response: {reply}")
        print(f"  Model: {data['model']}")
except error.HTTPError as e:
    print(f"✗ HTTP {e.code}: {e.read().decode()[:200]}")
except Exception as ex:
    print(f"✗ Error: {ex}")
