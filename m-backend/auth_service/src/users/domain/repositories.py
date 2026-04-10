"""Abstract repository interfaces — the domain's contract with infrastructure."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from .entities import ProfileImageEntity, UserEntity


class AbstractUserRepository(ABC):
    """Port for user persistence operations."""

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> Optional[UserEntity]:
        """Retrieves a user by their primary key."""

    @abstractmethod
    def get_by_login(self, login: str) -> Optional[UserEntity]:
        """Retrieves a user matching the given username or email."""

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """Returns True if the username is already taken."""

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Returns True if the email is already registered."""

    @abstractmethod
    def save(self, user: UserEntity) -> UserEntity:
        """Persists a new user and returns the saved entity."""


class AbstractProfileImageRepository(ABC):
    """Port for profile image catalog operations."""

    @abstractmethod
    def get_by_id(self, image_id: uuid.UUID) -> Optional[ProfileImageEntity]:
        """Retrieves a predefined profile image by its id."""
