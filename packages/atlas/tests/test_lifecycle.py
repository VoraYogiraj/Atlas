from atlas.lifecycle.lifecycle import AtlasLifecycle


def test_created_state():
    lifecycle = AtlasLifecycle.CREATED

    assert str(lifecycle) == "created"
    assert not lifecycle.is_active()
    assert not lifecycle.is_terminal()


def test_active_state():
    lifecycle = AtlasLifecycle.ACTIVE

    assert str(lifecycle) == "active"
    assert lifecycle.is_active()
    assert not lifecycle.is_terminal()


def test_archived_state():
    lifecycle = AtlasLifecycle.ARCHIVED

    assert str(lifecycle) == "archived"
    assert not lifecycle.is_active()
    assert lifecycle.is_terminal()


def test_deleted_state():
    lifecycle = AtlasLifecycle.DELETED

    assert str(lifecycle) == "deleted"
    assert not lifecycle.is_active()
    assert lifecycle.is_terminal()


def test_valid_transitions():
    assert AtlasLifecycle.CREATED.can_transition_to(
        AtlasLifecycle.ACTIVE
    )

    assert AtlasLifecycle.CREATED.can_transition_to(
        AtlasLifecycle.ARCHIVED
    )

    assert AtlasLifecycle.ACTIVE.can_transition_to(
        AtlasLifecycle.ARCHIVED
    )

    assert AtlasLifecycle.ACTIVE.can_transition_to(
        AtlasLifecycle.DELETED
    )

    assert AtlasLifecycle.ARCHIVED.can_transition_to(
        AtlasLifecycle.DELETED
    )


def test_invalid_transitions():
    assert not AtlasLifecycle.CREATED.can_transition_to(
        AtlasLifecycle.DELETED
    )

    assert not AtlasLifecycle.ARCHIVED.can_transition_to(
        AtlasLifecycle.ACTIVE
    )

    assert not AtlasLifecycle.DELETED.can_transition_to(
        AtlasLifecycle.ACTIVE
    )

    assert not AtlasLifecycle.DELETED.can_transition_to(
        AtlasLifecycle.DELETED
    )