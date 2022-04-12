import pytest

try:
    from disnake.ext import commands
    from bots.discord import helpers
except ImportError:
    pytest.skip(allow_module_level=True)


# pylint: disable=R0903,W0212


@pytest.mark.bots
def test_missing_sequential():
    test = helpers._MissingSentinel()
    assert test.__eq__("hello") is False
    assert test.__bool__() is False
    assert test.__repr__() == "..."


@pytest.mark.bots
def test_hash_user_id():
    value = helpers.hash_user_id("Didier")

    assert value


@pytest.mark.bots
def test_fancy_traceback(recorder):
    value = helpers.fancy_traceback(ValueError("You did something wrong which is bad."))

    recorder.capture(value)


class MockCommand:
    def __init__(self):
        self.usage = "Uses"
        self.qualified_name = "Serious Name"


@pytest.mark.bots
def test_GSTHelpCommand():
    test = helpers.GSTHelpCommand()
    setattr(test, "clean_prefix", "hello")
    response = test.get_command_signature(MockCommand())
    assert isinstance(response, str)

    test.add_bot_commands_formatting([1, 2, 4], "Hello")


gst_bot = helpers.GSTBot()


class MockMessage:
    def delete(self):
        return True


class MockCTX:
    def __init__(self):
        self.message = MockMessage()


class MockResponded:
    def __init__(self, responded):
        self._responded = responded


class MockName:
    def __init__(self, name):
        self.name = name


class MockGuild:
    def __init__(self):
        self.id = "1234"
        self.name = "Mark"
        self.member_count = 200


class MockChannel:
    def __init__(self, channel):
        self.name = channel


class MockInter:
    def __init__(self, responded, option=None, name=None, guild=None):
        self.response = MockResponded(responded)
        self.option = option
        self.name = MockName(name)
        self.guid = guild if guild else False
        self.channel = MockChannel("Main")


@pytest.mark.bots
def test_load_all_extensions():
    with pytest.raises(FileNotFoundError):
        gst_bot.load_all_extensions("cmds")


@pytest.mark.bots
@pytest.mark.anyio
def test_on_command_error():
    gst_bot.on_command_error(MockCTX(), commands.MissingPermissions("Hello"))


@pytest.mark.bots
@pytest.mark.anyio
@pytest.mark.parametrize(
    "responded, error",
    [
        (True, commands.NoPrivateMessage),
        (False, commands.NoPrivateMessage),
        (True, commands.MissingPermissions),
        (False, commands.MissingPermissions),
        (True, commands.CheckAnyFailure),
        (False, commands.CheckAnyFailure),
        (True, "Hello"),
        (False, "Hello"),
    ],
)
def test_on_slash_command_error(responded, error):
    inter = MockInter(responded)
    gst_bot.on_slash_command_error(inter, error)


@pytest.mark.bots
@pytest.mark.anyio
@pytest.mark.parametrize(
    "option, name, guild", [("...", "...", True), ("Hello", "Hello", False)]
)
def test_on_application_command(option, name, guild):
    inter = MockInter(True, option, name, guild)
    gst_bot.on_application_command(inter)


@pytest.mark.bots
@pytest.mark.anyio
@pytest.mark.parametrize("responded", [True, False])
def test_on_user_command_error(responded):
    inter = MockInter(responded)
    gst_bot.on_user_command_error(inter, commands.NoPrivateMessage)


@pytest.mark.bots
@pytest.mark.anyio
@pytest.mark.parametrize("responded", [True, False])
def test_on_message_command_error(responded):
    inter = MockInter(responded)
    gst_bot.on_message_command_error(inter, commands.NoPrivateMessage)


@pytest.mark.bots
@pytest.mark.anyio
def test_on_ready():
    gst_bot.on_ready()
