import re
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, validator


# 基础用户模型（公共字段）
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    real_name: Optional[str] = Field(None, description="真实姓名")
    role: Literal["admin", "driver", "customer"] = Field(description="角色")


# 用户注册请求模型
class UserCreateRequest(UserBase):
    password: str = Field(min_length=6, description="密码")

    # 手机号格式校验
    @validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式错误")
        return v


# 用户登录请求模型
class UserLoginRequest(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


# 用户登录响应模型
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: dict


# 用户信息响应模型（隐藏敏感字段）
class UserInfoResponse(BaseModel):
    id: int
    username: str
    role: str
    phone: Optional[str]
    real_name: Optional[str]
    create_time: str

    # 支持ORM模型转DTO
    class Config:
        orm_mode = True


# 用户信息修改请求模型
class UserUpdateRequest(BaseModel):
    phone: Optional[str] = Field(None, description="手机号")
    real_name: Optional[str] = Field(None, description="真实姓名")

    @validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式错误")
        return v


# 密码重置请求模型
class PasswordResetRequest(BaseModel):
    old_password: str = Field(description="旧密码")
    new_password: str = Field(min_length=6, description="新密码(至少6位)")
