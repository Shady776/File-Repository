import hashlib
import re
import cloudinary.uploader

def get_file_hash(file_content: bytes) -> str:
    return hashlib.md5(file_content).hexdigest()


def delete_from_cloudinary(public_id: str):
    try:
        cloudinary.uploader.destroy(public_id, resource_type="raw")
    except Exception as e:
        print(f"Failed to delete from Cloudinary: {e}")
