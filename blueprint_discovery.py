"""
API Version Management
Automatically discover and register all API versions
"""
import importlib
import os
from pathlib import Path

from flask import Flask


def register_api_versions(app: Flask) -> None:
    """
    Automatically discover and register all API versions

    Scans the routes directory for v1, v2, v3... folders
    and registers them as blueprints automatically
    """

    # Get routes directory path
    routes_dir = Path(__file__).parent / "routes"
    versions = []

    # Auto-discover all version folders (v1, v2, v3, etc.)
    for item in sorted(routes_dir.iterdir()):
        if item.is_dir() and item.name.startswith("v") and item.name[1:].isdigit():
            version_name = item.name
            try:
                # Dynamically import the version module
                module = importlib.import_module(f"routes.{version_name}")

                # Get the blueprint from the module (expects api_v1, api_v2, etc.)
                blueprint_name = f"api_{version_name}"
                if hasattr(module, blueprint_name):
                    blueprint = getattr(module, blueprint_name)
                    app.register_blueprint(blueprint)
                    app.logger.info(
                        f"✅ Registered API {version_name} at /api/{version_name}"
                    )
                    versions.append(
                        {
                            "version": version_name,
                            "base_url": f"/api/{version_name}",
                            "status": "stable" if version_name == "v1" else "beta",
                        }
                    )
                else:
                    app.logger.warning(
                        f"⚠️  No blueprint '{blueprint_name}' found in routes.{version_name}"
                    )

            except Exception as e:
                app.logger.error(f"❌ Failed to register {version_name}: {str(e)}")

    # Add API version info endpoint
    @app.route("/api/versions")
    def api_versions():
        """List all available API versions"""
        return {
            "versions": versions,
            "latest": versions[0]["version"] if versions else None,
            "recommended": "v1",
            "total": len(versions),
        }
