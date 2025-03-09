import html as std_html
from aiogram import types

def format_user(user: types.User) -> str:
    safe_first = std_html.escape(user.first_name) if user.first_name else ""
    safe_last = std_html.escape(user.last_name) if user.last_name else ""
    safe_username = std_html.escape(user.username) if user.username else ""

    if safe_username:
        return f"@{safe_username}"
    elif safe_first or safe_last:
        return f"{safe_first} {safe_last}".strip()
    else:
        return f"Неизвестный ({user.id})"