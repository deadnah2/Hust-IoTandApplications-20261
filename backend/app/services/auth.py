from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status # Thêm dòng này
from app.core import security
from app.core.config import settings
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import UserRegister


class AuthService:
    @staticmethod
    async def register_user(user_in: UserRegister) -> User:
        """
        Registers a new user.

        Args:
            user_in: The user registration data.

        Returns:
            The created user.

        Raises:
            HTTPException: If the username or email is already taken.
        """
        existing_user = await User.find_one(User.username == user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )
        if user_in.email:
            existing_email = await User.find_one(User.email == user_in.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )

        hashed_password = security.get_password_hash(user_in.password)
        user = User(
            username=user_in.username,
            email=user_in.email,
            passwordHash=hashed_password,
        )
        await user.create()
        return user

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticates a user.

        Args:
            username: The username.
            password: The password.

        Returns:
            The authenticated user, or None if authentication fails.
        """
        user = await User.find_one(User.username == username)
        if not user:
            return None
        if not security.verify_password(password, user.passwordHash):
            return None
        return user

    @staticmethod
    async def create_tokens(user: User) -> (str, str):
        """
        Creates access and refresh tokens for a user.

        Args:
            user: The user to create tokens for.

        Returns:
            A tuple containing the access token and refresh token.
        """
        access_token = security.create_access_token(user.id)
        refresh_token = security.create_refresh_token(user.id)

        # Save session
        session = Session(
            userId=user.id,
            refreshToken=refresh_token,
            expiresAt=datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await session.create()

        return access_token, refresh_token

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Optional[str]:
        """
        Refreshes an access token using a refresh token.

        Args:
            refresh_token: The refresh token.

        Returns:
            A new access token, or None if the refresh token is invalid.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            if payload["type"] != "refresh":
                return None

            session = await Session.find_one(Session.refreshToken == refresh_token)
            if not session:
                return None

            user = await User.get(session.userId)
            if not user:
                return None

            return security.create_access_token(user.id)
        except JWTError:
            return None

    @staticmethod
    async def logout(refresh_token: str):
        """
        Logs out a user by deleting their session.

        Args:
            refresh_token: The refresh token of the session to delete.
        """
        session = await Session.find_one(Session.refreshToken == refresh_token)
        if session:
            await session.delete()
