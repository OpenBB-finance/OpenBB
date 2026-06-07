"""Test script for Flask metadata layer implementation."""

def test_introspection():
    """Test Flask route introspection."""
    try:
        from flask import Flask, request
        from openbb_core.app.utils.flask.introspection import FlaskIntrospector
        
        app = Flask(__name__)
        
        @app.route('/test/<int:user_id>')
        def get_user(user_id):
            """Get user data.
            
            Retrieve user information by ID.
            
            Args:
                user_id: The user identifier
                include_details: Include detailed information
            """
            include_details = request.args.get('include_details', 'false')
            return {'user_id': user_id, 'details': include_details}
        
        introspector = FlaskIntrospector(app)
        routes = introspector.analyze_routes()
        
        assert len(routes) > 0
        route = routes[0]
        assert route['path'] == '/test/<int:user_id>'
        assert route['function_name'] == 'get_user'
        assert route['summary'] == 'Get user data.'
        assert len(route['path_params']) == 1
        assert route['path_params'][0]['name'] == 'user_id'
        
        print("✓ Introspection test passed")
        return True
    except Exception as e:
        print(f"✗ Introspection test failed: {e}")
        return False


def test_openapi_generation():
    """Test OpenAPI spec generation."""
    try:
        from openbb_core.app.utils.flask.adapter import OpenAPISpecGenerator
        
        routes = [{
            'path': '/test/<int:user_id>',
            'methods': ['GET'],
            'summary': 'Get user data',
            'description': 'Retrieve user information',
            'function_name': 'get_user',
            'path_params': [{'name': 'user_id', 'type': 'int', 'required': True, 'default': None, 'description': None}],
            'query_params': [{'name': 'include_details', 'type': 'bool', 'required': False, 'default': 'false', 'description': None}],
        }]
        
        spec = OpenAPISpecGenerator.generate_spec(routes)
        
        assert 'paths' in spec
        assert 'components' in spec
        assert '/test/{user_id}' in spec['paths']
        assert 'get' in spec['paths']['/test/{user_id}']
        
        operation = spec['paths']['/test/{user_id}']['get']
        assert operation['summary'] == 'Get user data'
        assert len(operation['parameters']) == 2
        
        print("✓ OpenAPI generation test passed")
        return True
    except Exception as e:
        print(f"✗ OpenAPI generation test failed: {e}")
        return False


def test_registry():
    """Test FlaskMountRegistry for multiple mount management."""
    try:
        from flask import Flask
        from openbb_core.app.utils.flask.registry import FlaskMountRegistry
        from openbb_core.app.utils.flask.introspection import FlaskIntrospector
        from openbb_core.app.utils.flask.adapter import OpenAPISpecGenerator
        
        # Clear registry for clean test
        FlaskMountRegistry.clear()
        
        # Create two Flask apps
        app_v1 = Flask('v1')
        @app_v1.route('/users')
        def v1_users():
            """V1 users endpoint."""
            return {'version': 'v1'}
        
        app_v2 = Flask('v2')
        @app_v2.route('/users')
        def v2_users():
            """V2 users endpoint."""
            return {'version': 'v2'}
        
        # Register both mounts
        for prefix, app in [('/api/v1', app_v1), ('/api/v2', app_v2)]:
            introspector = FlaskIntrospector(app)
            routes = introspector.analyze_routes()
            spec = OpenAPISpecGenerator.generate_spec(routes)
            FlaskMountRegistry.register_mount(prefix, app, spec)
        
        # Test registry operations
        assert len(FlaskMountRegistry.list_mounts()) == 2
        assert '/api/v1' in FlaskMountRegistry.list_mounts()
        assert '/api/v2' in FlaskMountRegistry.list_mounts()
        
        # Test aggregated spec
        aggregated = FlaskMountRegistry.get_aggregated_spec()
        assert '/api/v1/users' in aggregated['paths']
        assert '/api/v2/users' in aggregated['paths']
        
        # Test individual mount retrieval
        v1_mount = FlaskMountRegistry.get_mount('/api/v1')
        assert v1_mount is not None
        assert v1_mount['app'].name == 'v1'
        
        print("✓ Registry test passed")
        return True
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_loader_integration():
    """Test Flask extension loader with registry integration."""
    try:
        from flask import Flask
        from openbb_core.app.utils.flask.loader import FlaskExtensionLoader
        from openbb_core.app.utils.flask.registry import FlaskMountRegistry
        
        FlaskMountRegistry.clear()
        
        app = Flask(__name__)
        
        @app.route('/health')
        def health():
            """Health check endpoint."""
            return {'status': 'ok'}
        
        # Simulate loading
        if FlaskExtensionLoader.validate_flask_app(app):
            from openbb_core.app.utils.flask.introspection import FlaskIntrospector
            from openbb_core.app.utils.flask.adapter import OpenAPISpecGenerator
            
            introspector = FlaskIntrospector(app)
            routes = introspector.analyze_routes()
            spec = OpenAPISpecGenerator.generate_spec(routes)
            
            # Register in registry
            FlaskMountRegistry.register_mount('/test', app, spec)
            
            assert 'paths' in spec
            assert 'components' in spec
            assert len(FlaskMountRegistry.list_mounts()) == 1
            
            print("✓ Loader integration test passed")
            return True
    except Exception as e:
        print(f"✗ Loader integration test failed: {e}")
        return False


if __name__ == '__main__':
    print("Testing Flask metadata layer implementation...\n")
    
    results = []
    results.append(test_introspection())
    results.append(test_openapi_generation())
    results.append(test_registry())
    results.append(test_loader_integration())
    
    print(f"\n{'='*50}")
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print(f"{'='*50}")
