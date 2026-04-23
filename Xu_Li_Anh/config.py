from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytesseract


def _default_tesseract_candidates() -> list[str]:
    return [
        # Common Windows install locations
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        # Some users install under LocalAppData
        str(Path.home() / r"AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]


def setup_tesseract() -> tuple[str | None, str | None]:
    """
    Ensure pytesseract knows where `tesseract.exe` is, and try to set TESSDATA_PREFIX.

    Returns:
        (tesseract_cmd, tessdata_dir) where either can be None if not found.
    """
    env_cmd = os.environ.get("TESSERACT_CMD") or os.environ.get("TESSERACT_EXE")
    cmd: str | None = None

    if env_cmd and Path(env_cmd).is_file():
        cmd = env_cmd
    else:
        which_cmd = shutil.which("tesseract")
        if which_cmd and Path(which_cmd).is_file():
            cmd = which_cmd
        else:
            for candidate in _default_tesseract_candidates():
                if Path(candidate).is_file():
                    cmd = candidate
                    break

    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd

    tessdata_dir: str | None = None
    env_prefix = os.environ.get("TESSDATA_PREFIX")
    if env_prefix and Path(env_prefix).exists():
        tessdata_dir = env_prefix
    elif cmd:
        guess = Path(cmd).resolve().parent / "tessdata"
        if guess.is_dir():
            tessdata_dir = str(guess)
            os.environ["TESSDATA_PREFIX"] = tessdata_dir

    return cmd, tessdata_dir


def list_tesseract_languages() -> list[str]:
    cmd, _ = setup_tesseract()
    if not cmd:
        return []

    try:
        out = subprocess.check_output(
            [cmd, "--list-langs"],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return []

    langs: list[str] = []
    for line in out.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith("list of available languages"):
            continue
        langs.append(s)
    return langs


def resolve_ocr_settings(preferred: str = "vie") -> tuple[str | None, str | None, str | None]:
    """
    Resolve OCR language and (optional) tessdata dir override.

    Returns:
        (lang, tessdata_dir_override, warning_message)
    """
    cmd, install_tessdata = setup_tesseract()
    if not cmd:
        return None, None, "Không tìm thấy Tesseract. Hãy cài Tesseract OCR và đảm bảo `tesseract.exe` có trong PATH."

    preferred = (preferred or "").strip() or "eng"
    parts = [p.strip() for p in preferred.split("+") if p.strip()]

    available = set(list_tesseract_languages())
    if not available:
        return preferred, None, None

    if len(parts) >= 2:
        kept = [p for p in parts if p in available]
        if kept:
            kept_lang = "+".join(kept)
            warn = None if kept_lang == preferred else f"Thiếu một số ngôn ngữ OCR ({preferred}); đang dùng: {kept_lang}."
            return kept_lang, None, warn

    if preferred in available:
        return preferred, None, None

    if preferred == "vie":
        tessdata_hint = install_tessdata or r"<thư mục tessdata của Tesseract>"
        warn = (
            "Thiếu ngôn ngữ OCR tiếng Việt (`vie`). "
            f"Hãy copy `vie.traineddata` vào: {tessdata_hint}. "
            "Tạm thời OCR sẽ dùng tiếng Anh (`eng`)."
        )
        if "eng" in available:
            return "eng", None, warn
        return None, None, warn

    if "eng" in available:
        return "eng", None, f"Không có ngôn ngữ OCR `{preferred}`; đang dùng `eng`."

    return None, None, f"Không có ngôn ngữ OCR `{preferred}`; sẽ dùng ngôn ngữ mặc định của Tesseract."


def resolve_ocr_language(preferred: str = "vie") -> tuple[str | None, str | None]:
    """
    Pick an OCR language that is actually installed.

    Returns:
        (lang, warning_message). If lang is None, pytesseract will use its default.
    """
    lang, _tessdata_dir, warn = resolve_ocr_settings(preferred)
    return lang, warn


STORAGE_PATH = os.path.join(os.path.dirname(__file__), "storage") + os.sep
