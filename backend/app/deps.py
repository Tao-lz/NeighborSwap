from fastapi import Header, HTTPException


def current_user_id(x_user_id: int | None = Header(default=None)) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="缺少用户标识 X-User-Id")
    return x_user_id


def optional_user_id(x_user_id: int | None = Header(default=None)) -> int | None:
    return x_user_id
