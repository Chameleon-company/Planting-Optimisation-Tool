import os
import secrets
from pathlib import Path


def main() -> None:
    env_file = Path(".env")
    if env_file.exists():
        return

    template = Path(".env.example").read_text(encoding="utf-8")
    placeholder = "SECRET_KEY=\n"
    if template.count(placeholder) != 1:
        raise ValueError(".env.example must contain exactly one empty SECRET_KEY entry")

    contents = template.replace(placeholder, f"SECRET_KEY={secrets.token_urlsafe(32)}\n", 1)
    fd = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(contents)
    print("--- Created .env from .env.example with a random signing key ---")


if __name__ == "__main__":
    main()
