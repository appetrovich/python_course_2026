"""
procs.py: распределение CPU-интенсивных проверок простоты по процессам.
Использует очереди для задач и результатов, сообщает об ошибках каждого задания.
"""
from __future__ import annotations

from math import isfinite
from time import perf_counter
from multiprocessing import get_context, cpu_count
from queue import Empty
from typing import NamedTuple

from primes import is_prime, NUMBERS


class Result(NamedTuple):
    n: int
    prime: bool | None
    elapsed: float
    error: str | None = None


def worker(task_q, result_q) -> None:
    """
    Воркер: берёт числа из task_q, проверяет, кладёт результат в result_q.
    Останавливается по получении None.
    """
    while True:
        n = task_q.get()
        if n is None:
            # Сентинел для остановки
            break
        t0 = perf_counter()
        try:
            prime = is_prime(n)
        except Exception as error:
            result = Result(n, None, perf_counter() - t0,
                            f'{type(error).__name__}: {error}')
        else:
            result = Result(n, prime, perf_counter() - t0)
        result_q.put(result)


def collect_results(procs, result_q, expected: int, deadline: float) -> list[Result]:
    """Ждём сообщения до общего срока, проверяя состояние процессов при паузах."""
    received = []
    while len(received) < expected:
        remaining = deadline - perf_counter()
        if remaining <= 0:
            raise TimeoutError('Истёк срок ожидания результатов')
        # После выхода всех процессов новые сообщения уже не появятся.
        all_exited = all(p.exitcode is not None for p in procs)
        try:
            result = result_q.get(timeout=min(0.1, remaining))
        except Empty:
            failed = [p.exitcode for p in procs if p.exitcode not in (None, 0)]
            if failed:
                raise RuntimeError(f'Аварийное завершение воркера: {failed}')
            if all_exited:
                raise RuntimeError('Воркеры завершились, но получены не все результаты')
        else:
            received.append(result)
    return received


def run_checks(numbers, n_workers: int = 2, timeout: float = 120) -> list[Result]:
    """Запускаем пул через spawn; timeout задаёт общий срок ожидания работы."""
    if n_workers < 1 or not isfinite(timeout) or timeout <= 0:
        raise ValueError('Нужны положительные число воркеров и конечный timeout')
    numbers = list(numbers)
    if any(n is None for n in numbers):
        raise ValueError('None занят маркером остановки')
    if not numbers:
        return []
    deadline = perf_counter() + timeout
    context = get_context('spawn')
    task_q = context.Queue()
    result_q = context.Queue()
    procs = []
    try:
        # Сначала запускаем воркеров, затем кладём задания в очередь.
        for _ in range(min(n_workers, len(numbers))):
            p = context.Process(target=worker, args=(task_q, result_q))
            p.start()
            procs.append(p)
        for n in numbers:
            task_q.put(n)
        for _ in procs:
            task_q.put(None)

        received = collect_results(procs, result_q, len(numbers), deadline)
        for p in procs:
            p.join(timeout=max(0, deadline - perf_counter()))
            if p.is_alive():
                raise TimeoutError('Воркер не завершился в отведённое время')
            if p.exitcode != 0:
                raise RuntimeError(f'Код завершения воркера: {p.exitcode}')
        return received
    finally:
        # При сбое останавливаем оставшиеся процессы и больше не используем очереди.
        for p in procs:
            if p.is_alive():
                p.terminate()
        for p in procs:
            p.join()
            p.close()
        for q in (task_q, result_q):
            q.cancel_join_thread()
            q.close()


def main() -> None:
    n_workers = min(cpu_count(), len(NUMBERS))
    print(f'Checking {len(NUMBERS)} numbers with {n_workers} processes:')
    started = perf_counter()
    results = run_checks(NUMBERS, n_workers)
    elapsed = perf_counter() - started
    for res in results:
        if res.error is not None:
            print(f'{str(res.n):>16} ERROR {res.error}')
        else:
            label = 'P' if res.prime else ' '
            print(f'{res.n:16} {label} {res.elapsed:9.6f}s')
    failed = sum(res.error is not None for res in results)
    print(f'{len(results)} checks, {failed} errors, total time: {elapsed:.2f}s')


if __name__ == '__main__':
    main()
