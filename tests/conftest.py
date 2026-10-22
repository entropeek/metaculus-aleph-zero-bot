"""Stubs forecasting_tools when it is not installed, so aleph_bot logic can be unit-tested offline."""
import sys
import textwrap
import types

# Real package present: use it; otherwise install minimal stand-ins.
if "forecasting_tools" not in sys.modules:
    try:
        import forecasting_tools  # noqa: F401
    except ImportError:
        stub = types.ModuleType("forecasting_tools")

        class BinaryQuestion:
            """Minimal binary question stand-in."""

            def __init__(self, **fields):
                self.__dict__.update(fields)

        stub.BinaryQuestion = BinaryQuestion
        stub.MetaculusQuestion = BinaryQuestion
        stub.GeneralLlm = object
        stub.clean_indents = lambda text: textwrap.dedent(text).strip()
        sys.modules["forecasting_tools"] = stub
