from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    email: str
    name: str

class UserRepository:
    def find_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError  # Реализуется в продакшене

    def save(self, user: User) -> None:
        raise NotImplementedError

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, email: str, name: str) -> User:
        if self.repo.find_by_email(email):
            raise ValueError("Email already registered")
        user = User(email=email, name=name)
        self.repo.save(user)
        return user

    def get_user(self, email: str) -> User:
        user = self.repo.find_by_email(email)
        if not user:
            raise LookupError("User not found")
        return user