"""Lightweight prompt templating with required-variable validation."""

from __future__ import annotations

import string


class PromptTemplate:
    """A reusable prompt with ``{placeholders}``.

    Unlike a bare ``str.format``, this detects the variables up front and tells
    you exactly which ones are missing at render time.

    Example::

        t = PromptTemplate("Translate {text} into {language}.")
        t.render(text="hello", language="French")
        # -> "Translate hello into French."
    """

    def __init__(self, template: str):
        self.template = template
        self.variables = self._extract_variables(template)

    @staticmethod
    def _extract_variables(template: str) -> set[str]:
        return {
            field
            for _, field, _, _ in string.Formatter().parse(template)
            if field
        }

    def render(self, **kwargs) -> str:
        missing = self.variables - kwargs.keys()
        if missing:
            raise KeyError(f"Missing template variables: {sorted(missing)}")
        return self.template.format(**kwargs)

    def __repr__(self) -> str:
        return f"PromptTemplate(variables={sorted(self.variables)})"
