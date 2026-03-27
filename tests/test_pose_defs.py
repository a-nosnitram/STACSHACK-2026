from pwp_game.pose.pose_defs import DEFAULT_POSES, PoseName


def test_default_poses_are_defined() -> None:
    names = {p.name for p in DEFAULT_POSES}
    assert PoseName.PUNCH in names
    assert PoseName.KICK in names
    assert PoseName.SLASH in names
