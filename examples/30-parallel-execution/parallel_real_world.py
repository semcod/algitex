"""Example: Real-world parallel refactoring scenario.

This example demonstrates how algitex handles a common scenario:
refactoring multiple modules in a large codebase where different
teams need to work simultaneously without conflicts.
"""
from pathlib import Path
from algitex import Project
from algitex.tools.parallel,RegionExtractor, TaskPartitioner

def setup_sample_project(base_dir: Path) -> None:
    """Create a sample project structure for demonstration."""
    # Create directory structure
    dirs = ["src/auth", "src/api", "src/models", "src/utils", "tests"]
    for d in dirs:
        (base_dir / d).mkdir(parents=True, exist_ok=True)
    
    # Create sample files with various complexity issues
    files = {
        "src/auth/middleware.py": """
class AuthMiddleware:
    def __init__(self, config):
        self.config = config
        self.tokens = {}
        self.users = {}
        self.sessions = {}
        self.rate_limits = {}
        self.audit_log = []
        
    def authenticate(self, request):
        # Complex authentication logic (CC=15)
        if not request.headers.get('Authorization'):
            return None
        token = request.headers['Authorization'].split(' ')[1]
        if token in self.tokens:
            user_id = self.tokens[token]
            if user_id in self.users:
                user = self.users[user_id]
                if user.is_active:
                    if self._check_rate_limit(user_id):
                        self._log_access(user_id, request)
                        return user
        return None
    
    def _check_rate_limit(self, user_id):
        # Rate limiting logic
        pass
""",
        "src/api/handlers.py": """
class APIHandler:
    def __init__(self, db, auth, cache):
        self.db = db
        self.auth = auth
        self.cache = cache
        self.logger = None
        self.metrics = {}
        self.middleware = []
        
    def handle_request(self, request):
        # Complex request handling (CC=12)
        try:
            user = self.auth.authenticate(request)
            if not user:
                return self._error(401, "Unauthorized")
            
            if request.method == "GET":
                return self._handle_get(request, user)
            elif request.method == "POST":
                return self._handle_post(request, user)
            else:
                return self._error(405, "Method not allowed")
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return self._error(500, "Internal server error")
""",
        "src/models/user.py": """
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.profile = None
        self.preferences = {}
        self.roles = []
        self.permissions = []
        
    def update_profile(self, data):
        # Profile update logic (CC=10)
        if 'name' in data:
            self.name = data['name']
        if 'email' in data:
            self.email = data['email']
        if 'preferences' in data:
            self.preferences.update(data['preferences'])
        self._validate()
        self._save()
        
    def _validate(self):
        # Validation logic
        pass
""",
        "src/utils/helpers.py": """
def format_response(data, status=200):
    # Utility function (CC=3)
    return {
        'status': status,
        'data': data,
        'timestamp': time.time()
    }

def calculate_pagination(page, limit, total):
    # Pagination helper (CC=4)
    offset = (page - 1) * limit
    return {
        'offset': offset,
        'limit': limit,
        'total': total,
        'pages': (total + limit - 1) // limit
    }
"""
    }
    
    for file_path, content in files.items():
        (base_dir / file_path).write_text(content)

def main() -> None:
    """Demonstrate parallel refactoring of a real-world project."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        print(f"Created sample project in: {base_dir}")
        
        # Setup sample project
        setup_sample_project(base_dir)
        
        # Initialize algitex project
        p = Project(str(base_dir))
        
        # 1. Analyze the project
        print("\n=== Analyzing project ===")
        health = p.analyze()
        print(f"Found {len(health.complexity_hotspots)} complexity hotspots")
        
        # Show top hotspots
        for i, hotspot in enumerate(health.complexity_hotspots[:3], 1):
            print(f"  {i}. {hotspot['function']} in {hotspot['file']} (CC={hotspot['complexity']})")
        
        # 2. Generate tickets from analysis
        print("\n=== Generating tickets ===")
        tickets = p._tickets.from_analysis(health)
        print(f"Generated {len(tickets)} tickets")
        
        # Prepare tickets for parallel execution
        ticket_dicts = []
        for ticket in tickets[:4]:  # Use first 4 tickets
            ticket_dicts.append({
                "id": ticket.id,
                "title": ticket.title,
                "llm_hints": {
                    "files_to_modify": [ticket.meta.get("file", "unknown")]
                }
            })
        
        # 3. Extract regions and partition
        print("\n=== Partitioning tasks ===")
        extractor = RegionExtractor(str(base_dir))
        regions = extractor.extract_all()
        print(f"Extracted {len(regions)} code regions")
        
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(ticket_dicts, max_agents=3)
        
        print(f"Partitioned {len(ticket_dicts)} tickets into {len(groups)} groups:")
        for agent_id, ticket_ids in groups.items():
            print(f"  Agent {agent_id}: {len(ticket_ids)} tickets")
            for tid in ticket_ids:
                ticket = next(t for t in ticket_dicts if t["id"] == tid)
                print(f"    - {tid}: {ticket['title'][:50]}...")
        
        # 4. Simulate parallel execution (dry run)
        print("\n=== Parallel execution plan ===")
        print("Tickets can be executed in parallel because:")
        print("  1. Different files → No conflicts")
        print("  2. Same file, different functions → Region-level locking")
        print("  3. Dependencies tracked → Semantic conflict detection")
        
        # Show region information for each ticket
        print("\nRegion analysis:")
        for ticket in ticket_dicts:
            files = ticket["llm_hints"]["files_to_modify"]
            if files:
                file_path = files[0]
                file_regions = [r for r in regions if r.file == file_path]
                if file_regions:
                    print(f"  {ticket['id']}: {len(file_regions)} regions in {file_path}")
                    for r in file_regions[:2]:  # Show first 2 regions
                        print(f"    - {r.name} ({r.type.value}) lines {r.start_line}-{r.end_line}")

if __name__ == "__main__":
    main()
