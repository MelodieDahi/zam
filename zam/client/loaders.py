import json
import os
from io import BytesIO
from pathlib import Path
from typing import Tuple

import pdfminer.high_level

from decorators import check_existence, require_env_vars
from parsers import parse_docx


def load_json(source_path: Path) -> dict:
    with open(source_path) as source:
        return json.loads(source.read())


@require_env_vars(env_vars=['ZAM_DRUPAL_SOURCE'])
def load_drupal_source() -> Tuple[str, dict]:
    source = load_json(os.environ['ZAM_DRUPAL_SOURCE'])[0]  # Unique item.
    return source['libelle'], source['list']


@require_env_vars(env_vars=['ZAM_ASPIRATEUR_SOURCE'])
def load_aspirateur_source() -> Tuple[str, dict]:
    source = load_json(os.environ['ZAM_ASPIRATEUR_SOURCE'])[0]  # Unique item.
    return source['libelle'], source['list']


@check_existence
def load_pdf(source_path: Path) -> str:
    target = BytesIO()
    with open(source_path, 'rb') as source:
        pdfminer.high_level.extract_text_to_fp(source, target, codec='latin-1')
    content = target.getvalue().decode()
    # Skip optional headers.
    separator = '----------'
    if separator in content:
        headers, content = content.split(separator)
    return content.strip()


@check_existence
def load_docx(source_path: Path) -> str:
    with open(source_path, 'rb') as source:
        content = parse_docx(source)
    # Get rid of (not proper docx) headers.
    return '\n'.join(part for part in content.split('\n')[9:])
