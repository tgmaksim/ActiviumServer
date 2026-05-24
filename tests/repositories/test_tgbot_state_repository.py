import pytest

from ..fixtures import tgbot_state, tgbot_state_repository

from src.support.repositories.tgbot_state_repository import TgbotStateRepository


@pytest.mark.asyncio
async def test_get_state(
    tgbot_state_repository: TgbotStateRepository,
    tgbot_state
):
    result = await tgbot_state_repository.get_state(
        tgbot_state.key
    )

    assert result is not None

    assert result.key == tgbot_state.key
    assert result.state == tgbot_state.state
    assert result.data == tgbot_state.data


@pytest.mark.asyncio
async def test_get_unknown_state_returns_none(
    tgbot_state_repository: TgbotStateRepository
):
    result = await tgbot_state_repository.get_state(
        "unknown_key"
    )

    assert result is None


@pytest.mark.asyncio
async def test_set_state_creates_state(
    tgbot_state_repository: TgbotStateRepository
):
    await tgbot_state_repository.set_state(
        "123_456",
        "waiting_email"
    )

    result = await tgbot_state_repository.get_state(
        "123_456"
    )

    assert result is not None

    assert result.key == "123_456"
    assert result.state == "waiting_email"


@pytest.mark.asyncio
async def test_set_state_updates_state(
    tgbot_state_repository: TgbotStateRepository,
    tgbot_state
):
    await tgbot_state_repository.set_state(
        tgbot_state.key,
        "waiting_photo"
    )

    result = await tgbot_state_repository.get_state(
        tgbot_state.key
    )

    assert result is not None
    assert result.state == "waiting_photo"


@pytest.mark.asyncio
async def test_set_state_accepts_none(
    tgbot_state_repository: TgbotStateRepository
):
    await tgbot_state_repository.set_state(
        "123_456",
        None
    )

    result = await tgbot_state_repository.get_state(
        "123_456"
    )

    assert result is not None
    assert result.state is None


@pytest.mark.asyncio
async def test_set_data_creates_data(
    tgbot_state_repository: TgbotStateRepository
):
    await tgbot_state_repository.set_data(
        "123_456",
        {
            "message_id": 100
        }
    )

    result = await tgbot_state_repository.get_state(
        "123_456"
    )

    assert result is not None

    assert result.data == {
        "message_id": 100
    }


@pytest.mark.asyncio
async def test_set_data_updates_data(
    tgbot_state_repository: TgbotStateRepository,
    tgbot_state
):
    await tgbot_state_repository.set_data(
        tgbot_state.key,
        {
            "new_key": "new_value"
        }
    )

    result = await tgbot_state_repository.get_state(
        tgbot_state.key
    )

    assert result is not None

    assert result.data == {
        "new_key": "new_value"
    }


@pytest.mark.asyncio
async def test_set_data_accepts_empty_dict(
    tgbot_state_repository: TgbotStateRepository
):
    await tgbot_state_repository.set_data(
        "123_456",
        {}
    )

    result = await tgbot_state_repository.get_state(
        "123_456"
    )

    assert result is not None
    assert result.data == {}
