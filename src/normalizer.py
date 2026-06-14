"""Clean math symbols for NLP processing."""

import re
import pandas as pd


def normalize_math_text(text: str) -> str:
    """Apply math symbol transformations for NLP-friendly text."""
    if not isinstance(text, str):
        return str(text)

    # Square root patterns
    text = re.sub(r'[²³]?√(\w+)', r'sqrt(\1)', text)
    text = re.sub(r'[²³]?√', 'sqrt', text)

    # Superscript patterns (before general superscript replacement)
    text = re.sub(r'(\w)²', r'\1^2', text)
    text = re.sub(r'(\w)³', r'\1^3', text)

    # Comparison operators
    text = text.replace('≤', '<=')
    text = text.replace('≥', '>=')
    text = text.replace('≠', '!=')

    # Mathematical constants
    text = text.replace('π', 'pi')
    text = text.replace('∞', 'inf')

    # Arithmetic operators
    text = text.replace('×', '*')
    text = text.replace('÷', '/')
    text = text.replace('−', '-')  # unicode minus

    # Remaining superscript digits
    text = text.replace('²', '^2')
    text = text.replace('³', '^3')

    # Clean whitespace
    text = re.sub(r'  +', ' ', text)
    text = text.strip()

    return text


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply normalize_math_text to question and all option columns."""
    df = df.copy()
    text_cols = ["question", "option_a", "option_b", "option_c", "option_d"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(normalize_math_text)
    return df
