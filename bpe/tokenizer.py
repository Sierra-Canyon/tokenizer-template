"""Byte-pair encoding, written from an empty file.

Fill in the four functions below. Nothing here imports anything the assignment
bans: the standard library and `regex` only, no tiktoken, no transformers.

Run the tests as you go, smallest first:

    pytest tests/test_helpers.py -q      # get_stats and merge
    pytest tests/test_basic.py -q        # BasicTokenizer
    pytest tests/test_regex.py -q        # RegexTokenizer
    pytest tests/ -q                     # all 47

`pytest -x` stops at the first failure, which is usually what you want.
"""
from __future__ import annotations

# The GPT-4 split pattern. Requires the `regex` module: the standard library's
# `re` does not support \p{L}, and the failure looks like a bug in your code.
GPT4_SPLIT_PATTERN = (
    r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}"""
    r"""| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
)


def get_stats(ids, counts=None):
    """Count how often each adjacent pair appears in `ids`.

    >>> get_stats([1, 2, 3, 1, 2])
    {(1, 2): 2, (2, 3): 1, (3, 1): 1}

    `counts` lets you accumulate across several chunks without allocating a new
    dict each time, which is how RegexTokenizer counts over its split pieces.
    """
    raise NotImplementedError


def merge(ids, pair, idx):
    """Replace every consecutive occurrence of `pair` in `ids` with `idx`.

    >>> merge([1, 2, 3, 1, 2], (1, 2), 4)
    [4, 3, 4]

    Walk the list once. The bug to avoid is stepping by one after a match and
    re-reading the token you just wrote.
    """
    raise NotImplementedError


class BasicTokenizer:
    """BPE straight over the UTF-8 bytes, no splitting."""

    def __init__(self):
        self.merges = {}   # (int, int) -> int, in the order they were learned
        self.vocab = {}    # int -> bytes

    def train(self, text, vocab_size, verbose=False):
        """Learn `vocab_size - 256` merges from `text`.

        Each round: count pairs, take the one with the HIGHEST count, mint the
        next id for it. Ties can go either way; the tests do not depend on which.
        """
        raise NotImplementedError

    def encode(self, text):
        """Text to token ids.

        Each round: of the pairs currently present, merge the one with the
        LOWEST merge index, because that is the one that was learned first.
        Not the highest count. This is the single most common bug in the
        assignment and it produces output that looks almost right.

        Read `self.merges` and `self.vocab` and nothing else. The tests build a
        tokenizer by hand to check merge ordering, so encode must not depend on
        anything train() happens to leave lying around.
        """
        raise NotImplementedError

    def decode(self, ids):
        """Token ids back to text.

        A byte sequence mid-merge is often not valid UTF-8, so decode with
        errors="replace" and be able to say why that is correct rather than a
        workaround.
        """
        raise NotImplementedError


class RegexTokenizer(BasicTokenizer):
    """BasicTokenizer, but the text is split before any pair is counted, so no
    merge is ever learned across a category boundary."""

    def __init__(self, pattern=None):
        super().__init__()
        self.pattern = pattern or GPT4_SPLIT_PATTERN

    def train(self, text, vocab_size, verbose=False):
        raise NotImplementedError

    def encode(self, text):
        raise NotImplementedError
