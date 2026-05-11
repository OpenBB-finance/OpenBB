"""Test the BasePlatformController."""

from unittest.mock import MagicMock, patch

import pytest

from openbb_cli.controllers.base_platform_controller import PlatformController, Session


@pytest.fixture
def mock_session():
    """Mock session fixture."""
    with patch(
        "openbb_cli.controllers.base_platform_controller.session",
        MagicMock(spec=Session),
    ) as mock:
        yield mock


def test_initialization_with_valid_params(mock_session):
    """Test the initialization of the BasePlatformController."""
    translators = {"dummy_translator": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )
    assert controller._name == "test"
    assert controller.translators == translators


def test_initialization_without_required_params():
    """Test the initialization of the BasePlatformController without required params."""
    with pytest.raises(ValueError):
        PlatformController(name="test", parent_path=["parent"])


def test_command_generation(mock_session):
    """Test the command generation method."""
    translator = MagicMock()
    translators = {"test_command": translator}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    assert "test_command" in controller.translators


def test_print_help(mock_session):
    """Test the print help method."""
    translators = {"test_command": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    with patch(
        "openbb_cli.controllers.base_platform_controller.MenuText"
    ) as mock_menu_text:
        controller.print_help()
        mock_menu_text.assert_called_once_with("/parent/test/")


def test_sub_controller_generation(mock_session):
    """Test the sub controller generation method."""
    translators = {"test_menu_item": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    assert "test_menu_item" in controller.translators


def test_intersect_data_processing_commands_resolves_obb_index(mock_session):
    """``OBBnnn`` syntax in ``--data`` is resolved to the registered OBBject's ``results``."""
    from openbb_core.app.model.obbject import OBBject

    translators = {"test_cmd": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    obj = MagicMock(spec=OBBject)
    obj.results = "real-results"
    mock_session.obbject_registry.obbjects = [obj]
    mock_session.obbject_registry.obbject_keys = []
    mock_session.obbject_registry.get.return_value = obj

    ns_parser = MagicMock()
    ns_parser.data = "OBB0"
    out = controller._intersect_data_processing_commands(ns_parser)
    assert out.data == "real-results"


def test_intersect_data_processing_commands_unknown_data_passes_through(mock_session):
    """Non-OBB string that doesn't match any registry entry is left as-is."""
    translators = {"test_cmd": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    mock_session.obbject_registry.obbjects = []
    mock_session.obbject_registry.obbject_keys = []
    mock_session.obbject_registry.get.return_value = None

    ns_parser = MagicMock()
    ns_parser.data = "raw-data"
    out = controller._intersect_data_processing_commands(ns_parser)
    assert out.data == "raw-data"


def test_intersect_data_processing_commands_no_data_attr(mock_session):
    """When ``ns_parser.data`` is absent, the helper short-circuits to return ns_parser."""
    translators = {"test_cmd": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    class Bare:
        pass

    ns_parser = Bare()
    out = controller._intersect_data_processing_commands(ns_parser)
    assert out is ns_parser


def _backend_with_refs(paths=None, routers=None):
    """Build a mock backend exposing ``reference_paths`` / ``reference_routers``."""
    backend = MagicMock()
    backend.reference_paths = paths or {}
    backend.reference_routers = routers or {}
    return backend


def test_get_command_description_uses_obb_reference(mock_session):
    """``_get_command_description`` reads ``backend.reference_paths`` first."""
    mock_session.obbject_registry.obbjects = []
    controller = PlatformController(
        name="test", parent_path=["parent"], translators={"test_dummy": MagicMock()}
    )
    controller._factory_backend = _backend_with_refs(
        paths={"/parent/test/list_indicators": {"description": "List indicators."}}
    )
    assert controller._get_command_description("list_indicators") == "list indicators"


def test_get_command_description_falls_back_to_parser_description(mock_session):
    """When the reference has no entry, the translator's parser description is used."""
    trl = MagicMock()
    trl.parser.description = "Quote command. Returns a quote."
    controller = PlatformController(
        name="test", parent_path=["parent"], translators={"test_quote": trl}
    )
    controller._factory_backend = _backend_with_refs()
    assert "quote command" in controller._get_command_description("quote")


def test_get_menu_description_uses_obb_reference(mock_session):
    """``_get_menu_description`` reads ``backend.reference_routers`` first."""
    controller = PlatformController(
        name="test",
        parent_path=["parent"],
        translators={"test_sub_command": MagicMock()},
    )
    controller._factory_backend = _backend_with_refs(
        routers={"/parent/test/sub": {"description": "Sub menu."}}
    )
    assert controller._get_menu_description("sub") == "sub menu"


def test_get_menu_description_falls_back_to_sub_commands(mock_session):
    """When no description is in the reference, sub-command names are joined."""
    translators = {
        "parent_test_inner_one": MagicMock(),
        "parent_test_inner_two": MagicMock(),
    }
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )
    controller._factory_backend = _backend_with_refs()
    desc = controller._get_menu_description("inner")
    assert "one" in desc and "two" in desc


def test_print_help_renders_menus_and_commands(mock_session):
    """``print_help`` walks CHOICES_MENUS and CHOICES_COMMANDS, then session.console.print."""
    mock_session.obbject_registry.obbjects = []
    controller = PlatformController(
        name="test", parent_path=["parent"], translators={"test_cmd": MagicMock()}
    )
    controller._factory_backend = _backend_with_refs()
    controller.CHOICES_MENUS = ["sub"]
    controller.CHOICES_COMMANDS = ["test_cmd"]
    controller.print_help()
    mock_session.console.print.assert_called()


def test_print_help_includes_cached_results(mock_session):
    """When the registry has results, print_help adds the 'Cached Results' header."""
    mock_session.obbject_registry.obbjects = [MagicMock()]
    mock_session.obbject_registry.all = {0: {"command": "/equity/quote"}}
    mock_session.settings.N_TO_DISPLAY_OBBJECT_REGISTRY = 5
    controller = PlatformController(
        name="test", parent_path=["parent"], translators={"test_q": MagicMock()}
    )
    controller._factory_backend = _backend_with_refs()
    controller.CHOICES_MENUS = []
    controller.CHOICES_COMMANDS = []
    controller.print_help()
    mock_session.console.print.assert_called()


def test_generate_controller_call_creates_call_method(mock_session):
    """``_generate_controller_call`` binds a ``call_<name>`` method that delegates to load_class."""
    sub_controller_cls = MagicMock()
    controller = PlatformController.__new__(PlatformController)
    controller._name = "test"
    controller.PATH = "/parent/test/"
    controller.path = ["parent", "test"]
    controller.queue = ["x"]
    controller.load_class = MagicMock(return_value=["after"])
    controller._generate_controller_call(
        controller=sub_controller_cls,
        name="sub",
        parent_path=["parent", "test"],
        translators={},
    )
    assert hasattr(controller, "call_sub")
    controller.call_sub([])
    controller.load_class.assert_called_once()


def _make_command_call_test_setup(mock_session, command_returns):
    """Helper: produce a controller with a generated ``call_<name>`` and stubs."""

    translator = MagicMock()
    translator.func.__name__ = "test_command"
    parser = MagicMock()
    translator.parser = parser
    translator.execute_func.return_value = command_returns
    translators = {"test_command": translator}

    controller = PlatformController.__new__(PlatformController)
    controller._name = "test"
    controller.PATH = "/parent/test/"
    controller.path = ["parent", "test"]
    controller.translators = translators
    controller.paths = {}
    controller.CHOICES_COMMANDS = []
    controller.parse_known_args_and_warn = MagicMock()
    controller._intersect_data_processing_commands = lambda ns: ns
    controller._generate_command_call(name="cmd", translator=translator)
    return controller, translator


def test_generated_call_no_parsed_args_short_circuits(mock_session):
    """If ``parse_known_args_and_warn`` returns falsy, the command body is skipped."""
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=None
    )
    controller.parse_known_args_and_warn.return_value = None
    controller.call_cmd([])
    translator.execute_func.assert_not_called()


def test_generated_call_with_obbject_results_dispatches_to_output_adapter(mock_session):
    """A successful command calls ``session.output_adapter.display`` with the OBBject."""
    from openbb_core.app.model.obbject import OBBject

    obbject = OBBject(results=[{"a": 1}, {"a": 2}])
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=obbject
    )
    ns = MagicMock()
    ns.export = ""
    ns.register_obbject = False
    ns.chart = False
    ns.sheet_name = None
    controller.parse_known_args_and_warn.return_value = ns
    mock_session.max_obbjects_exceeded.return_value = False
    mock_session.obbject_registry.register.return_value = True

    controller.call_cmd([])
    mock_session.output_adapter.display.assert_called_once()


def test_generated_call_wraps_list_in_obbject(mock_session):
    """A command returning a plain list gets wrapped in an ``OBBject`` before display."""
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=[{"a": 1}]
    )
    ns = MagicMock()
    ns.export = ""
    ns.register_obbject = False
    ns.chart = False
    ns.sheet_name = None
    controller.parse_known_args_and_warn.return_value = ns
    mock_session.max_obbjects_exceeded.return_value = False
    mock_session.obbject_registry.register.return_value = True
    controller.call_cmd([])
    mock_session.output_adapter.display.assert_called_once()


def test_generated_call_max_obbjects_exceeded_evicts_oldest(mock_session):
    """``max_obbjects_exceeded()=True`` triggers ``registry.remove()`` before register."""
    from openbb_core.app.model.obbject import OBBject

    obbject = OBBject(results=[{"a": 1}])
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=obbject
    )
    ns = MagicMock()
    ns.export = ""
    ns.register_obbject = True
    ns.chart = False
    ns.sheet_name = None
    controller.parse_known_args_and_warn.return_value = ns
    mock_session.max_obbjects_exceeded.return_value = True
    mock_session.obbject_registry.register.return_value = True
    controller.call_cmd([])
    mock_session.obbject_registry.remove.assert_called_once()


def test_generated_call_dict_result_is_dataframed(mock_session):
    """A dict result is wrapped via ``pd.DataFrame.from_dict`` and printed."""
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns={"a": 1, "b": 2}
    )
    ns = MagicMock()
    ns.export = ""
    ns.register_obbject = False
    ns.chart = False
    ns.sheet_name = None
    controller.parse_known_args_and_warn.return_value = ns
    controller.call_cmd([])
    mock_session.console.print.assert_called()


def test_generated_call_export_branch_invokes_export_data(mock_session):
    """``ns.export`` + dict result → ``export_data`` is called.

    The generated method's local ``df`` is only populated in the dict-result
    branch (OBBject results route through ``output_adapter.display``, which
    handles export internally). The dict must be list-valued so
    ``pd.DataFrame.from_dict(orient='columns')`` succeeds — scalar values
    raise inside the wrapping try/except and skip ``export_data``.
    """
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns={"a": [1, 2], "b": [3, 4]}
    )
    ns = MagicMock()
    ns.export = ["csv"]
    ns.chart = False
    ns.sheet_name = None
    controller.parse_known_args_and_warn.return_value = ns
    with (
        patch(
            "openbb_cli.controllers.base_platform_controller.export_data"
        ) as export_data,
        patch("openbb_cli.controllers.base_platform_controller.print_rich_table"),
    ):
        controller.call_cmd([])
    export_data.assert_called_once()


def test_generate_sub_controllers_skips_path_value_entries(mock_session):
    """Entries in ``paths`` whose value is ``"path"`` (leaf marker) are skipped."""
    translator_outer = MagicMock()
    translators = {"test_inner_command": translator_outer}
    controller = PlatformController.__new__(PlatformController)
    controller._name = "test"
    controller.PATH = "/parent/test/"
    controller.path = ["parent", "test"]
    controller.translators = translators
    controller.paths = {"inner": "menu", "leaf": "path"}
    controller.CHOICES_COMMANDS = ["test_inner_command"]
    with patch.object(controller, "_generate_controller_call") as gen:
        controller._generate_sub_controllers()
    assert gen.call_count == 1
    assert gen.call_args[1]["name"] == "inner"


def test_link_obbject_to_data_processing_commands_sets_choices(mock_session):
    """``_link_obbject_to_data_processing_commands`` writes ``OBBn`` + register_keys
    onto every translator action with ``dest == "data"``."""
    translator = MagicMock()
    action = MagicMock()
    action.dest = "data"
    other = MagicMock()
    other.dest = "symbol"
    translator._parser._actions = [other, action]
    obj_keyed = MagicMock()
    obj_keyed.extra = {"register_key": "myresult"}
    obj_unkeyed = MagicMock()
    obj_unkeyed.extra = {}
    mock_session.obbject_registry.obbjects = [obj_keyed, obj_unkeyed]

    controller = PlatformController.__new__(PlatformController)
    controller.translators = {"x": translator}
    controller._link_obbject_to_data_processing_commands()
    assert action.choices == ["OBB0", "OBB1", "myresult"]
    assert action.type is str
    assert action.nargs is None


def test_generated_call_register_key_already_taken_warns(mock_session):
    """``register_key`` collision prints a yellow warning instead of overwriting."""
    from openbb_core.app.model.obbject import OBBject

    obbject = OBBject(results=[{"a": 1}])
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=obbject
    )
    ns = MagicMock(
        export="",
        register_obbject=False,
        register_key="existing",
        chart=False,
        sheet_name=None,
    )
    controller.parse_known_args_and_warn.return_value = ns
    mock_session.obbject_registry.obbject_keys = ["existing"]
    controller.call_cmd([])
    msgs = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("already exists" in m for m in msgs)


def test_generated_call_store_obbject_with_show_msg(mock_session):
    """``store_obbject=True`` AND ``SHOW_MSG_OBBJECT_REGISTRY=True`` prints the cache notice."""
    from openbb_core.app.model.obbject import OBBject

    obbject = OBBject(results=[{"a": 1}])
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=obbject
    )
    ns = MagicMock(export="", register_obbject=True, chart=False, sheet_name=None)
    del ns.register_key
    controller.parse_known_args_and_warn.return_value = ns
    mock_session.max_obbjects_exceeded.return_value = False
    mock_session.obbject_registry.register.return_value = True
    mock_session.settings.SHOW_MSG_OBBJECT_REGISTRY = True
    mock_session.obbject_registry.obbjects = []
    controller._link_obbject_to_data_processing_commands = MagicMock()
    controller.update_completer = MagicMock()
    controller.CHOICES_GENERATION = False
    mock_session.output_adapter.display.side_effect = None
    controller.call_cmd([])
    msgs = [str(c) for c in mock_session.console.print.call_args_list]
    assert any(("Added" in m and "cached" in m) for m in msgs), f"calls={msgs!r}"


def test_generated_call_display_error_falls_back_to_results(mock_session):
    """When ``output_adapter.display`` raises, the fallback prints raw results."""
    from openbb_core.app.model.obbject import OBBject

    obbject = OBBject(results=[{"a": 1}])
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=obbject
    )
    ns = MagicMock(export="", register_obbject=False, chart=False, sheet_name=None)
    del ns.register_key
    controller.parse_known_args_and_warn.return_value = ns
    mock_session.output_adapter.display.side_effect = RuntimeError("display oops")
    controller.call_cmd([])
    msgs = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("Display error" in m for m in msgs)


def test_generated_call_non_obbject_non_dict_result_falls_through(mock_session):
    """A scalar (non-OBBject, non-dict) result is printed via ``console.print``."""
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns=42
    )
    ns = MagicMock(export="", register_obbject=False, chart=False, sheet_name=None)
    del ns.register_key
    controller.parse_known_args_and_warn.return_value = ns
    controller.call_cmd([])
    mock_session.console.print.assert_called()


def test_generated_call_sheet_name_list_unwrapped(mock_session):
    """``sheet_name=['Foo']`` is unwrapped to ``'Foo'`` for ``export_data``."""
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns={"a": [1, 2], "b": [3, 4]}
    )
    ns = MagicMock(export=["xlsx"], chart=False, sheet_name=["MySheet"])
    controller.parse_known_args_and_warn.return_value = ns
    with (
        patch(
            "openbb_cli.controllers.base_platform_controller.export_data"
        ) as export_data,
        patch("openbb_cli.controllers.base_platform_controller.print_rich_table"),
    ):
        controller.call_cmd([])
    assert export_data.call_args[1]["sheet_name"] == "MySheet"


def test_generated_call_chart_export_extracts_fig(mock_session):
    """``ns.chart=True`` + export → ``obbject.chart.fig`` is extracted into ``fig``."""

    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns={"a": [1, 2]}
    )
    ns = MagicMock(export=["png"], chart=True, sheet_name=None)
    controller.parse_known_args_and_warn.return_value = ns
    with (
        patch(
            "openbb_cli.controllers.base_platform_controller.export_data"
        ) as export_data,
        patch("openbb_cli.controllers.base_platform_controller.print_rich_table"),
    ):
        controller.call_cmd([])
    export_data.assert_called_once()


def test_generated_call_export_with_empty_df_warns(mock_session):
    """When ``ns.export`` is set but the local ``df`` is empty, a yellow warning runs."""
    controller, translator = _make_command_call_test_setup(
        mock_session, command_returns="just-a-string"
    )
    ns = MagicMock(export=["csv"], chart=False, sheet_name=None)
    controller.parse_known_args_and_warn.return_value = ns
    controller.call_cmd([])
    msgs = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("No data to export" in m for m in msgs)


def test_factory_translators_picked_up_from_class_attrs(mock_session):
    """When the factory stashes ``_factory_translators`` on the class, the
    controller picks them up without ``platform_target`` or ``translators=``."""
    fake_translator = MagicMock()
    fake_translator._parser = MagicMock()
    fake_translator._parser._actions = []

    Subclass = type(
        "FactoryWiredController",
        (PlatformController,),
        {
            "_factory_backend": MagicMock(),
            "_factory_translators": {"x_quote": fake_translator},
            "_factory_paths": {"sub": "subpath"},
        },
    )
    controller = Subclass(name="x", parent_path=["parent"])
    assert controller.translators == {"x_quote": fake_translator}
    assert controller.paths == {"sub": "subpath"}


def test_legacy_platform_target_path_imports_obb(mock_session, monkeypatch):
    """``platform_target=...`` falls back to the legacy ``obb`` walk."""
    import sys
    import types

    fake_obb = MagicMock()
    fake_obb.reference = {"paths": {"/parent/x/quote": {"description": "q"}}}
    fake_module = types.ModuleType("openbb")
    fake_module.obb = fake_obb
    monkeypatch.setitem(sys.modules, "openbb", fake_module)

    fake_processor = MagicMock()
    fake_processor.translators = {"x_quote": MagicMock(_parser=MagicMock(_actions=[]))}
    fake_processor.paths = {}
    monkeypatch.setattr(
        "openbb_cli.argparse_translator.argparse_class_processor.ArgparseClassProcessor",
        MagicMock(return_value=fake_processor),
    )
    PlatformController(
        name="x",
        parent_path=["parent"],
        platform_target=MagicMock(),
    )


def test_init_raises_when_no_source_provided(mock_session):
    """Constructing without translators / target / factory raises ValueError."""
    bare = type("Bare", (PlatformController,), {})
    with pytest.raises(ValueError, match="needs one of"):
        bare(name="x", parent_path=["parent"])


def test_get_reference_paths_falls_back_to_local_backend_when_no_factory(
    mock_session, monkeypatch
):
    """Without a factory backend, ``_get_reference_paths`` builds a LocalBackend."""
    fake_backend = MagicMock()
    fake_backend.reference_paths = {"/x": {"description": "from local"}}
    monkeypatch.setattr(
        "openbb_cli.backend.LocalBackend", MagicMock(return_value=fake_backend)
    )
    controller = PlatformController(
        name="x", parent_path=["parent"], translators={"x_q": MagicMock()}
    )
    controller._factory_backend = None
    assert controller._get_reference_paths() == {"/x": {"description": "from local"}}


def test_get_reference_routers_falls_back_to_local_backend_when_no_factory(
    mock_session, monkeypatch
):
    """``_get_reference_routers`` falls back to ``LocalBackend`` when no factory is set."""
    fake_backend = MagicMock()
    fake_backend.reference_routers = {"/x/": {"description": "menu desc"}}
    monkeypatch.setattr(
        "openbb_cli.backend.LocalBackend", MagicMock(return_value=fake_backend)
    )
    controller = PlatformController(
        name="x", parent_path=["parent"], translators={"x_q": MagicMock()}
    )
    controller._factory_backend = None
    assert controller._get_reference_routers() == {"/x/": {"description": "menu desc"}}


def test_print_help_emits_warnings(mock_session):
    """``MenuText.warnings`` populated → ``print_help`` prints each formatted warning."""
    from openbb_cli.controllers import base_platform_controller as mod

    with patch.object(mod, "MenuText") as MenuText:
        mt_inst = MagicMock()
        mt_inst.warnings = ["{'cmd': 'broken'}"]
        mt_inst.menu_text = "..."
        MenuText.return_value = mt_inst
        mock_session.obbject_registry.obbjects = []
        controller = PlatformController(
            name="test", parent_path=["parent"], translators={"test_q": MagicMock()}
        )
        controller._factory_backend = _backend_with_refs()
        controller.CHOICES_MENUS = []
        controller.CHOICES_COMMANDS = []
        controller.print_help()
    msgs = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("cmd: broken" in m for m in msgs)
