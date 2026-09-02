"""get_stats and merge. Everything else is built on these two, so they are
worth getting exactly right before you write another line."""
import pytest
from bpe.tokenizer import get_stats, merge


class TestGetStats:
    def test_counts_adjacent_pairs(self):
        assert get_stats([1, 2, 3, 1, 2]) == {(1, 2): 2, (2, 3): 1, (3, 1): 1}

    def test_empty_list_has_no_pairs(self):
        assert get_stats([]) == {}

    def test_single_element_has_no_pairs(self):
        assert get_stats([7]) == {}

    def test_two_elements_give_one_pair(self):
        assert get_stats([7, 8]) == {(7, 8): 1}

    def test_overlapping_runs_are_counted_by_position(self):
        # [1,1,1] contains the pair (1,1) at index 0 and at index 1.
        assert get_stats([1, 1, 1]) == {(1, 1): 2}

    def test_accumulates_into_a_supplied_dict(self):
        counts = {(9, 9): 5}
        got = get_stats([1, 2], counts)
        assert got is counts, "pass the same dict back, do not copy it"
        assert counts == {(9, 9): 5, (1, 2): 1}

    def test_accumulating_across_chunks_sums(self):
        counts = {}
        get_stats([1, 2, 1, 2], counts)
        get_stats([1, 2], counts)
        assert counts[(1, 2)] == 3

    def test_does_not_mutate_its_input(self):
        ids = [1, 2, 3]
        get_stats(ids)
        assert ids == [1, 2, 3]

    def test_keys_are_tuples_not_lists(self):
        for key in get_stats([1, 2, 3]):
            assert isinstance(key, tuple)


class TestMerge:
    def test_replaces_every_occurrence(self):
        assert merge([1, 2, 3, 1, 2], (1, 2), 4) == [4, 3, 4]

    def test_absent_pair_leaves_the_list_alone(self):
        assert merge([1, 2, 3], (8, 9), 99) == [1, 2, 3]

    def test_empty_list(self):
        assert merge([], (1, 2), 3) == []

    def test_single_element_cannot_contain_a_pair(self):
        assert merge([1], (1, 2), 3) == [1]

    def test_pair_at_the_very_end(self):
        assert merge([5, 1, 2], (1, 2), 4) == [5, 4]

    def test_pair_at_the_very_start(self):
        assert merge([1, 2, 5], (1, 2), 4) == [4, 5]

    def test_whole_list_is_one_pair(self):
        assert merge([1, 2], (1, 2), 4) == [4]

    def test_repeated_token_does_not_double_consume(self):
        # [1,1,1] has (1,1) at index 0. After merging it, index 2 holds a lone 1
        # with nothing after it. Stepping by one instead of two gets this wrong.
        assert merge([1, 1, 1], (1, 1), 4) == [4, 1]

    def test_four_in_a_row_merges_into_two(self):
        assert merge([1, 1, 1, 1], (1, 1), 4) == [4, 4]

    def test_does_not_mutate_its_input(self):
        ids = [1, 2, 3, 1, 2]
        merge(ids, (1, 2), 4)
        assert ids == [1, 2, 3, 1, 2]

    def test_returns_a_list(self):
        assert isinstance(merge([1, 2], (1, 2), 4), list)
