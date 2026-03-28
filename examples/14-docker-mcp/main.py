#!/usr/bin/env python3
"""Example 14: Docker MCP - Real Container Operations.

Creates sample Dockerfile and demonstrates Docker operations.
"""

,os
from pathlib import Path
import subprocess


def create_sample_docker_project() -> Any:
    """Create sample project with Dockerfile."""
    base_dir = Path(__file__).parent / "sample_docker_project"
    base_dir.mkdir(exist_ok=True)
    
    # Create simple Python app
    (base_dir / "app.py").write_text('''#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello from Docker!")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Server running on port 8000")
    server.serve_forever()
''')
    
    # Create Dockerfile
    (base_dir / "Dockerfile").write_text('''FROM python:3.11-slim

WORKDIR /app

COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
''')
    
    # Create TODO
    (base_dir / "TODO.md").write_text('''# Docker Operations TODO

- [ ] Build Docker image
- [ ] List local images
- [ ] Run container
- [ ] Check container logs
- [ ] Stop and remove container
''')
    
    return base_dir


def run_docker_command(cmd, cwd=None) -> Dict:
    """Run Docker command and return result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            timeout=30, cwd=cwd
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout if result.stdout else result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Timeout", "returncode": -1}
    except FileNotFoundError:
        return {"success": False, "output": "Docker not found", "returncode": -1}


def demo_docker_operations() -> None:
    """Demonstrate real Docker operations."""
    print("=== Docker MCP - Real Container Operations ===\n")
    
    # Create sample project
    project_dir = create_sample_docker_project()
    print(f"1. Created sample project: {project_dir}")
    
    # Show files
    print(f"\n2. Project files:")
    for f in project_dir.iterdir():
        print(f"   - {f.name} ({f.stat().st_size} bytes)")
    
    # Show Dockerfile
    dockerfile = project_dir / "Dockerfile"
    print(f"\n3. Dockerfile content:")
    print("-" * 40)
    print(dockerfile.read_text())
    print("-" * 40)
    
    # Show TODO
    todo_file = project_dir / "TODO.md"
    print(f"\n4. TODO list:")
    print(todo_file.read_text())
    
    # Try real Docker commands
    print("\n5. Running Docker commands:")
    
    # Check if Docker is available
    docker_check = run_docker_command("docker --version")
    if docker_check["success"]:
        print(f"   ✅ Docker available: {docker_check['output'].strip()}")
        
        # List images
        images = run_docker_command("docker images --format '{{.Repository}}:{{.Tag}}' | head -5")
        print(f"\n   Local images:")
        if images["output"]:
            for img in images["output"].strip().split("\n")[:5]:
                print(f"      - {img}")
        else:
            print(f"      (no images or docker not running)")
        
        # List containers
        containers = run_docker_command("docker ps --format '{{.Names}}' | head -5")
        print(f"\n   Running containers:")
        if containers["output"]:
            for c in containers["output"].strip().split("\n")[:5]:
                print(f"      - {c}")
        else:
            print(f"      (no running containers)")
    else:
        print(f"   ⚠️  Docker not available: {docker_check['output']}")
    
    # Show what docker-mcp would do
    print("\n6. Docker MCP operations to perform:")
    print(f"""
   Commands:
   
   # Build image
   algitex docker call docker-mcp docker_build_image \\
     -i '{{"context_path": "{project_dir}", "tag": "sample-app:latest"}}'
   
   # List containers
   algitex docker call docker-mcp docker_list_containers \\
     -i '{{"all": true}}'
   
   # Run container
   algitex docker call docker-mcp docker_run_container \\
     -i '{{"image": "sample-app:latest", "name": "sample-container", "ports": ["8080:8000"]}}'
        """)
    
    print(f"\n7. Files created:")
    print(f"   - {project_dir}/app.py")
    print(f"   - {project_dir}/Dockerfile")
    print(f"   - {project_dir}/TODO.md")
    print(f"\n   Keep for manual Docker experimentation.")
    print(f"   Clean up: rm -rf {project_dir}")


if __name__ == "__main__":
    demo_docker_operations()
