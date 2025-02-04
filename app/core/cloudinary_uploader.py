"""
    This file contains functions for the conversion of QR code image objects generated using the `qrcode` module to bytes (compressed bytes not bytes for every image pixel) using the `io` module which are then passed to a function which uploads the image to cloudinary and returns a response, using the `cloudinary` module
"""

import qrcode
import io

import cloudinary
import cloudinary.uploader
import cloudinary.api

from pydantic import BaseModel
from datetime import datetime
from typing import Dict

from app.core.config import settings


class CloudinaryResponse(BaseModel):
    """
    A validates the response from cloudinary and returns an object
    """

    access_mode: str
    api_key: str
    asset_id: str
    bytes: int
    created_at: datetime
    etag: str
    folder: str = ""
    format: str
    height: int
    original_filename: str
    placeholder: bool
    public_id: str
    resource_type: str
    secure_url: str
    signature: str
    tags: list
    type: str
    url: str
    version: int
    version_id: str
    width: int


def make_qrcode_with_content(content: str):
    """
    create qrcode image object
    """
    if not content:
        raise Exception("qr code content is required")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white")


def image_to_bytes(image) -> bytes:
    """
    accepts an image object and returns image bytes

    More performant than using `image`.`tobytes()`
    """
    # create I/O byte buffer
    img_byte = io.BytesIO()
    # write image to buffer
    image.save(img_byte)
    # get byte's from content buffer
    img_byte = img_byte.getvalue()
    return img_byte


# initializing/assigning cloudinary configurations
config = cloudinary.config(
    secure=True,
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


def uploadImage(imageBytes: bytes) -> CloudinaryResponse:
    """
    uploads the image to cloudinary returning a `CloudinaryResponse` object
    """
    cloudinary_res = cloudinary.uploader.upload(
        imageBytes, unique_filename=True, overwrite=True, folder="qrcode_event_manager"
    )
    return CloudinaryResponse(**cloudinary_res)


def create_n_upload_qrcode(content: str) -> CloudinaryResponse:
    """
    this function performs the following functionality, in order:
    - accepts a string
    - embeds the string into a QR code image object (in memory)
    - stores the QR code image on cloudinary and returns a `CloudinaryResponse`
    """
    img_obj = make_qrcode_with_content(content)
    img_bytes = image_to_bytes(img_obj)
    return uploadImage(img_bytes)


def deleteImage(public_id: str) -> Dict[str, str]:
    """
    deletes an image from cloudinary using the image public id
    """
    response = cloudinary.uploader.destroy(public_id)
    # e.g {'result': 'ok'}
    return response


__all__ = ("create_n_upload_qrcode", "deleteImage")
