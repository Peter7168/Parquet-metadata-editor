import pyarrow.parquet as pq
import pyarrow as pa
import os


def load_parquet_metadata(file_path):
    table = pq.read_table(file_path)
    metadata = table.schema.metadata or {}
    # Convert from bytes to str for editing
    return {k.decode(): v.decode() for k, v in metadata.items()}, table


def save_parquet_with_metadata(original_file_path, new_metadata, table):
    # Convert dict from str to bytes
    encoded_metadata = {k.encode(): v.encode() for k, v in new_metadata.items()}

    # Update schema with new metadata
    new_schema = table.schema.with_metadata(encoded_metadata)

    # Replace the schema in the table
    new_table = pa.Table.from_arrays(table.columns, schema=new_schema)

    # Write to same path or a new file
    #TODO add option to save as new file
    pq.write_table(new_table, original_file_path)


def update_metadata_value(metadata, key, new_value):
    metadata[key] = new_value
    return metadata


def delete_metadata_key(metadata, key):
    if key in metadata:
        del metadata[key]
    return metadata


def add_new_metadata_key(metadata, key, value=""):
    if key not in metadata:
        metadata[key] = value
    return metadata
