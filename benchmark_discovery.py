"""
Performance Benchmark cho Blueprint Auto-Discovery
"""
import time
import os
from app_factory import create_app
from blueprint_discovery import auto_register_blueprints

def benchmark_auto_discovery():
    """Benchmark auto-discovery performance"""
    
    print("🔬 Performance Benchmark - Blueprint Auto-Discovery")
    print("=" * 60)
    
    # Test 1: App creation với auto-discovery
    start_time = time.time()
    app = create_app()
    total_time = time.time() - start_time
    
    print(f"⏱️  Total app creation time: {total_time:.4f} seconds")
    
    # Test 2: Chỉ auto-discovery
    start_time = time.time()
    from flask import Flask
    test_app = Flask(__name__)
    count = auto_register_blueprints(test_app, verbose=False)
    discovery_time = time.time() - start_time
    
    print(f"🔍 Auto-discovery time: {discovery_time:.4f} seconds")
    print(f"📊 Registered {count} blueprints")
    
    # Test 3: Memory usage
    import psutil
    process = psutil.Process()
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    print(f"💾 Memory usage: {memory_usage:.2f} MB")
    
    # Test 4: Routes count
    with app.app_context():
        total_routes = len(list(app.url_map.iter_rules()))
    print(f"🛤️  Total routes registered: {total_routes}")
    
    # Performance ratio
    if total_time > 0:
        discovery_ratio = (discovery_time / total_time) * 100
        print(f"📈 Auto-discovery overhead: {discovery_ratio:.1f}% of total startup time")

def benchmark_manual_vs_auto():
    """So sánh manual registration vs auto-discovery"""
    
    print("\n🏁 Manual vs Auto-Discovery Comparison")
    print("=" * 50)
    
    # Manual registration simulation
    start_time = time.time()
    
    # Simulate manual imports (nhanh hơn vì đã biết trước)
    from routes.main import main_bp
    from routes.api import api_bp
    from routes.blog import blog_bp
    from routes.forms import forms_bp
    from routes.errors import errors_bp
    from routes.demo import demo_bp
    
    from flask import Flask
    manual_app = Flask(__name__)
    manual_app.register_blueprint(main_bp)
    manual_app.register_blueprint(api_bp)
    manual_app.register_blueprint(blog_bp)
    manual_app.register_blueprint(forms_bp)
    manual_app.register_blueprint(errors_bp)
    manual_app.register_blueprint(demo_bp)
    
    manual_time = time.time() - start_time
    
    # Auto-discovery
    start_time = time.time()
    auto_app = Flask(__name__)
    auto_count = auto_register_blueprints(auto_app, verbose=False)
    auto_time = time.time() - start_time
    
    print(f"⚡ Manual registration: {manual_time:.4f}s")
    print(f"🔍 Auto-discovery: {auto_time:.4f}s")
    
    if manual_time > 0:
        overhead = ((auto_time - manual_time) / manual_time) * 100
        print(f"📊 Auto-discovery overhead: +{overhead:.1f}%")
    
    print(f"📈 Auto-discovery registered: {auto_count} blueprints")

def simulate_large_project():
    """Simulate performance với nhiều blueprint files"""
    
    print("\n🏢 Large Project Simulation")
    print("=" * 40)
    
    # Count current files
    routes_dir = "routes"
    current_files = len([f for f in os.listdir(routes_dir) 
                        if f.endswith('.py') and not f.startswith('__')])
    
    print(f"📁 Current blueprint files: {current_files}")
    
    # Estimate for larger projects
    scenarios = [10, 25, 50, 100]
    
    for file_count in scenarios:
        if file_count <= current_files:
            continue
            
        # Rough estimate: 0.001s per additional file
        estimated_time = (file_count - current_files) * 0.001
        base_time = 0.05  # Base auto-discovery time
        estimated_total = base_time + estimated_time
        
        print(f"📊 {file_count:3d} files → ~{estimated_total:.3f}s startup time")

if __name__ == "__main__":
    benchmark_auto_discovery()
    benchmark_manual_vs_auto()
    simulate_large_project()
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS:")
    print("✅ Auto-discovery is acceptable for most projects")
    print("⚠️  Consider manual registration for 50+ blueprint files")  
    print("🚀 Use caching for production deployments")
    print("=" * 60)