import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the global imports for routers (lines 21-29)
content = re.sub(r'from routes\..+ import router as .+\n', '', content)

# 2. Add the structured startup logging after imports
startup_log = """
logger_startup = logging.getLogger("startup")
logger_startup.info("STARTUP STEP 1: Loading settings...")

startup_status = {
    "settings": "success",
    "env_vars": {},
    "mongo": "pending",
    "routes": {}
}

logger_startup.info("STARTUP STEP 2: Checking Env Variables...")
for var in ["MONGO_URI", "JWT_SECRET", "GEMINI_API_KEY", "REDIS_URL"]:
    val = os.getenv(var)
    status = "FOUND" if val else "MISSING"
    startup_status["env_vars"][var] = status
    logger_startup.info(f"{var}: {status}")

logger_startup.info("STARTUP STEP 3: Loading Mongo...")
logger_startup.info("STARTUP STEP 4: Loading Gemini...")
logger_startup.info("STARTUP STEP 5: Loading Redis...")
logger_startup.info("STARTUP STEP 6: Loading routes...")
"""

# Insert startup_log after "from config.settings import settings"
content = content.replace('from config.settings import settings\n', 'from config.settings import settings\n' + startup_log)

# 3. Replace the routes block
routes_block_regex = r'# ── ROUTES ──.+?(?=# ── SYSTEM ENDPOINTS ──)'
new_routes_block = """# ── ROUTES ─────────────────────────────────────────────────────────────────

def load_routers(app):
    def safe_include(module_name, router_name, prefix, tags):
        try:
            import importlib
            module = importlib.import_module(f"routes.{module_name}")
            router = getattr(module, router_name)
            app.include_router(router, prefix=prefix, tags=tags)
            startup_status["routes"][module_name] = "success"
        except Exception as e:
            logger_startup.error(f"Failed to load route {module_name}: {e}")
            startup_status["routes"][module_name] = "failed"

    safe_include("auth", "router", "/auth", ["Authentication"])
    safe_include("resume", "router", "/resume", ["Resume"])
    safe_include("resume", "router", "/resumes", ["Resume"])
    safe_include("ai", "router", "/ai", ["AI Feedback"])
    safe_include("jobs", "router", "/jobs", ["Job Matching"])
    safe_include("rewriter", "router", "/rewriter", ["AI Rewriter"])
    safe_include("interviews", "router", "/interviews", ["AI Interview Prep"])
    safe_include("live_jobs", "router", "/live_jobs", ["Live Job API"])
    safe_include("recruiter", "router", "/recruiter", ["Recruiter Console"])
    safe_include("career", "router", "/career", ["Career Intelligence"])
    
    logger_startup.info("Application started...")

load_routers(app)

"""
content = re.sub(routes_block_regex, new_routes_block, content, flags=re.DOTALL)

# 4. Add the /health/startup endpoint
health_startup = """
@app.get("/health/startup", tags=["System"])
async def health_check_startup():
    return startup_status
"""
content = content + health_startup

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("main.py rewritten successfully!")
