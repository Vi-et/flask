"""
Blueprint Auto-Discovery System
Enhanced version with more features
"""
import os
import importlib
import inspect
from typing import List, Tuple, Dict, Any
from flask import Flask, Blueprint


class BlueprintDiscovery:
    """Advanced Blueprint Auto-Discovery System"""
    
    def __init__(self, routes_dir: str = "routes"):
        self.routes_dir = routes_dir
        self.discovered_blueprints: List[Tuple[str, Blueprint]] = []
        self.failed_imports: List[Tuple[str, str]] = []
        
    def discover_blueprints(self) -> Dict[str, Any]:
        """Discover all blueprints in routes directory"""
        
        # Get current directory (where blueprint_discovery.py is located)
        current_dir = os.path.dirname(__file__)
        routes_path = os.path.join(current_dir, self.routes_dir)
        
        if not os.path.exists(routes_path):
            return {
                "success": False,
                "error": f"Routes directory '{self.routes_dir}' not found",
                "blueprints": [],
                "failed": []
            }
        
        self.discovered_blueprints.clear()
        self.failed_imports.clear()
        
        # Scan all Python files
        for filename in sorted(os.listdir(routes_path)):
            if self._should_process_file(filename):
                module_name = filename[:-3]  # Remove .py
                self._process_module(module_name)
        
        return {
            "success": True,
            "blueprints": self.discovered_blueprints,
            "failed": self.failed_imports,
            "total_found": len(self.discovered_blueprints),
            "total_failed": len(self.failed_imports)
        }
    
    def register_discovered_blueprints(self, app: Flask, discovery_result: Dict[str, Any]) -> int:
        """Register all discovered blueprints to Flask app"""
        
        if not discovery_result["success"]:
            print(f"❌ Discovery failed: {discovery_result['error']}")
            return 0
        
        registered_count = 0
        
        print("🔍 Auto-registering discovered blueprints...")
        
        for module_name, blueprint in discovery_result["blueprints"]:
            try:
                app.register_blueprint(blueprint)
                registered_count += 1
                
                # Get blueprint info
                prefix = getattr(blueprint, 'url_prefix', '') or ''
                routes_count = len(blueprint.deferred_functions)
                
                print(f"  ✅ {blueprint.name:12s} | {module_name:15s} | {prefix:10s} | {routes_count} routes")
                
            except Exception as e:
                print(f"  ❌ Failed to register {blueprint.name}: {str(e)}")
        
        # Show failed imports
        if discovery_result["failed"]:
            print("\n⚠️  Failed imports:")
            for module_name, error in discovery_result["failed"]:
                print(f"  • {module_name}.py: {error}")
        
        return registered_count
    
    def _should_process_file(self, filename: str) -> bool:
        """Check if file should be processed"""
        return (
            filename.endswith('.py') and 
            not filename.startswith('__') and
            not filename.startswith('.')
        )
    
    def _process_module(self, module_name: str) -> None:
        """Process a single module for blueprints"""
        try:
            # Import module
            module = importlib.import_module(f'{self.routes_dir}.{module_name}')
            
            # Find all blueprints in module
            blueprints_found = []
            
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    attr = getattr(module, attr_name)
                    
                    if isinstance(attr, Blueprint):
                        blueprints_found.append((module_name, attr))
                        self.discovered_blueprints.append((module_name, attr))

                
        except ImportError as e:
            self.failed_imports.append((module_name, f"Import error: {str(e)}"))
        except Exception as e:
            self.failed_imports.append((module_name, f"Unexpected error: {str(e)}"))



def auto_register_blueprints(app: Flask, routes_dir: str = "routes", verbose: bool = True) -> int:
    """
    Auto-discover and register all blueprints from routes directory
    
    Args:
        app: Flask application instance
        routes_dir: Directory containing route modules (default: 'routes')
        verbose: Print discovery information (default: True)
    
    Returns:
        Number of successfully registered blueprints
    """
    
    discovery = BlueprintDiscovery(routes_dir)
    result = discovery.discover_blueprints()
    
    if verbose:
        if result["success"]:
            print(f"🎯 Found {result['total_found']} blueprints in '{routes_dir}/' directory")
        else:
            print(f"❌ {result['error']}")
    
    registered = discovery.register_discovered_blueprints(app, result)
    
    if verbose and registered > 0:
        print(f"🎉 Successfully registered {registered} blueprints!")
    
    return registered


# Backward compatibility function
def register_blueprints_simple(app: Flask) -> None:
    """Simple auto-registration (backward compatible)"""
    auto_register_blueprints(app, verbose=True)