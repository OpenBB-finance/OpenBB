"""Tests for Flask route introspection, AST analysis and docstring parsing."""

import importlib.util

import pytest

from openbb_core.app.utils.flask.ast_analysis import analyze_view_source
from openbb_core.app.utils.flask.docstrings import parse_docstring

FLASK_AVAILABLE = importlib.util.find_spec("flask") is not None


def test_parse_google_docstring():
    doc = """Get a thing.

    Long description here.

    Args:
        symbol: The ticker symbol.
        limit: Max results.
    """
    summary, description, params = parse_docstring(doc)
    assert summary == "Get a thing."
    assert description == "Long description here."
    assert params["symbol"] == "The ticker symbol."
    assert params["limit"] == "Max results."


def test_parse_numpy_docstring():
    doc = """Get a thing.

    Parameters
    ----------
    symbol
        The ticker symbol.
    limit
        Max results.
    """
    _, _, params = parse_docstring(doc)
    assert params["symbol"] == "The ticker symbol."
    assert params["limit"] == "Max results."


def test_parse_sphinx_docstring():
    doc = """Get a thing.

    :param symbol: The ticker symbol.
    :param limit: Max results.
    """
    _, _, params = parse_docstring(doc)
    assert params["symbol"] == "The ticker symbol."
    assert params["limit"] == "Max results."


def _view_typed_query():
    from flask import request

    limit = request.args.get("limit", type=int)
    name = request.args.get("name", "abc")
    return {"limit": limit, "name": name}


def test_ast_typed_and_default_query():
    query, _, body, _ = analyze_view_source(_view_typed_query)
    by_name = {p.name: p for p in query}
    assert by_name["limit"].schema["type"] == "integer"
    assert by_name["name"].schema["type"] == "string"
    assert by_name["name"].example == "abc"
    assert body is None


def _view_subscript_query():
    from flask import request

    return {"q": request.args["q"]}


def test_ast_subscript_query_is_required():
    query, _, _, _ = analyze_view_source(_view_subscript_query)
    by_name = {p.name: p for p in query}
    assert by_name["q"].required is True


def _view_getlist():
    from flask import request

    return {"ids": request.args.getlist("ids")}


def test_ast_getlist_is_array():
    query, _, _, _ = analyze_view_source(_view_getlist)
    by_name = {p.name: p for p in query}
    assert by_name["ids"].schema["type"] == "array"


def _view_to_dict():
    from flask import request

    return dict(request.args.to_dict())


def test_ast_to_dict_marks_partial():
    _, _, _, partial = analyze_view_source(_view_to_dict)
    assert partial is True


def _view_json_body():
    from flask import request

    data = request.get_json()
    return {"name": data["name"]}


def test_ast_json_body_with_keys():
    _, _, body, _ = analyze_view_source(_view_json_body)
    assert body is not None
    assert body.media_type == "application/json"
    assert "name" in body.schema.get("properties", {})


def _view_form_body():
    from flask import request

    return {"email": request.form["email"]}


def test_ast_form_body():
    _, _, body, _ = analyze_view_source(_view_form_body)
    assert body is not None
    assert body.media_type == "application/x-www-form-urlencoded"
    assert "email" in body.schema.get("properties", {})


def _view_header():
    from flask import request

    return {"auth": request.headers.get("Authorization")}


def test_ast_header_param():
    _, headers, _, _ = analyze_view_source(_view_header)
    assert {h.name for h in headers} == {"Authorization"}


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspector_path_converters():
    from flask import Flask

    from openbb_core.app.utils.flask.introspector import FlaskIntrospector

    app = Flask(__name__)

    @app.route("/items/<int:item_id>")
    def get_item(item_id):
        """Get item."""
        return {}

    @app.route("/users/<uuid:user_id>")
    def get_user(user_id):
        """Get user."""
        return {}

    @app.route("/pages/<any(home, about):page>")
    def get_page(page):
        """Get page."""
        return {}

    routes, _ = FlaskIntrospector(app).introspect()
    by_path = {r.path: r for r in routes}

    assert by_path["/items/{item_id}"].operations[0].parameters[0].schema == {
        "type": "integer"
    }
    assert by_path["/users/{user_id}"].operations[0].parameters[0].schema == {
        "type": "string",
        "format": "uuid",
    }
    assert by_path["/pages/{page}"].operations[0].parameters[0].schema["enum"] == [
        "home",
        "about",
    ]


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspector_class_based_view():
    from flask import Flask
    from flask.views import MethodView

    from openbb_core.app.utils.flask.introspector import FlaskIntrospector

    app = Flask(__name__)

    class ItemAPI(MethodView):
        def get(self):
            """List items."""
            return {}

        def post(self):
            """Create item."""
            return {}

    app.add_url_rule("/items", view_func=ItemAPI.as_view("items"))

    routes, _ = FlaskIntrospector(app).introspect()
    ops = {op.method: op for route in routes for op in route.operations}

    assert ops["get"].summary == "List items."
    assert ops["post"].summary == "Create item."


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspector_dedupes_operation_ids():
    from flask import Flask

    from openbb_core.app.utils.flask.introspector import FlaskIntrospector

    app = Flask(__name__)

    @app.route("/a")
    @app.route("/alias")
    def handler():
        """Aliased handler."""
        return {}

    routes, _ = FlaskIntrospector(app).introspect()
    operation_ids = [op.operation_id for route in routes for op in route.operations]
    assert len(operation_ids) == len(set(operation_ids))


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspector_reads_widget_config_attribute():
    from flask import Flask

    from openbb_core.app.utils.flask.introspector import FlaskIntrospector

    app = Flask(__name__)

    @app.route("/quote")
    def quote():
        """Get a quote."""
        return {}

    setattr(quote, "widget_config", {"name": "Quote", "category": "Equity"})

    routes, _ = FlaskIntrospector(app).introspect()
    assert routes[0].operations[0].widget_config == {
        "name": "Quote",
        "category": "Equity",
    }


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspector_ids_exclude_path_parameters():
    from flask import Flask

    from openbb_core.app.utils.flask.introspector import FlaskIntrospector

    app = Flask(__name__)

    @app.route("/quote/<symbol>")
    def quote(symbol):
        """Get a quote."""
        return {}

    routes, _ = FlaskIntrospector(app, "demo_flask").introspect()
    op = routes[0].operations[0]
    assert op.operation_id == "demo_flask_quote"
    assert op.widget_id == "demo_flask_quote"
    assert "{" not in op.operation_id and "symbol" not in op.operation_id


def _view_html_string():
    return "<html><body>hi</body></html>"


def _view_render_template():
    from flask import render_template_string

    return render_template_string("<p>{{ x }}</p>", x=1)


def _view_json_dict():
    return {"ok": True}


def test_returns_html_for_string_literal():
    from openbb_core.app.utils.flask.ast_analysis import returns_html

    assert returns_html(_view_html_string) is True


def test_returns_html_for_render_template():
    from openbb_core.app.utils.flask.ast_analysis import returns_html

    assert returns_html(_view_render_template) is True


def test_returns_html_false_for_dict():
    from openbb_core.app.utils.flask.ast_analysis import returns_html

    assert returns_html(_view_json_dict) is False


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspector_html_route_uses_text_html_response():
    from flask import Flask

    from openbb_core.app.utils.flask.introspector import FlaskIntrospector

    app = Flask(__name__)

    @app.route("/page")
    def page():
        """A page."""
        return "<html><body>hi</body></html>"

    routes, _ = FlaskIntrospector(app, "demo").introspect()
    content = routes[0].operations[0].responses["200"]["content"]
    assert "text/html" in content
    assert "application/json" not in content
