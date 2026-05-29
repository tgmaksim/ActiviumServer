import pytest

from sqlalchemy.exc import IntegrityError

from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.referral_repository import ReferralRepository


@pytest.fixture
def referral_repository(session):
    return ReferralRepository(session)


@pytest.mark.asyncio
async def test_link_referral(
    referral_repository: ReferralRepository,
    parent_repository: ParentRepository,
    parent
):
    referral = await parent_repository.create_parent(
        100002
    )

    result = await referral_repository.link_referral(
        parent_id=parent.parent_id,
        referral_id=referral.parent_id,
        name="Maksim"
    )

    assert result is not None

    assert result.parent_id == parent.parent_id
    assert result.referral_id == referral.parent_id
    assert result.name == "Maksim"


@pytest.mark.asyncio
async def test_link_referral_does_nothing_on_conflict(
    referral_repository: ReferralRepository,
    parent_repository: ParentRepository,
    parent
):
    referral = await parent_repository.create_parent(
        100002
    )

    first = await referral_repository.link_referral(
        parent_id=parent.parent_id,
        referral_id=referral.parent_id,
        name="First"
    )

    second = await referral_repository.link_referral(
        parent_id=999999,
        referral_id=referral.parent_id,
        name="Second"
    )

    assert second is None

    result = await referral_repository.get_me_referral(
        referral.parent_id
    )

    assert result is not None

    assert result.parent_id == first.parent_id
    assert result.name == "First"


@pytest.mark.asyncio
async def test_get_count_my_referrals(
    referral_repository: ReferralRepository,
    parent_repository: ParentRepository,
    parent
):
    referral1 = await parent_repository.create_parent(
        100002
    )

    referral2 = await parent_repository.create_parent(
        100003
    )

    await referral_repository.link_referral(
        parent_id=parent.parent_id,
        referral_id=referral1.parent_id,
        name="First"
    )

    await referral_repository.link_referral(
        parent_id=parent.parent_id,
        referral_id=referral2.parent_id,
        name="Second"
    )

    result = await referral_repository.get_count_my_referrals(
        parent.parent_id
    )

    assert result == 2


@pytest.mark.asyncio
async def test_get_me_referral(
    referral_repository: ReferralRepository,
    parent_repository: ParentRepository,
    parent
):
    referral = await parent_repository.create_parent(
        100002
    )

    await referral_repository.link_referral(
        parent_id=parent.parent_id,
        referral_id=referral.parent_id,
        name="Maksim"
    )

    result = await referral_repository.get_me_referral(
        referral.parent_id
    )

    assert result is not None

    assert result.parent_id == parent.parent_id
    assert result.referral_id == referral.parent_id


@pytest.mark.asyncio
async def test_get_unknown_referral_returns_none(
    referral_repository: ReferralRepository
):
    result = await referral_repository.get_me_referral(
        999999
    )

    assert result is None


@pytest.mark.asyncio
async def test_link_referral_with_unknown_parent_raises(
    referral_repository: ReferralRepository,
    parent_repository: ParentRepository
):
    referral = await parent_repository.create_parent(
        100002
    )

    with pytest.raises(IntegrityError):
        await referral_repository.link_referral(
            parent_id=999999,
            referral_id=referral.parent_id,
            name="Maksim"
        )


@pytest.mark.asyncio
async def test_link_referral_with_unknown_referral_raises(
    referral_repository: ReferralRepository,
    parent
):
    with pytest.raises(IntegrityError):
        await referral_repository.link_referral(
            parent_id=parent.parent_id,
            referral_id=999999,
            name="Maksim"
        )


@pytest.mark.asyncio
async def test_link_self_referral_raises(
    referral_repository: ReferralRepository,
    parent
):
    with pytest.raises(IntegrityError):
        await referral_repository.link_referral(
            parent_id=parent.parent_id,
            referral_id=parent.parent_id,
            name="Maksim"
        )
