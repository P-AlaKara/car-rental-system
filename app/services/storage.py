import os
import uuid
from typing import Optional

from flask import current_app


class StorageService:
    """Abstraction over storage backends (DigitalOcean Spaces or local filesystem).

    Provides simple APIs to upload bytes/streams and build public URLs.
    """

    def __init__(self,
                 provider: str,
                 upload_folder: str,
                 spaces_bucket: Optional[str] = None,
                 spaces_endpoint_url: Optional[str] = None,
                 spaces_region: Optional[str] = None,
                 spaces_access_key_id: Optional[str] = None,
                 spaces_secret_access_key: Optional[str] = None,
                 spaces_cdn_base_url: Optional[str] = None) -> None:
        self.provider = (provider or 'local').lower()
        self.upload_folder = upload_folder or 'uploads'

        self.bucket = spaces_bucket
        self.endpoint_url = spaces_endpoint_url
        self.region = spaces_region
        self.access_key_id = spaces_access_key_id
        self.secret_access_key = spaces_secret_access_key
        self.cdn_base_url = spaces_cdn_base_url.rstrip('/') if spaces_cdn_base_url else None

        self._s3 = None
        if self.provider == 'spaces' and self.bucket and self.endpoint_url and self.access_key_id and self.secret_access_key:
            # Lazy import boto3 only when needed
            import boto3
            self._s3 = boto3.client(
                's3',
                region_name=self.region,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
            )

    # --------------- Public API ---------------
    def generate_key(self, prefix: str, original_filename: str) -> str:
        safe_name = original_filename.replace(' ', '_')
        unique = uuid.uuid4().hex[:8]
        return f"{prefix.rstrip('/')}/{unique}_{safe_name}"

    def url_for(self, key: str) -> str:
        if self.provider == 'spaces' and self.bucket:
            if self.cdn_base_url:
                return f"{self.cdn_base_url}/{key}"
            # Build region-specific URL if endpoint is provided, else fallback to standard pattern
            base = self.endpoint_url.rstrip('/') if self.endpoint_url else ''
            # If endpoint is something like https://nyc3.digitaloceanspaces.com, use path-style
            if base:
                return f"{base}/{self.bucket}/{key}"
            # Fallback: https://{bucket}.{region}.digitaloceanspaces.com/{key}
            region = self.region or 'nyc3'
            return f"https://{self.bucket}.{region}.digitaloceanspaces.com/{key}"
        # Local provider -> serve via /uploads route
        return f"/uploads/{key}"

    def url_to_key(self, url: str) -> Optional[str]:
        if not url:
            return None
        # Spaces URLs (via CDN base)
        if self.cdn_base_url and url.startswith(self.cdn_base_url + '/'):
            return url[len(self.cdn_base_url) + 1 :]
        # Spaces URLs (via endpoint + bucket path-style)
        if self.endpoint_url and self.bucket:
            prefix = f"{self.endpoint_url.rstrip('/')}/{self.bucket}/"
            if url.startswith(prefix):
                return url[len(prefix):]
        # Spaces URL without endpoint configured but using standard bucket.region style
        if self.bucket and self.region:
            alt_prefix = f"https://{self.bucket}.{self.region}.digitaloceanspaces.com/"
            if url.startswith(alt_prefix):
                return url[len(alt_prefix):]
        # Local URLs
        if url.startswith('/uploads/'):
            return url[len('/uploads/'):]
        if url.startswith('/static/uploads/'):
            return url[len('/static/uploads/'):]
        return None

    def upload_fileobj(self, fileobj, key: str, content_type: Optional[str] = None) -> str:
        if self._s3:
            extra = {}
            if content_type:
                extra['ContentType'] = content_type
            self._s3.put_object(Bucket=self.bucket, Key=key, Body=fileobj.read(), ACL='public-read', **extra)
            return self.url_for(key)
        # Local
        abs_path = self._ensure_local_path_for_key(key)
        with open(abs_path, 'wb') as f:
            f.write(fileobj.read())
        return self.url_for(key)

    def upload_bytes(self, data: bytes, key: str, content_type: Optional[str] = None) -> str:
        if self._s3:
            extra = {}
            if content_type:
                extra['ContentType'] = content_type
            self._s3.put_object(Bucket=self.bucket, Key=key, Body=data, ACL='public-read', **extra)
            return self.url_for(key)
        abs_path = self._ensure_local_path_for_key(key)
        with open(abs_path, 'wb') as f:
            f.write(data)
        return self.url_for(key)

    def delete(self, key_or_url: str) -> bool:
        key = self.url_to_key(key_or_url) or key_or_url
        if self._s3:
            try:
                self._s3.delete_object(Bucket=self.bucket, Key=key)
                return True
            except Exception:
                return False
        abs_path = self._local_path_for_key(key)
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
                return True
        except Exception:
            return False
        return False

    # --------------- Internals ---------------
    def _local_path_for_key(self, key: str) -> str:
        base = os.path.join(current_app.root_path, '..', self.upload_folder)
        return os.path.abspath(os.path.join(base, key))

    def _ensure_local_path_for_key(self, key: str) -> str:
        path = self._local_path_for_key(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path


def get_storage() -> StorageService:
    """Return a cached StorageService for the current app."""
    app = current_app
    svc: Optional[StorageService] = app.extensions.get('storage_service') if hasattr(app, 'extensions') else None
    if svc:
        return svc

    cfg = app.config
    provider = 'spaces' if cfg.get('SPACES_BUCKET') else 'local'
    svc = StorageService(
        provider=provider,
        upload_folder=cfg.get('UPLOAD_FOLDER', 'uploads'),
        spaces_bucket=cfg.get('SPACES_BUCKET'),
        spaces_endpoint_url=cfg.get('SPACES_ENDPOINT_URL'),
        spaces_region=cfg.get('SPACES_REGION'),
        spaces_access_key_id=cfg.get('SPACES_ACCESS_KEY_ID'),
        spaces_secret_access_key=cfg.get('SPACES_SECRET_ACCESS_KEY'),
        spaces_cdn_base_url=cfg.get('SPACES_CDN_BASE_URL'),
    )

    if not hasattr(app, 'extensions'):
        app.extensions = {}
    app.extensions['storage_service'] = svc
    return svc

