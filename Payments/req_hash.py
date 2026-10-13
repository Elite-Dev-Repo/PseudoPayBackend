import hashlib
import json

def generate_request_hash(request):
    canonical = json.dumps(
        request,
        sort_keys=True
    )
    hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return hash