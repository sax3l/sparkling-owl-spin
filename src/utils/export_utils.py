import csv
import io
import json
import gzip
import os
import datetime
import uuid # Import uuid for UUID type handling
import enum # Import enum for Enum type handling
from typing import List, Dict, Any, Generator, Optional
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, asc, desc
from src.database.models import Person, Company, Vehicle # Import relevant models
from src.integrations.supabase.client import supabase # Assuming supabase client is available
import logging

logger = logging.getLogger(__name__)

# Mapping of export_type to SQLAlchemy model
MODEL_MAP = {
    "person": Person,
    "company": Company,
    "vehicle": Vehicle,
    # Add other models as needed
}

def get_model_by_export_type(export_type: str):
    model = MODEL_MAP.get(export_type)
    if not model:
        raise ValueError(f"Unsupported export type: {export_type}")
    return model

def _mask_personal_number(personal_number: Optional[str]) -> Optional[str]:
    """Masks a personal number, showing only the last 4 digits."""
    if not personal_number:
        return None
    # Assumes format YYYYMMDD-XXXX or YYMMDD-XXXX
    # Masks all but the last 4 digits
    if len(personal_number) >= 4:
        return f"***-***-{personal_number[-4:]}"
    return "***-***-****" # Fallback for very short or invalid numbers

def generate_csv_stream(data_generator: Generator[Dict, None, None], fieldnames: List[str]) -> Generator[bytes, None, None]:
    """Generates a CSV stream from a dictionary generator."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)

    # Write header
    writer.writeheader()
    yield output.getvalue().encode('utf-8')
    output.seek(0)
    output.truncate(0)

    # Write data rows
    for row in data_generator:
        writer.writerow(row)
        yield output.getvalue().encode('utf-8')
        output.seek(0)
        output.truncate(0)

def generate_ndjson_stream(data_generator: Generator[Dict, None, None]) -> Generator[bytes, None, None]:
    """Generates an NDJSON stream from a dictionary generator."""
    for row in data_generator:
        yield (json.dumps(row, ensure_ascii=False) + "\n").encode('utf-8')

def generate_json_stream(data_generator: Generator[Dict, None, None]) -> Generator[bytes, None, None]:
    """Generates a standard JSON array stream from a dictionary generator."""
    yield b"[\n"
    first = True
    for row in data_generator:
        if not first:
            yield b",\n"
        yield json.dumps(row, ensure_ascii=False).encode('utf-8')
        first = False
    yield b"\n]\n"

async def upload_to_supabase_storage(
    bucket_name: str,
    file_path: str,
    data_stream: Generator[bytes, None, None],
    content_type: str,
    compress: bool = False
) -> str:
    """
    Uploads a data stream to Supabase Storage.
    Returns the public URL of the uploaded file.
    """
    # Supabase storage client doesn't directly support streaming upload from a generator
    # in the same way as boto3. We'll need to buffer it or write to a temp file.
    # For simplicity, let's collect the data into bytes first.
    # For very large files, consider writing to a temporary file and then uploading.

    full_data = b""
    for chunk in data_stream:
        full_data += chunk

    if compress:
        full_data = gzip.compress(full_data)
        file_path += ".gz"
        content_type = "application/gzip" # Update content type for gzipped files

    try:
        # Supabase storage upload
        # The `upload` method expects bytes or a file-like object.
        # If `full_data` is too large, this will be a memory issue.
        # A more robust solution for very large files would involve
        # Deno Edge Functions or a server-side stream to Supabase.
        response = await supabase.storage.from_(bucket_name).upload(file_path, full_data, {
            'contentType': content_type,
            'upsert': True # Overwrite if exists
        })

        if response.error:
            raise Exception(f"Supabase Storage upload failed: {response.error.message}")

        # Get public URL
        public_url_response = supabase.storage.from_(bucket_name).get_public_url(file_path)
        if public_url_response.error:
            raise Exception(f"Failed to get public URL: {public_url_response.error.message}")

        return public_url_response.data.publicUrl

    except Exception as e:
        logger.error(f"Error uploading to Supabase Storage: {e}")
        raise

async def generate_presigned_url(bucket_name: str, file_path: str, expires_in: int = 3600) -> str:
    """
    Generates a presigned URL for a file in Supabase Storage.
    `expires_in` is in seconds.
    """
    try:
        response = supabase.storage.from_(bucket_name).create_signed_url(file_path, expires_in)
        if response.error:
            raise Exception(f"Failed to create signed URL: {response.error.message}")
        return response.data.signedUrl
    except Exception as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise

def get_data_from_db(
    db: Session, 
    export_type: str, 
    filters: Dict[str, Any], 
    sort_by: Optional[str] = None,
    fields: Optional[List[str]] = None,
    mask_pii: bool = True # New parameter for PII masking
) -> Generator[Dict, None, None]:
    """
    Fetches data from the database based on export_type, filters, sorting, and field selection.
    Yields rows as dictionaries.
    """
    model = get_model_by_export_type(export_type)
    query = db.query(model)

    # Apply filters
    for key, value in filters.items():
        if hasattr(model, key):
            column = getattr(model, key)
            if isinstance(value, dict):
                # Handle operators like gte, lte, in
                if "gte" in value:
                    query = query.filter(column >= value["gte"])
                if "lte" in value:
                    query = query.filter(column <= value["lte"])
                if "in" in value and isinstance(value["in"], list):
                    query = query.filter(column.in_(value["in"]))
            else:
                # Basic equality filter
                query = query.filter(column == value)
        else:
            logger.warning(f"Filter field '{key}' not found in model '{export_type}'. Skipping.")

    # Apply sorting
    if sort_by:
        sort_column_name = sort_by.lstrip('-')
        if hasattr(model, sort_column_name):
            sort_column = getattr(model, sort_column_name)
            if sort_by.startswith('-'):
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            logger.warning(f"Sort field '{sort_by}' not found in model '{export_type}'. Skipping sort.")

    # Fetch and yield data
    for row in query.all():
        row_dict = {}
        # Select specific fields if requested, otherwise all columns
        columns_to_include = fields if fields else [c.name for c in inspect(model).columns]

        for col_name in columns_to_include:
            if hasattr(row, col_name):
                value = getattr(row, col_name)
                
                # Apply PII masking if enabled and applicable
                if mask_pii and export_type == "person" and col_name == "personal_number_hash":
                    # Note: personal_number_hash is a hash, not the raw number.
                    # For masking, we'd ideally mask the *decrypted* personal_number.
                    # As a placeholder for production-readiness, we'll mask the hash itself
                    # or indicate it's masked. A proper PII service would handle decryption.
                    row_dict[col_name] = "[MASKED_HASH]"
                elif mask_pii and export_type == "person" and col_name == "personal_number_enc":
                    row_dict[col_name] = "[MASKED_ENCRYPTED_DATA]"
                elif mask_pii and export_type == "person" and col_name == "phone_number_hash":
                    row_dict[col_name] = "[MASKED_PHONE_HASH]"
                elif mask_pii and export_type == "person" and col_name == "phone_number_enc":
                    row_dict[col_name] = "[MASKED_ENCRYPTED_PHONE]"
                elif mask_pii and export_type == "person" and col_name == "salary_decimal":
                    row_dict[col_name] = "[MASKED_SALARY]"
                # Handle non-JSON serializable types (e.g., datetime, Decimal, UUID, Enum)
                elif isinstance(value, (datetime.datetime, datetime.date)):
                    row_dict[col_name] = value.isoformat()
                elif isinstance(value, datetime.timedelta):
                    row_dict[col_name] = str(value)
                elif isinstance(value, uuid.UUID):
                    row_dict[col_name] = str(value)
                elif isinstance(value, enum.Enum):
                    row_dict[col_name] = value.value
                elif isinstance(value, (float, int)):
                    row_dict[col_name] = value
                elif isinstance(value, bytes): # For LargeBinary columns
                    row_dict[col_name] = value.decode('utf-8', errors='ignore') # Or base64 encode
                else:
                    row_dict[col_name] = value
        yield row_dict

def get_fieldnames_for_export_type(export_type: str) -> List[str]:
    """Returns a list of column names for a given export type."""
    model = get_model_by_export_type(export_type)
    return [column.name for column in inspect(model).columns]