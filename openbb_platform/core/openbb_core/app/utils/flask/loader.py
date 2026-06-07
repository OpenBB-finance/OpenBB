"""Flask extension loading integration."""

from typing import Any, Optional
from .introspection import _check_flask_available, FlaskIntrospector
from .adapter import OpenAPISpecGenerator
from .registry import FlaskMountRegistry


class FlaskExtensionLoader:
    """Integrates Flask app loading with OpenBB's extension system."""
    
    @staticmethod
    def detect_flask_entry_point(entry_point: str) -> bool:
        """Detect if an entry point references a Flask application."""
        try:
            module_path, app_name = entry_point.split(':')
            module = __import__(module_path, fromlist=[app_name])
            app = getattr(module, app_name)
            return FlaskExtensionLoader.validate_flask_app(app)
        except Exception:
            return False
    
    @staticmethod
    def load_flask_extension(entry_point: str, prefix: str = "/") -> Optional[Any]:
        """Load Flask app as OpenBB extension with OpenAPI metadata."""
        try:
            if not _check_flask_available():
                return None
                
            module_path, app_name = entry_point.split(':')
            module = __import__(module_path, fromlist=[app_name])
            flask_app = getattr(module, app_name)
            
            if FlaskExtensionLoader.validate_flask_app(flask_app):
                from openbb_core.app.router import Router
                from fastapi.middleware.wsgi import WSGIMiddleware

                router = Router()
                router.api_router.mount("/", WSGIMiddleware(flask_app))
                
                # Generate OpenAPI spec and register in centralized registry
                introspector = FlaskIntrospector(flask_app)
                routes = introspector.analyze_routes()
                openapi_spec = OpenAPISpecGenerator.generate_spec(routes)
                
                FlaskMountRegistry.register_mount(
                    prefix=prefix,
                    flask_app=flask_app,
                    openapi_spec=openapi_spec,
                    router=router
                )
                
                return router
            return None
        except Exception as e:
            print(f"Error loading Flask extension {entry_point}: {e}")
            return None
    
    @staticmethod
    def validate_flask_app(app: Any) -> bool:
        """Validate that the loaded object is a proper Flask application."""
        try:
            return (
                hasattr(app, 'url_map') and
                hasattr(app, 'view_functions') and
                hasattr(app, 'name')
            )
        except Exception:
            return False