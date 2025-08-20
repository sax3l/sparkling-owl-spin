import csv
import io
import json
import gzip
import os
import datetime
from typing import List, Dict, Any, Generator, Optional
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
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

def get_data_from_db(db: Session, export_type: str, filters: Dict[str, Any]) -> Generator[Dict, None, None]:
    """
    Fetches data from the database based on export_type and filters.
    Yields rows as dictionaries.
    """
    model = get_model_by_export_type(export_type)
    query = db.query(model)

    # Apply filters (basic example, needs more robust filter parsing)
    for key, value in filters.items():
        if hasattr(model, key):
            # Basic equality filter. For more complex filters (e.g., ranges, LIKE),
            # you'd need a more sophisticated filter parsing logic.
            query = query.filter(getattr(model, key) == value)

    # Implement cursor-based pagination for large datasets
    # For simplicity, this example fetches all matching records.
    # In a real-world scenario, you'd fetch in chunks using a cursor.
    
    # Example of fetching in chunks (pseudo-code for cursor pagination)
    # last_id = None
    # while True:
    #     chunk_query = query.order_by(model.id).limit(1000)
    #     if last_id:
    #         chunk_query = chunk_query.filter(model.id > last_id)
    #     
    #     results = chunk_query.all()
    #     if not results:
    #         break
    #     
    #     for row in results:
    #         yield {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs}
    #     
    #     last_id = results[-1].id

    # For now, fetch all and yield
    for row in query.all():
        # Convert SQLAlchemy model instance to dictionary
        row_dict = {}
        for column in inspect(model).columns:
            value = getattr(row, column.name)
            # Handle non-JSON serializable types (e.g., datetime, Decimal, UUID)
            if isinstance(value, (datetime.datetime, datetime.date)):
                row_dict[column.name] = value.isoformat()
            elif isinstance(value, datetime.timedelta):
                row_dict[column.name] = str(value)
            elif isinstance(value, uuid.UUID):
                row_dict[column.name] = str(value)
            elif isinstance(value, enum.Enum):
                row_dict[column.name] = value.value
            elif isinstance(value, (float, int)):
                row_dict[column.name] = value
            elif isinstance(value, bytes): # For LargeBinary columns
                row_dict[column.name] = value.decode('utf-8', errors='ignore') # Or base64 encode
            else:
                row_dict[column.name] = value
        yield row_dict

def get_fieldnames_for_export_type(export_type: str) -> List[str]:
    """Returns a list of column names for a given export type."""
    model = get_model_by_export_type(export_type)
    return [column.name for column in inspect(model).columns]