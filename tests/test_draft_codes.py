def test_code_of_six_chars():
    from tgdraft.managers.draft_manager import DraftManager

    m = DraftManager(None)
    assert 6 == len(m._produce_code())
