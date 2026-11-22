# 3. spinner_proc.py – изменившиеся части (остальное как в spinner_thread.py)
# python scripts/8_lesson/spinner_proc.py        – slow() ждёт 3 секунды
# python scripts/8_lesson/spinner_proc.py prime  – slow() занят вычислением
import itertools
import sys
import time
from multiprocessing import Process, Event
from multiprocessing import synchronize  # для корректной аннотации типов Event

from primes import is_prime

CPU_BOUND = sys.argv[1:] == ['prime']

def spin(msg: str, done: synchronize.Event) -> None:
    # остальной код идентичен версии на потоках:
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

def supervisor() -> int:
    done = Event()  # возвращает synchronize.Event
    spinner = Process(target=spin, args=('thinking!', done))
    print(f'spinner object: {spinner}')  
    spinner.start()
    try:
        return slow()
    finally:
        done.set()
        spinner.join()

# main() – без изменений:
def main() -> None:
    print(f'Answer: {supervisor()}')

if __name__ == '__main__':
    main()
