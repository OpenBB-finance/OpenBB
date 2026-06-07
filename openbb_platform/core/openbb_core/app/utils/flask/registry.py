"""Flask mount registry for managing multiple Flask apps and their OpenAPI specs."""

from typing import Any, Dict, Optional


class FlaskMountRegistry:
    """App-level registry for Flask mounts with centralized OpenAPI spec management.
    
    Solves the router attribute fragility issue by providing lifecycle-independent
    state management for multiple Flask app mounts.
    """
    
    _mounts: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_mount(
        cls,
        prefix: str,
        flask_app: Any,
        openapi_spec: Dict[str, Any],
        router: Optional[Any] = None
    ) -> None:
        """Register a Flask app mount with its OpenAPI metadata.
        
        Args:
            prefix: Mount path prefix (e.g., '/api/v1', '/legacy')
            flask_app: Flask application instance
            openapi_spec: Generated OpenAPI specification dict
            router: Optional Router instance for reference
        """
        cls._mounts[prefix] = {
            'app': flask_app,
            'spec': openapi_spec,
            'router': router,
        }
    
    @classmethod
    def get_aggregated_spec(cls) -> Dict[str, Any]:
        """Merge all registered Flask specs into single OpenAPI document.
        
        Returns:
            Aggregated OpenAPI spec with prefix-rewritten paths
        """
        aggregated: Dict[str, Any] = {
            'paths': {},
            'components': {'schemas': {}}
        }
        
        for prefix, mount_data in cls._mounts.items():
            spec = mount_data['spec']
            
            # Rewrite paths with mount prefix
            for path, path_item in spec.get('paths', {}).items():
                prefixed_path = f"{prefix.rstrip('/')}{path}"
                aggregated['paths'][prefixed_path] = path_item
            
            # Merge component schemas
            for schema_name, schema_def in spec.get('components', {}).get('schemas', {}).items():
                aggregated['components']['schemas'][schema_name] = schema_def
        
        return aggregated
    
    @classmethod
    def get_mount(cls, prefix: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific mount metadata.
        
        Args:
            prefix: Mount path prefix
            
        Returns:
            Mount data dict or None if not found
        """
        return cls._mounts.get(prefix)
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered mounts (primarily for testing)."""
        cls._mounts.clear()
    
    @classmethod
    def list_mounts(cls) -> list[str]:
        """List all registered mount prefixes."""
        return list(cls._mounts.keys())
