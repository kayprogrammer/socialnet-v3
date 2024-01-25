import asyncio, os, sys

sys.path.append(os.path.abspath("./"))  # To single-handedly execute this script

import logging

from initials.data_script import CreateData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    create_data = CreateData()
    await create_data.initialize()


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
