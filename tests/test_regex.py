"""RegexTokenizer: the same BPE, but the text is split first so no merge is
ever learned across a category boundary."""
import pytest
from bpe.tokenizer import RegexTokenizer, BasicTokenizer, GPT4_SPLIT_PATTERN


class TestSplitting:
    def test_the_pattern_needs_the_regex_module(self):
        # \p{L} is a Unicode property escape. The standard library's `re` does
        # not support it, and the error it gives points at the pattern rather
        # than at the import, which is why people lose an hour here.
        import regex
        assert regex.compile(GPT4_SPLIT_PATTERN)

    def test_no_merge_spans_a_letter_and_a_digit(self, regexed):
        letters = set("abcdefghijklmnopqrstuvwxyz".encode("utf-8"))
        digits = set("0123456789".encode("utf-8"))
        for (a, b) in regexed.merges:
            crosses = (a in letters and b in digits) or (a in digits and b in letters)
            assert not crosses, f"merge {(a, b)} crosses a letter/digit boundary"

    def test_a_space_never_merges_onto_the_end_of_a_word(self, regexed):
        space = ord(" ")
        for (a, b) in regexed.merges:
            assert b != space or a == space, (
                "the pattern puts a space at the START of the next piece, "
                "so nothing should ever merge a trailing space"
            )


class TestRoundTrip:
    @pytest.mark.parametrize("text", ["hello world", "héllo wörld", "🙂 ok",
                                      "def foo(): pass", "", "a", "   "])
    def test_decode_of_encode_is_the_original(self, regexed, text):
        assert regexed.decode(regexed.encode(text)) == text

    def test_round_trip_on_the_training_corpus(self, regexed, corpus):
        assert regexed.decode(regexed.encode(corpus)) == corpus


class TestAgainstBasic:
    def test_it_is_a_basic_tokenizer(self, regexed):
        assert isinstance(regexed, BasicTokenizer)

    def test_splitting_changes_what_gets_learned(self, corpus):
        b, r = BasicTokenizer(), RegexTokenizer()
        b.train(corpus, 320)
        r.train(corpus, 320)
        assert set(b.merges) != set(r.merges), (
            "if these are identical your splitting is not being applied"
        )

    def test_a_custom_pattern_is_honoured(self, corpus):
        # Split on whitespace only: a much coarser rule, so different merges.
        loose = RegexTokenizer(pattern=r"\S+|\s+")
        loose.train(corpus, 320)
        default = RegexTokenizer()
        default.train(corpus, 320)
        assert set(loose.merges) != set(default.merges)


class TestEncodeOrder:
    def test_merges_are_applied_lowest_index_first(self):
        """encode() reads self.merges and self.vocab and nothing else, so this
        builds a tokenizer by hand rather than training one.

        Two merges that overlap: (a,b) was learned first, (b,c) second. On the
        input "abcbc" the pair (b,c) occurs twice and (a,b) only once, so an
        encode loop that picks the most COMMON pair merges (b,c) first and gets
        a different answer than one that picks the LOWEST merge index. Both
        answers decode back to "abcbc", which is exactly why round-trip tests
        do not catch this.
        """
        a, b, c = ord("a"), ord("b"), ord("c")
        t = RegexTokenizer(pattern=r"\S+|\s+")
        t.merges = {(a, b): 256, (b, c): 257}
        t.vocab = {i: bytes([i]) for i in range(256)}
        t.vocab[256], t.vocab[257] = b"ab", b"bc"

        assert t.encode("abcbc") == [256, c, 257], (
            "expected the (a,b) merge to go first because its id is lower; "
            "picking the most frequent pair instead gives [97, 257, 257]"
        )

    def test_encoding_is_deterministic(self, regexed):
        s = "the quick brown fox"
        assert regexed.encode(s) == regexed.encode(s)

    def test_unknown_pair_stops_the_loop_rather_than_looping(self, regexed):
        # Text made only of bytes with no learned merge between them.
        assert regexed.decode(regexed.encode("\x01\x02\x03")) == "\x01\x02\x03"
