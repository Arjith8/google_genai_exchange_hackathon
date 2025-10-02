import io
import logging

from google.cloud.storage import Bucket

logger = logging.getLogger(__name__)


class FileUtils:
    @staticmethod
    def upload(file: str, file_name: str, bucket: Bucket) -> None:
        """
        Upload a string as a file to the given cloud storage bucket.

        Args:
            file: The file content as a string.
            file_name: The name of the file to create in the bucket.
            bucket: The bucket object to which the file will be uploaded.

        Returns:
            The blob object representing the uploaded file.

        """
        file_buffer = io.BytesIO(file.encode("utf-8"))
        blob_name = file_name

        logger.info("Uploading HTML content to GCP bucket")

        blob = bucket.blob(blob_name)
        blob.upload_from_file(file_buffer, rewind=True, content_type="text/plain")
