import pytest, hmac, hashlib, json

# Placeholder for webhook verification
def verify_webhook(body, hex_sig, secret):
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, hex_sig)

@pytest.mark.integration
def test_hmac_ok():
    secret = b"topsecret"
    body = json.dumps({"event": "job.done", "id": "123"}).encode()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    assert verify_webhook(body, sig, secret)