import asyncio
import contextlib
from .loader import dispatcher

async def main() -> None:
    print("Start!")
    await dispatcher.start_polling(fast=False)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):  # подавление трейсбека с KeyboardInterrupt
       asyncio.run(main())
