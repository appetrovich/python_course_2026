# Example 19-1. spinner_thread.py: функции spin и slow
# python scripts/8_lesson/spinner_thread.py        – slow() ждёт 3 секунды
# python scripts/8_lesson/spinner_thread.py prime  – slow() занят вычислением
import itertools
import sys
import time

from threading import Thread, Event

from primes import is_prime

CPU_BOUND = sys.argv[1:] == ['prime']

def spin(msg: str, done: Event) -> None:
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(0.1):
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

def slow() -> int:
    if CPU_BOUND:
        is_prime(5_000_111_000_222_021)
    else:
        time.sleep(3)
    return 42


# 2. spinner_thread.py: supervisor и main
def supervisor() -> int:
    done = Event()                                   # объект-событие для остановки спиннера
    spinner = Thread(target=spin, args=('thinking!', done))
    print(f'spinner object: {spinner}')              
    spinner.start()                                  # запускаем поток со спиннером
    try:
        return slow()
    finally:
        done.set()                                   # сигнализируем спиннеру завершиться
        spinner.join()                               # дожидаемся, пока поток завершится

def main() -> None:
    result = supervisor()
    print(f'Answer: {result}')

if __name__ == '__main__':
    main()
