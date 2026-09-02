"""BasicTokenizer: BPE straight over the bytes."""
import pytest
from bpe.tokenizer import BasicTokenizer
from .conftest import UNICODE_SAMPLES


class TestRoundTrip:
    """If these fail, every number you report later is noise."""

    @pytest.mark.parametrize("text", UNICODE_SAMPLES)
    def test_decode_of_encode_is_the_original(self, basic, text):
        assert basic.decode(basic.encode(text)) == text

    def test_round_trip_on_the_training_corpus(self, basic, corpus):
        assert basic.decode(basic.encode(corpus)) == corpus

    def test_round_trip_on_text_never_seen_in_training(self, basic):
        unseen = "Quetzalcoatl fourty-two ⟨brackets⟩ 987654321"
        assert basic.decode(basic.encode(unseen)) == unseen

    def test_empty_string_encodes_to_nothing(self, basic):
        assert basic.encode("") == []

    def test_empty_id_list_decodes_to_empty_string(self, basic):
        assert basic.decode([]) == ""

    def test_single_character_does_not_hang(self, basic):
        # The guard is `while len(ids) >= 2`. Without it this loops or throws.
        assert basic.decode(basic.encode("a")) == "a"


class TestTraining:
    def test_learns_the_requested_number_of_merges(self, corpus):
        t = BasicTokenizer()
        t.train(corpus, 300)
        assert len(t.merges) == 300 - 256

    def test_vocab_size_256_learns_nothing(self, corpus):
        t = BasicTokenizer()
        t.train(corpus, 256)
        assert len(t.merges) == 0

    def test_merge_ids_start_at_256_and_are_consecutive(self, basic):
        ids = sorted(basic.merges.values())
        assert ids == list(range(256, 256 + len(ids)))

    def test_merges_are_ordered_by_when_they_were_learned(self, basic):
        # dict preserves insertion order; the values must be increasing.
        assert list(basic.merges.values()) == sorted(basic.merges.values())

    def test_every_merge_key_is_a_pair_of_ints(self, basic):
        for pair in basic.merges:
            assert isinstance(pair, tuple) and len(pair) == 2
            assert all(isinstance(x, int) for x in pair)

    def test_vocab_covers_every_byte(self, basic):
        for b in range(256):
            assert basic.vocab[b] == bytes([b])

    def test_vocab_has_an_entry_per_merge(self, basic):
        assert len(basic.vocab) == 256 + len(basic.merges)

    def test_vocab_entry_is_the_concatenation_of_its_parts(self, basic):
        for (p0, p1), idx in basic.merges.items():
            assert basic.vocab[idx] == basic.vocab[p0] + basic.vocab[p1]

    def test_training_twice_does_not_accumulate_merges(self, corpus):
        t = BasicTokenizer()
        t.train(corpus, 300)
        t.train(corpus, 300)
        assert len(t.merges) == 44, "train() should reset, not append"

    def test_the_first_merge_is_the_most_common_pair(self, corpus):
        # Training takes the pair with the HIGHEST count. Using min here is the
        # mirror image of the encode-side bug and is just as quiet.
        from bpe.tokenizer import get_stats
        t = BasicTokenizer()
        t.train(corpus, 257)
        first_pair = next(iter(t.merges))
        counts = get_stats(list(corpus.encode("utf-8")))
        assert counts[first_pair] == max(counts.values())


class TestCompression:
    def test_encoding_is_shorter_than_the_raw_bytes(self, basic, corpus):
        assert len(basic.encode(corpus)) < len(corpus.encode("utf-8"))

    def test_more_merges_compress_at_least_as_well(self, corpus):
        small, large = BasicTokenizer(), BasicTokenizer()
        small.train(corpus, 280)
        large.train(corpus, 340)
        assert len(large.encode(corpus)) <= len(small.encode(corpus))

    def test_untrained_text_is_one_id_per_byte(self, corpus):
        t = BasicTokenizer()
        t.train(corpus, 256)
        s = "hello"
        assert t.encode(s) == list(s.encode("utf-8"))


class TestBytesNotCharacters:
    def test_multibyte_character_is_more_than_one_byte(self):
        assert len("é".encode("utf-8")) == 2
        assert len("héllo") == 5 and len("héllo".encode("utf-8")) == 6

    def test_untrained_emoji_costs_four_ids(self, corpus):
        t = BasicTokenizer()
        t.train(corpus, 256)
        assert len(t.encode("🙂")) == 4

    def test_decode_replaces_rather_than_raising_on_a_broken_sequence(self, basic):
        # A lone continuation byte is not valid UTF-8 on its own. errors="replace"
        # is why this returns a string instead of blowing up.
        out = basic.decode([0x80])
        assert isinstance(out, str)
        assert out == "�"
