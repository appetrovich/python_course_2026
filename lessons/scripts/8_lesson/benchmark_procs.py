"""Сравнение одной и той же проверки чисел: последовательно и через spawn."""
from collections import Counter
from statistics import median
from time import perf_counter

from primes import is_prime
from procs import run_checks


def compare(numbers, n_workers=2, repeats=3):
    numbers = list(numbers)
    if repeats < 1:
        raise ValueError('Нужен хотя бы один замер')
    timings = {'sequential': [], 'processes': []}
    for repeat in range(repeats):
        # Чередуем порядок, чтобы один вариант не запускался всегда первым.
        modes = ('sequential', 'processes') if repeat % 2 == 0 else ('processes', 'sequential')
        answers = {}
        for mode in modes:
            started = perf_counter()
            if mode == 'sequential':
                values = [(n, is_prime(n)) for n in numbers]
            else:
                results = run_checks(numbers, n_workers=n_workers, timeout=30)
                if any(result.error is not None for result in results):
                    raise RuntimeError('Замер с ошибкой задания нельзя сравнивать с успешным')
                values = [(result.n, result.prime) for result in results]
            timings[mode].append(perf_counter() - started)
            answers[mode] = Counter(values)
        if answers['sequential'] != answers['processes']:
            raise AssertionError('Варианты выполнили разную работу')
    return {mode: median(values) for mode, values in timings.items()}


def main():
    for label, numbers in [('короткие задания', [104_729] * 24),
                           ('длинные задания', [1_000_000_000_039] * 24)]:
        timing = compare(numbers)
        speedup = timing['sequential'] / timing['processes']
        print(f'{label}: последовательно {timing["sequential"]:.6f} с; '
              f'2 процесса {timing["processes"]:.6f} с; ускорение {speedup:.3f}')


if __name__ == '__main__':
    main()
