# Демонстрация блокировки цикла событий через time.sleep(3).
import asyncio
import itertools
import time

async def spin(msg: str) -> None:
    status = ''
    try:
        for char in itertools.cycle(r'\|/-'):
            status = f'\r{char} {msg}'
            print(status, flush=True, end='')
            await asyncio.sleep(0.1)
    finally:
        blanks = ' ' * len(status)
        print(f'\r{blanks}\r', end='')

async def slow() -> int:
    # Неправильно: блокирует весь event loop на 3 секунды
    time.sleep(3)
    return 42

async def supervisor() -> int:
    spinner = asyncio.create_task(spin('thinking!'))
    print(f'spinner task: done={spinner.done()}')
    try:
        return await slow()
    finally:
        spinner.cancel()
        try:
            await spinner
        except asyncio.CancelledError:
            pass

def main() -> None:
    result = asyncio.run(supervisor())
    print(f'Answer: {result}')

if __name__ == '__main__':
    main()
