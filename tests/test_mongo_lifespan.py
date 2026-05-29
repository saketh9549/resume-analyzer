import asyncio
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def main():
    os.environ["ENVIRONMENT"] = "production"
    os.environ.pop("MONGO_URI", None)
    os.environ.pop("MONGODB_URI", None)
    
    from main import lifespan, app
    
    try:
        async with lifespan(app):
            print("Lifespan started successfully (THIS IS A BUG)")
            sys.exit(1)
    except RuntimeError as e:
        print(f"Lifespan failed successfully: {e}")
        sys.exit(0)
    except Exception as e:
        print(f"Lifespan failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
