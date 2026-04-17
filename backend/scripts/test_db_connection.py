import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import ping_database


async def main() -> None:
    connected = await ping_database()
    if connected:
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")


if __name__ == "__main__":
    asyncio.run(main())
