import os
import sys

# Test 1: Development with no URI -> should not raise Error
os.environ["ENVIRONMENT"] = "development"
os.environ.pop("MONGO_URI", None)
os.environ.pop("MONGODB_URI", None)

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from config.settings import Settings
s1 = Settings()
assert s1.get_mongo_uri == "mongodb://localhost:27017"

# Test 2: Production with no URI -> should return None
os.environ["ENVIRONMENT"] = "production"
s2 = Settings()
assert s2.get_mongo_uri is None

# Test 3: Production with MONGODB_URI -> should return URI
os.environ["MONGODB_URI"] = "mongodb+srv://atlas:test"
s3 = Settings()
assert s3.get_mongo_uri == "mongodb+srv://atlas:test"

print("All config tests passed.")
