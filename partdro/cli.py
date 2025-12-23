import click
from partdro.services.db import instruments_count
from partdro.services.schema import fetch_openapi_schema, list_columns_from_openapi, list_tables_from_openapi
import partdro.extensions as extensions
from config import Config
from urllib.parse import urlparse
import httpx
from partdro.services.storage import create_bucket, upload, get_public_url

def register_cli(app):
    @app.cli.command("health")
    def health():
        count = instruments_count()
        click.echo(f"ok count={count}")

    @app.cli.command("schema")
    @click.argument("table")
    def schema(table):
        openapi = fetch_openapi_schema()
        cols = list_columns_from_openapi(openapi, table)
        if not cols:
            click.echo(f"table={table} not found or no columns parsed")
        else:
            click.echo(f"table={table} columns={','.join(cols)}")

    @app.cli.command("tables")
    def tables():
        openapi = fetch_openapi_schema()
        tables = list_tables_from_openapi(openapi)
        click.echo(f"tables={','.join(tables)}")

    @app.cli.command("schemas")
    def schemas():
        openapi = fetch_openapi_schema()
        schemas = (
            openapi.get("components", {})
            .get("schemas", {})
        )
        names = list(schemas.keys())
        click.echo(f"schemas={','.join(sorted(names))}")

    @app.cli.command("columns")
    @click.argument("table")
    def columns(table):
        openapi = fetch_openapi_schema()
        cols = list_columns_from_openapi(openapi, table)
        click.echo(f"columns({table}) count={len(cols)} {','.join(cols[:50])}")

    @app.cli.command("check-thumbnails")
    @click.option("--limit", default=50, help="Max rows to check")
    def check_thumbnails(limit):
        supa_host = urlparse(Config.SUPABASE_URL).netloc
        resp = extensions.supabase.table("product").select("id,thumbnail").limit(int(limit)).execute()
        rows = getattr(resp, "data", []) or []
        if not rows:
            click.echo("no product rows found")
            return
        ok_count = 0
        fail = []
        for r in rows:
            pid = r.get("id")
            url = (r.get("thumbnail") or "").strip()
            if not url:
                fail.append((pid, "empty"))
                continue
            parsed = urlparse(url)
            is_same_host = parsed.netloc == supa_host
            is_storage_path = parsed.path.startswith("/storage/v1/object/")
            if is_same_host and is_storage_path:
                ok_count += 1
            else:
                fail.append((pid, f"host={parsed.netloc} path={parsed.path}"))
        click.echo(f"checked={len(rows)} ok={ok_count} fail={len(fail)}")
        for pid, reason in fail[:50]:
            click.echo(f" - id={pid} reason={reason}")

    @app.cli.command("migrate-thumbnails")
    @click.option("--bucket", default="public-assets", help="Target bucket")
    @click.option("--limit", default=50, help="Max rows to migrate")
    @click.option("--dry-run", is_flag=True, default=False, help="Only print, do not write")
    def migrate_thumbnails(bucket, limit, dry_run):
        try:
            create_bucket(bucket, True)
        except Exception:
            pass
        supa_host = urlparse(Config.SUPABASE_URL).netloc
        resp = extensions.supabase.table("product").select("id,thumbnail").limit(int(limit)).execute()
        rows = getattr(resp, "data", []) or []
        migrated = 0
        failed = 0
        for r in rows:
            pid = r.get("id")
            url = (r.get("thumbnail") or "").strip()
            if not url:
                failed += 1
                click.echo(f"id={pid} skip empty")
                continue
            parsed = urlparse(url)
            is_same_host = parsed.netloc == supa_host and parsed.path.startswith("/storage/v1/object/")
            if is_same_host:
                click.echo(f"id={pid} ok already bucket")
                continue
            try:
                resp_img = httpx.get(url, timeout=15)
                resp_img.raise_for_status()
                data = resp_img.content
                ct = resp_img.headers.get("content-type") or "image/jpeg"
                ext = ".jpg"
                if "png" in ct:
                    ext = ".png"
                elif "webp" in ct:
                    ext = ".webp"
                path = f"products/{pid}{ext}"
                if dry_run:
                    public_url = get_public_url(bucket, path)
                    click.echo(f"id={pid} would upload {len(data)} bytes to {bucket}/{path} -> {public_url}")
                    migrated += 1
                    continue
                upload(bucket, path, data, content_type=ct, upsert=True)
                public_url = get_public_url(bucket, path)
                extensions.supabase.table("product").update({"thumbnail": public_url}).eq("id", pid).execute()
                migrated += 1
                click.echo(f"id={pid} migrated -> {public_url}")
            except Exception as e:
                failed += 1
                click.echo(f"id={pid} fail {e}")
        click.echo(f"migrated={migrated} failed={failed} total={len(rows)}")

    @app.cli.command("debug-storage")
    @click.option("--bucket", default="public-assets", help="Bucket to test")
    def debug_storage(bucket):
        supa_host = urlparse(Config.SUPABASE_URL).netloc
        click.echo(f"supa_host={supa_host} bucket={bucket}")
        # List buckets via SDK if possible
        try:
            buckets = extensions.supabase.storage.list_buckets()  # type: ignore[attr-defined]
            click.echo(f"list_buckets sdk_ok count={len(buckets)}")
        except Exception as e:
            click.echo(f"list_buckets sdk_fail {e}")
        # Ensure bucket exists
        try:
            create_bucket(bucket, True)
            click.echo("create_bucket ok or exists")
        except Exception as e:
            click.echo(f"create_bucket fail {e}")
        # Upload small text
        try:
            data = b"storage-diagnostic"
            path = "diag/test.txt"
            upload(bucket, path, data, content_type="text/plain", upsert=True)
            click.echo("upload ok")
        except Exception as e:
            click.echo(f"upload fail {e}")
        # List objects under diag/
        try:
            listing = extensions.supabase.storage.from_(bucket).list("diag")
            click.echo(f"list diag count={len(listing)}")
        except Exception as e:
            click.echo(f"list fail {e}")
        # Public URL check
        try:
            public_url = extensions.supabase.storage.from_(bucket).get_public_url("diag/test.txt")
            click.echo(f"public_url={public_url}")
            r = httpx.get(public_url, timeout=10)
            click.echo(f"public_fetch status={r.status_code} bytes={len(r.content)}")
        except Exception as e:
            click.echo(f"public_fetch fail {e}")
        # Signed URL check
        try:
            signed = extensions.supabase.storage.from_(bucket).create_signed_url("diag/test.txt", 60)
            url = signed.get("signedURL") or signed.get("signed_url") or ""
            click.echo(f"signed_url={url}")
            if url:
                r = httpx.get(url, timeout=10)
                click.echo(f"signed_fetch status={r.status_code} bytes={len(r.content)}")
        except Exception as e:
            click.echo(f"signed_url fail {e}")
