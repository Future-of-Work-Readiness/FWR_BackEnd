"""
JWT Token utilities.
Functions for creating and decoding access and refresh tokens.
"""

import ast
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException
from pydantic import BaseModel

from src.app.config.settings import get_settings

config = get_settings()


# ============================================================
# TOKEN RESPONSE SCHEMAS
# ============================================================


class Tokens(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None  # seconds until expiration


class TokenData(BaseModel):
    """Schema for decoded token data."""

    sub: str
    exp: datetime


# ============================================================
# TOKEN CREATION FUNCTIONS
# ============================================================


def create_token(
    sub: str,
    secret: str,
    expires_delta: Optional[timedelta] = None,
    default_expire_minutes: int = 60,
) -> str:
    """
    Create a JWT token with the given subject, secret,
    expiration delta, and default expiration minutes.

    :param sub: The subject of the token (usually user_id).
    :param secret: The secret key to sign the token.
    :param expires_delta: The expiration delta of the token.
    :param default_expire_minutes: Default expiration minutes if no delta provided.
    :return: A JWT token string.
    """
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=default_expire_minutes)
    )
    to_encode = {"sub": str(sub), "exp": expire}
    return jwt.encode(to_encode, secret, algorithm=config.JWT_ALGORITHM)


def create_access_token(
    sub: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create an access token with the given subject and expiration delta.

    :param sub: The subject of the token (usually user_id).
    :param expires_delta: The expiration delta of the token.
    :return: An access token string.
    """
    return create_token(
        sub,
        config.JWT_SECRET,
        expires_delta,
        config.JWT_EXPIRES_IN,
    )


def create_refresh_token(
    sub: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a refresh token with the given subject and expiration delta.

    :param sub: The subject of the token (usually user_id).
    :param expires_delta: The expiration delta of the token.
    :return: A refresh token string.
    """
    return create_token(
        sub,
        config.JWT_REFRESH_SECRET,
        expires_delta,
        config.JWT_REFRESH_EXPIRES_IN,
    )


def create_tokens(user_id: str) -> Tokens:
    """
    Create both access and refresh tokens for a user.

    :param user_id: The user's ID to encode in the tokens.
    :return: Tokens object with access_token and refresh_token.
    """
    access_token = create_access_token(str(user_id))
    refresh_token = create_refresh_token(str(user_id))

    return Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.JWT_EXPIRES_IN * 60,  # Convert minutes to seconds
    )


# ============================================================
# TOKEN DECODING FUNCTIONS
# ============================================================


def decode_token(token: str, secret: str) -> dict:
    """
    Decode a JWT token with the given token and secret.

    :param token: The token to decode.
    :param secret: The secret key used to sign the token.
    :return: The decoded token payload.
    :raises HTTPException: If the token is invalid or expired.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return jwt.decode(token, secret, algorithms=[config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def decode_access_token(token: str) -> dict:
    """
    Decode an access token with the given token.

    :param token: The token to decode.
    :return: The decoded access token payload.
    :raises HTTPException: If the token is invalid or expired.
    """
    data = decode_token(token, config.JWT_SECRET)
    # Handle case where sub might be a stringified dict/tuple
    try:
        data["sub"] = ast.literal_eval(data["sub"])
    except (ValueError, SyntaxError):
        # sub is already a simple string (like user_id)
        pass
    return data


def decode_refresh_token(token: str) -> dict:
    """
    Decode a refresh token with the given token.

    :param token: The token to decode.
    :return: The decoded refresh token payload.
    :raises HTTPException: If the token is invalid or expired.
    """
    return decode_token(token, config.JWT_REFRESH_SECRET)


# ============================================================
# TOKEN VALIDATION HELPERS
# ============================================================


def verify_token(token: str, secret: str) -> bool:
    """
    Verify if a token is valid without raising exceptions.

    :param token: The token to verify.
    :param secret: The secret key used to sign the token.
    :return: True if valid, False otherwise.
    """
    try:
        decode_token(token, secret)
        return True
    except HTTPException:
        return False


def verify_access_token(token: str) -> bool:
    """
    Verify if an access token is valid.

    :param token: The access token to verify.
    :return: True if valid, False otherwise.
    """
    return verify_token(token, config.JWT_SECRET)


def verify_refresh_token(token: str) -> bool:
    """
    Verify if a refresh token is valid.

    :param token: The refresh token to verify.
    :return: True if valid, False otherwise.
    """
    return verify_token(token, config.JWT_REFRESH_SECRET)


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from an access token.

    :param token: The access token.
    :return: The user ID from the token.
    :raises HTTPException: If the token is invalid.
    """
    data = decode_access_token(token)
    return data["sub"]
