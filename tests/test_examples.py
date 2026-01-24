import logging
import py_compile
import sys
from six import StringIO

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

logger = logging.getLogger(__name__)

examples_path = Path(__file__).parent.parent / "docs" / "examples"


def test_compile():
    """
    Validate if all provided example programs compile well.
    https://stackoverflow.com/a/4537442
    """

    # Save stderr, because the test function redirects it.
    real_stderr = getattr(sys, "stderr")

    # List of examples written for Python 3.
    python3_examples = ["muc.py"]

    for example in examples_path.glob("*.py"):

        # On Python 2, skip examples written for Python 3.
        if sys.version_info < (3, 0, 0) and example.name in python3_examples:
            continue

        # Compile program. If that emits anything to stderr, bail out.
        buffer = StringIO()
        setattr(sys, "stderr", buffer)
        py_compile.compile(str(example))
        output = buffer.getvalue().strip()
        if output != "":
            raise RuntimeError("Failed to compile %s: %s" % (example, output))

    # Restore stderr.
    setattr(sys, "stderr", real_stderr)
