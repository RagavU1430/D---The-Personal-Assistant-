from app.agent.planner import Planner
from app.tools.registry import ToolRegistry


class ExampleTool:
    name = "open_application"
    description = "Opens an application"


def test_planner_creates_structured_plan() -> None:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    plan = Planner(registry).plan("Open VS Code.")

    assert plan.goal.lower().startswith("open")
    assert plan.steps
    assert plan.steps[0].action_type == "tool"
    assert plan.steps[0].tool == "open_application"


def test_invalid_plan_tool_is_rejected() -> None:
    registry = ToolRegistry()
    planner = Planner(registry)

    invalid_plan = planner.create_plan("Run arbitrary shell command", tool="arbitrary_shell")

    try:
        planner.validate_plan(invalid_plan)
    except ValueError:
        return

    raise AssertionError("Expected plan validation to reject an unregistered tool.")
