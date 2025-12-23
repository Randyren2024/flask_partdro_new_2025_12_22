import partdro.extensions as extensions
from config import Config
import httpx

def create_bucket(bucket_id: str, public: bool = True):
    url = f"{Config.SUPABASE_URL}/storage/v1/bucket"
    headers = {
        "apikey": Config.SUPABASE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    body = {"name": bucket_id, "public": public}
    resp = httpx.post(url, json=body, headers=headers, timeout=10)
    if resp.status_code in (200, 201):
        return resp.json()
    if resp.status_code == 409:
        return {"status": 409, "message": "Bucket already exists"}
    resp.raise_for_status()
    return resp.json()

def upload(bucket_id: str, path: str, data: bytes, content_type: str | None = None, upsert: bool = True):
    options = {}
    if content_type:
        options["contentType"] = content_type
    options["upsert"] = "true" if upsert else "false"
    return extensions.supabase.storage.from_(bucket_id).upload(path, data, options)

def get_public_url(bucket_id: str, path: str):
    return extensions.supabase.storage.from_(bucket_id).get_public_url(path)
