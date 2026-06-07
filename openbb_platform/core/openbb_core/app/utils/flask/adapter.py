"""Flask-to-OpenBB conversion logic."""

from typing import Any, Dict, List
from .introspection import FlaskIntrospector, FlaskRouteInfo


def is_flask_available() -> bool:
    """Check if Flask is available."""
    try:
        import flask
        return True
    except ImportError:
        return False


class OpenAPISpecGenerator:
    """Generate OpenAPI specification from Flask route metadata."""
    
    TYPE_MAP = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
    }
    
    @classmethod
    def generate_spec(cls, routes: List[FlaskRouteInfo]) -> Dict[str, Any]:
        """Generate OpenAPI spec dictionary from Flask routes."""
        paths: Dict[str, Any] = {}
        schemas: Dict[str, Any] = {}
        
        for route in routes:
            openapi_path = cls._convert_flask_path(route['path'])
            if openapi_path not in paths:
                paths[openapi_path] = {}
            
            for method in route['methods']:
                operation = cls._generate_operation(route, schemas)
                paths[openapi_path][method.lower()] = operation
        
        return {
            'paths': paths,
            'components': {'schemas': schemas}
        }
    
    @classmethod
    def _convert_flask_path(cls, flask_path: str) -> str:
        """Convert Flask path format to OpenAPI format."""
        import re
        return re.sub(r'<(?:int:)?(?:float:)?(?:path:)?([^>]+)>', r'{\1}', flask_path)
    
    @classmethod
    def _generate_operation(cls, route: FlaskRouteInfo, schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OpenAPI operation object for a route."""
        operation: Dict[str, Any] = {
            'summary': route['summary'] or f"{route['function_name']}",
            'operationId': f"{route['function_name']}_{route['path'].replace('/', '_').strip('_')}",
            'parameters': [],
            'responses': {
                '200': {'description': 'Successful Response'},
                '400': {'description': 'Bad Request'},
            }
        }
        
        if route['description']:
            operation['description'] = route['description']
        
        for param in route['path_params']:
            operation['parameters'].append(cls._generate_parameter(param, 'path'))
        
        for param in route['query_params']:
            operation['parameters'].append(cls._generate_parameter(param, 'query'))
        
        return operation
    
    @classmethod
    def _generate_parameter(cls, param: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Generate OpenAPI parameter object."""
        param_spec: Dict[str, Any] = {
            'name': param['name'],
            'in': location,
            'required': param['required'],
            'schema': {
                'type': cls.TYPE_MAP.get(param['type'], 'string'),
            }
        }
        
        if param.get('description'):
            param_spec['description'] = param['description']
        
        if not param['required'] and param.get('default') is not None:
            param_spec['schema']['default'] = param['default']
        
        return param_spec