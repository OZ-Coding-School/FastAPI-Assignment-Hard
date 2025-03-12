from __future__ import annotations

import random
from typing import Any


class UserModel:
    _data: list[UserModel] = []  # 전체 사용자 데이터를 저장하는 리스트
    _id_counter = 1  # ID 자동 증가를 위한 카운터

    def __init__(self, username: str, age: int, gender: str) -> None:
        self.id = UserModel._id_counter
        self.username = username
        self.age = age
        self.gender = gender

        # 클래스가 인스턴스화 될 때 _data에 추가하고 _id_counter를 증가시킴
        UserModel._data.append(self)
        UserModel._id_counter += 1

    @classmethod
    def create(cls, username: str, age: int, gender: str) -> UserModel:
        """새로운 유저 추가"""
        return cls(username, age, gender)

    @classmethod
    def get(cls, **kwargs: Any) -> UserModel | None:
        """단일 객체를 반환 (없으면 None)"""
        for user in cls._data:
            if all(getattr(user, key) == value for key, value in kwargs.items()):
                return user
        return None

    @classmethod
    def filter(cls, **kwargs: Any) -> list[UserModel]:
        """조건에 맞는 객체 리스트 반환"""
        return [user for user in cls._data if all(getattr(user, key) == value for key, value in kwargs.items())]

    def update(self, **kwargs: Any) -> None:
        """객체의 필드 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)

    def delete(self) -> None:
        """현재 인스턴스를 _data 리스트에서 삭제"""
        if self in UserModel._data:
            UserModel._data.remove(self)

    @classmethod
    def all(cls) -> list[UserModel]:
        """모든 사용자 반환"""
        return cls._data

    @classmethod
    def clear(cls) -> None:
        """모든 사용자 삭제"""
        cls._data = []

    @classmethod
    def create_dummy(cls) -> None:
        for i in range(1, 11):
            cls(username=f"dummy{i}", age=15 + i, gender=random.choice(["male", "female"]))

    def __repr__(self) -> str:
        return f"UserModel(id={self.id}, username='{self.username}', age={self.age}, gender='{self.gender}')"

    def __str__(self) -> str:
        return self.username
