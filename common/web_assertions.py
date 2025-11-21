"""Common web assertion utilities."""

from typing import Any, Iterable, Sequence, Mapping, Optional, Type


class WebAssertions:
    """Assertion helper with concise, consistent messages."""

    def __init__(self, driver=None, exception_cls: Type[Exception] = AssertionError):
        self.driver = driver
        self._exc = exception_cls

    # Internal
    def _fail(self, default: str, message: Optional[str]) -> None:
        raise self._exc(message or default)

    # Boolean
    def assert_true(self, condition: Any, message: Optional[str] = None) -> None:
        if not condition:
            self._fail("Condition is not true", message)

    def assert_false(self, condition: Any, message: Optional[str] = None) -> None:
        if condition:
            self._fail("Condition is not false", message)

    def assert_failed(self, message: Optional[str] = None) -> None:
        self._fail("Explicit failure", message)

    # Equality
    def assert_equals(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        if actual != expected:
            self._fail(f"{actual!r} != {expected!r}", message)

    def assert_not_equals(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        if actual == expected:
            self._fail(f"{actual!r} == {expected!r}", message)

    # Comparison
    def assert_less_than(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        if actual >= expected:
            self._fail(f"{actual!r} is not < {expected!r}", message)

    def assert_greater_than(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        if actual <= expected:
            self._fail(f"{actual!r} is not > {expected!r}", message)

    def assert_greater_or_equal(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        if actual < expected:
            self._fail(f"{actual!r} is not >= {expected!r}", message)

    def assert_less_or_equal(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        if actual > expected:
            self._fail(f"{actual!r} is not <= {expected!r}", message)

    # Emptiness
    def assert_empty(self, collection: Sequence | Mapping | Iterable, message: Optional[str] = None) -> None:
        if collection:
            self._fail("Collection is not empty", message)

    def assert_not_empty(self, collection: Sequence | Mapping | Iterable, message: Optional[str] = None) -> None:
        if not collection:
            self._fail("Collection is empty", message)

    # Containment
    def assert_contains(self, container: Iterable, item: Any, message: Optional[str] = None) -> None:
        if item not in container:
            self._fail(f"{item!r} not found in container", message)

    def assert_not_contains(self, container: Iterable, item: Any, message: Optional[str] = None) -> None:
        if item in container:
            self._fail(f"{item!r} unexpectedly found in container", message)

    # String
    def assert_starts_with(self, string: str, prefix: str, message: Optional[str] = None) -> None:
        if not string.startswith(prefix):
            self._fail(f"{string!r} does not start with {prefix!r}", message)

    def assert_ends_with(self, string: str, suffix: str, message: Optional[str] = None) -> None:
        if not string.endswith(suffix):
            self._fail(f"{string!r} does not end with {suffix!r}", message)
