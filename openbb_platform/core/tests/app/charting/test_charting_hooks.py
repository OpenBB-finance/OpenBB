"""Tests for chart lifecycle hooks: dispatch and real entry-point discovery.

Dispatch is driven with real ``ChartingHook`` objects through the public
``ChartingHooksManager`` constructor. Discovery is driven through a genuine
installed package (see ``conftest.py``); ``entry_points`` is never mocked.
"""

from openbb_core.app.charting import get_hooks_manager
from openbb_core.app.charting.hooks import (
    ChartingHook,
    ChartingHooksManager,
    ChartLifecycle,
    HookContext,
)

ALL_STAGES = list(ChartLifecycle)


class _RecordingHook(ChartingHook):
    name = "recording"
    priority = 10

    def __init__(self):
        self.seen: list[tuple[str, str]] = []

    def pre_figure(self, context):
        self.seen.append(("pre_figure", context.route))

    def post_figure(self, context):
        self.seen.append(("post_figure", context.route))
        context.content = {"patched": True}
        return context


class _ScopedHook(ChartingHook):
    name = "scoped"
    routes = ("/only/this",)

    def __init__(self):
        self.fired = False

    def pre_figure(self, context):
        self.fired = True


class TestChartingHookDispatch:
    """Dispatch ordering, scoping, and context handling with real hooks."""

    def test_dispatch_runs_matching_stage_methods(self):
        hook = _RecordingHook()
        manager = ChartingHooksManager(hooks=[hook])
        ctx = HookContext(
            route="/equity/price/historical", stage=ChartLifecycle.PRE_FIGURE
        )

        ctx = manager.dispatch(ChartLifecycle.PRE_FIGURE, ctx)
        ctx = manager.dispatch(ChartLifecycle.POST_FIGURE, ctx)

        assert hook.seen == [
            ("pre_figure", "/equity/price/historical"),
            ("post_figure", "/equity/price/historical"),
        ]
        # A returned context replaces the running one.
        assert ctx.content == {"patched": True}
        assert ctx.stage is ChartLifecycle.POST_FIGURE

    def test_route_scoped_hook_only_fires_for_its_route(self):
        scoped = _ScopedHook()
        manager = ChartingHooksManager(hooks=[scoped])

        manager.dispatch(
            ChartLifecycle.PRE_FIGURE,
            HookContext(route="/other/route", stage=ChartLifecycle.PRE_FIGURE),
        )
        assert scoped.fired is False

        manager.dispatch(
            ChartLifecycle.PRE_FIGURE,
            HookContext(route="/only/this", stage=ChartLifecycle.PRE_FIGURE),
        )
        assert scoped.fired is True

    def test_hooks_run_in_priority_order(self):
        order: list[str] = []

        class _First(ChartingHook):
            priority = 1

            def pre_figure(self, context):
                order.append("first")

        class _Second(ChartingHook):
            priority = 99

            def pre_figure(self, context):
                order.append("second")

        manager = ChartingHooksManager(hooks=[_Second(), _First()])
        manager.dispatch(
            ChartLifecycle.PRE_FIGURE,
            HookContext(route="/r", stage=ChartLifecycle.PRE_FIGURE),
        )
        assert order == ["first", "second"]

    def test_base_hook_methods_are_noops_for_every_stage(self):
        """A hook using the base implementations runs (and no-ops) at every stage."""

        class _BaseHook(ChartingHook):
            pass

        manager = ChartingHooksManager(hooks=[_BaseHook()])
        ctx = HookContext(route="/r", stage=ChartLifecycle.RESOLVE_DATA)
        for stage in ALL_STAGES:
            # Base methods return None, so the same context object is preserved.
            assert manager.dispatch(stage, ctx) is ctx

    def test_duck_typed_hook_without_stage_method_is_skipped(self):
        """A hook object lacking the dispatched stage method is skipped cleanly."""

        class _PartialHook:
            priority = 50

            def pre_figure(self, context):
                context.data = "touched"
                return context

            # Deliberately no ``post_render`` attribute at all.

        manager = ChartingHooksManager(hooks=[_PartialHook()])
        ctx = HookContext(route="/r", stage=ChartLifecycle.POST_RENDER)

        # ``getattr(hook, "post_render", None)`` is None -> the hook is skipped.
        assert manager.dispatch(ChartLifecycle.POST_RENDER, ctx) is ctx
        # The stage method it does define still runs for its own stage.
        assert manager.dispatch(ChartLifecycle.PRE_FIGURE, ctx).data == "touched"


class TestChartingHookDiscovery:
    """Discovery of hooks from the real installed extension package."""

    def test_hook_discovered_and_dispatched(self):
        """A hook registered via entry points is discovered and fires.

        The fixture also registers a deliberately broken hook entry point, so
        this exercises the resilient load path too.
        """
        manager = get_hooks_manager(reload=True)
        assert any(type(h).__name__ == "RecordingHook" for h in manager.hooks)

        ctx = HookContext(
            route="/equity/price/historical", stage=ChartLifecycle.POST_FIGURE
        )
        ctx = manager.dispatch(ChartLifecycle.POST_FIGURE, ctx)
        assert ctx.content == {"hooked": True}

    def test_hooks_manager_is_cached(self):
        """``get_hooks_manager`` returns the same instance until reloaded."""
        first = get_hooks_manager(reload=True)
        assert get_hooks_manager() is first
        assert get_hooks_manager(reload=True) is not first
