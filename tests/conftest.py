"""Shared fixtures. Imports whatever `bpe.tokenizer` currently defines, so the
suite runs against your code with no configuration."""
import pytest
from bpe.tokenizer import BasicTokenizer, RegexTokenizer

# Small but not degenerate: repeated words so merges have something to find,
# and a mix of scripts so the byte-level cases are real rather than contrived.
CORPUS = (
    "the quick brown fox jumps over the lazy dog. " * 12
    + "the theory of the thing is that the theatre theme repeats. " * 8
    + "naïve café résumé naïve café. " * 6
    + "def foo(): return foo() if foo else None\n" * 5
)

UNICODE_SAMPLES = [
    "hello",
    "héllo",
    "🙂🙃",
    "日本語のテキスト",
    "مرحبا بالعالم",
    "a" * 200,
    "    def foo():",
    "12,345,678",
    " hello",
    "",
]


@pytest.fixture(scope="session")
def corpus():
    return CORPUS


@pytest.fixture(scope="session")
def basic(corpus):
    t = BasicTokenizer()
    t.train(corpus, 320)
    return t


@pytest.fixture(scope="session")
def regexed(corpus):
    t = RegexTokenizer()
    t.train(corpus, 320)
    return t
