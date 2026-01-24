import logging
import py_compile
from pathlib import Path

logger = logging.getLogger(__name__)

examples_path = Path(__file__).parent.parent / "docs" / "examples"


def test_compile():
    """
    Validate if all provided example programs compile well.
    https://stackoverflow.com/a/4537442
    """
    for example in examples_path.glob("*.py"):
        if not py_compile.compile(str(example)):
            raise RuntimeError("Failed to compile %s" % (example,))
