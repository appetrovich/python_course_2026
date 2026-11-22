import asyncio
import math
import itertools

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

async def is_prime_async(n: int) -> bool:
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    root = math.isqrt(n)
    for i in range(3, root + 1, 2):
        if n % i == 0:
            return False
        # Даём другим корутинам выполниться каждые 50 000 итераций: i растёт на 2.
        if i % 100_000 == 1:
            await asyncio.sleep(0)  # нулевая задержка, но отдаём управление
    return True

# Пример интеграции в "slow"
async def slow() -> int:
    n = 5_000_111_000_222_021
    return 42 if await is_prime_async(n) else 0

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

if __name__ == '__main__':
    main()
