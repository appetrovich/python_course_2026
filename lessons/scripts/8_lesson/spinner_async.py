# 1. spinner_async.py: main и supervisor
# python scripts/8_lesson/spinner_async.py        – slow() ждёт 3 секунды
# python scripts/8_lesson/spinner_async.py prime  – slow() занят вычислением
import asyncio
import itertools
import sys

from primes import is_prime

CPU_BOUND = sys.argv[1:] == ['prime']

async def supervisor() -> int:
    spinner = asyncio.create_task(spin('thinking!'))
    print(f'spinner task: done={spinner.done()}')
    try:
        return await slow()            # ожидаем завершения "медленной" корутины
    finally:
        spinner.cancel()               # запрашиваем отмену спиннера
        try:
            await spinner              # ждём, пока spin очистит строку и завершится
        except asyncio.CancelledError:
            pass                       # отмену запросил сам supervisor

def main() -> None:
    result = asyncio.run(supervisor())  # запускаем event loop и корутину supervisor
    print(f'Answer: {result}')


# 2. spinner_async.py: корутины spin и slow
async def spin(msg: str) -> None:
    status = ''
    try:
        for char in itertools.cycle(r'\|/-'):
            status = f'\r{char} {msg}'
            print(status, flush=True, end='')
            # неблокирующая пауза: даём event loop переключиться на другие корутины
            await asyncio.sleep(0.1)
    finally:
        # выполняется и при отмене задачи: очищаем строку спиннера
        blanks = ' ' * len(status)
        print(f'\r{blanks}\r', end='')

async def slow() -> int:
    if CPU_BOUND:
        # вычисление без await: цикл событий не получает управления
        is_prime(5_000_111_000_222_021)
    else:
        # имитация длительной операции без блокировки event loop
        await asyncio.sleep(3)
    return 42

if __name__ == '__main__':
    main()
