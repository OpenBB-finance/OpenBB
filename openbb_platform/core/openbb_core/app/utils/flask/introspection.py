"""Flask route analysis and introspection utilities."""

import inspect
import re
import sys
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from werkzeug.routing import Rule


class FlaskParam(TypedDict):
    """Flask parameter metadata."""
    name: str
    type: str
    required: bool
    default: Any
    description: Optional[str]


class FlaskRouteInfo(TypedDict):
    """Flask route metadata structure."""
    path: str
    methods: List[str]
    summary: Optional[str]
    description: Optional[str]
    function_name: str
    path_params: List[FlaskParam]
    query_params: List[FlaskParam]


def _check_flask_available() -> bool:
    """Check if Flask is available without importing it."""
    return 'flask' in sys.modules or _can_import_flask()

def _can_import_flask() -> bool:
    """Safely attempt Flask import."""
    try:
        import flask
        return True
    except ImportError:
        return False

class FlaskIntrospector:
    """Analyzes Flask applications to extract route information."""
    
    def __init__(self, flask_app: Any):
        if not _check_flask_available():
            raise ImportError("Flask is not available in the current environment")
        self.flask_app = flask_app
        self.url_map = flask_app.url_map
    
    def analyze_routes(self) -> List[FlaskRouteInfo]:
        """Analyze all routes in the Flask application."""
        routes_info = []
        
        for rule in self.url_map.iter_rules():
            if rule.endpoint != 'static':  # Skip static file routes
                route_info = self._analyze_single_route(rule)
                if route_info:
                    routes_info.append(route_info)
        
        return routes_info
    
    def _analyze_single_route(self, rule: "Rule") -> Optional[FlaskRouteInfo]:
        """Analyze a single Flask route."""
        try:
            view_function = self.flask_app.view_functions.get(rule.endpoint)
            if not view_function:
                return None
            
            docstring_info = self._parse_docstring(view_function)
            path_params = [{'name': arg, 'type': 'str', 'required': True, 'default': None, 'description': None} for arg in rule.arguments]
            query_params = self._extract_query_parameters(view_function, docstring_info)
            
            route_info: FlaskRouteInfo = {
                'path': rule.rule,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'summary': docstring_info.get('summary'),
                'description': docstring_info.get('description'),
                'function_name': view_function.__name__,
                'path_params': path_params,
                'query_params': query_params,
            }
            
            return route_info
            
        except Exception as e:
            print(f"Warning: Could not analyze route {rule.rule}: {e}")
            return None
    
    def _parse_docstring(self, view_function) -> Dict[str, Any]:
        """Parse Google-style docstring into structured metadata."""
        docstring = inspect.getdoc(view_function)
        if not docstring:
            return {'summary': None, 'description': None, 'params': {}}
        
        lines = docstring.split('\n')
        summary = lines[0].strip() if lines else None
        description_lines = []
        param_descriptions = {}
        
        in_args_section = False
        in_description = True
        
        for line in lines[1:]:
            stripped = line.strip()
            
            # Detect section headers
            if stripped.lower() in ['args:', 'arguments:', 'parameters:', 'returns:', 'return:', 'raises:', 'examples:', 'example:', 'note:', 'notes:']:
                in_description = False
                in_args_section = stripped.lower() in ['args:', 'arguments:', 'parameters:']
                continue
            
            if in_args_section and stripped:
                param_match = re.match(r'(\w+)(?:\s*\([^)]+\))?:\s*(.+)', stripped)
                if param_match:
                    param_descriptions[param_match.group(1)] = param_match.group(2).strip()
            elif in_description and stripped:
                description_lines.append(stripped)
        
        description = ' '.join(description_lines) if description_lines else None
        return {'summary': summary, 'description': description, 'params': param_descriptions}
    
    def _extract_query_parameters(self, view_function, docstring_info: Dict[str, Any]) -> List[FlaskParam]:
        """Extract query parameters from Flask view function."""
        query_params: List[FlaskParam] = []
        
        try:
            source = inspect.getsource(view_function)
            param_pattern = r'request\.args\.get\([\'"]([^\'\"]+)[\'"](?:,\s*[\'"]?([^\'\"]*)[\'"]?)?\)'
            matches = re.findall(param_pattern, source)
            
            for match in matches:
                param_name = match[0]
                default_value = match[1] if len(match) > 1 and match[1] else None
                
                param: FlaskParam = {
                    'name': param_name,
                    'default': default_value,
                    'type': self._infer_parameter_type(default_value),
                    'required': default_value is None,
                    'description': docstring_info['params'].get(param_name)
                }
                query_params.append(param)
                
        except Exception as e:
            print(f"Warning: Could not extract query parameters from {view_function.__name__}: {e}")
        
        return query_params
    
    def _extract_docstring(self, view_function) -> Optional[str]:
        """Extract and clean docstring from view function."""
        docstring = inspect.getdoc(view_function)
        if docstring:
            lines = docstring.strip().split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            return ' '.join(cleaned_lines)
        return None
    
    def _infer_parameter_type(self, default_value: Optional[str]) -> str:
        """Infer parameter type from default value."""
        if default_value is None:
            return 'str'
        elif default_value.isdigit():
            return 'int'
        elif default_value.lower() in ['true', 'false']:
            return 'bool'
        else:
            return 'str'