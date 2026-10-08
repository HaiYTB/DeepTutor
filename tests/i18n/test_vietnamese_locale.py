"""Vietnamese UI locale integration tests."""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from deeptutor.api.routers.quiz_judge import (
    _JUDGE_SYSTEM_PROMPTS,
    SUPPORTED_JUDGE_LANGUAGES,
)
from deeptutor.core.response_languages import SUPPORTED_RESPONSE_LANGUAGES
from deeptutor.runtime.banner import LABELS, labels_for
from deeptutor.services.config.launch_settings import (
    _normalize_language as _launch_language,
)
from deeptutor.services.config.settings_spec import (
    _LANGUAGE_CHOICES,
    _RESPONSE_LANGUAGE_CHOICES,
)
from deeptutor.services.prompt.language import language_directive, language_label
from deeptutor.services.settings.interface_settings import _normalize_language

WEB = pathlib.Path(__file__).resolve().parents[2] / "web"

def _catalog(locale: str) -> dict[str, str]:
    return json.loads((WEB / f"locales/{locale}/app.json").read_text(encoding="utf-8"))

@pytest.mark.parametrize(
    "raw",
    [
        "vi",
        "VI",
        " vi ",
        "vietnamese",
        "tieng viet",
        "tiếng việt",
        "vi-VN",
        "vi_VN",
    ],
)
def test_normalizer_accepts_vietnamese_spellings(raw: str) -> None:
    assert _normalize_language(raw) == "vi"

def test_launch_settings_accept_vietnamese() -> None:
    assert _launch_language("vi-VN") == "vi"
    assert _launch_language("vietnamese") == "vi"

def test_settings_offers_vietnamese() -> None:
    assert "vi" in {code for code, _label, _desc in _LANGUAGE_CHOICES}

def test_settings_offer_vietnamese_as_reply_language() -> None:
    assert "vi" in {code for code, _label, _desc in _RESPONSE_LANGUAGE_CHOICES}
    assert "vi" in SUPPORTED_RESPONSE_LANGUAGES

def test_language_directive_names_vietnamese() -> None:
    assert language_label("vi") == "Tiếng Việt"
    assert "Tiếng Việt" in language_directive("vi")

def test_cli_banner_is_fully_translated() -> None:
    assert set(LABELS["vi"]) == set(LABELS["en"])
    assert labels_for("vi") is LABELS["vi"]

def test_judge_speaks_vietnamese() -> None:
    assert SUPPORTED_JUDGE_LANGUAGES == frozenset(_JUDGE_SYSTEM_PROMPTS)
    assert "vi" in SUPPORTED_JUDGE_LANGUAGES
    assert "tiếng Việt" in _JUDGE_SYSTEM_PROMPTS["vi"]

def test_web_locale_covers_every_english_key() -> None:
    en = _catalog("en")
    vi = _catalog("vi")

    assert set(en) <= set(vi)

    extras = set(vi) - set(en)
    assert all(key.endswith(("_zero", "_one", "_two", "_few", "_many", "_other")) for key in extras)

def test_web_locale_keeps_interpolation_placeholders() -> None:
    en = _catalog("en")
    vi = _catalog("vi")

    pattern = re.compile(r"\{\{[^}]+\}\}")

    mismatches = [
        key
        for key in set(en) & set(vi)
        if set(pattern.findall(en[key])) != set(pattern.findall(vi[key]))
    ]
    assert mismatches == []

def test_every_locale_can_name_vietnamese() -> None:
    for locale in ("en", "zh", "fr", "de", "uk", "pl", "vi"):
        assert "language.vietnamese" in _catalog(locale)

def test_frontend_registers_vietnamese() -> None:
    languages = (WEB / "i18n/languages.ts").read_text(encoding="utf-8")
    assert '{ code: "vi", labelKey: "language.vietnamese" }' in languages

    init = (WEB / "i18n/init.ts").read_text(encoding="utf-8")
    assert "@/locales/vi/app.json" in init
