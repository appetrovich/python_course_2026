"""Сравнение чистого Python в одном потоке и в пуле потоков."""
import sys
from concurrent.futures import ThreadPoolExecutor
from statistics import median
from time import perf_counter

from primes import is_prime

NUMBERS = [1_000_000_000_039] * 24


def check_sequential(numbers: list[int]) -> list[bool]:
    return [is_prime(n) for n in numbers]


def check_in_threads(numbers: list[int], workers: int) -> list[bool]:
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(is_prime, numbers))


def measure(workers: int = 4, repeats: int = 3) -> tuple[float, float]:
    timings = {"sequential": [], "threads": []}
    for repeat in range(repeats):
        modes = ("sequential", "threads") if repeat % 2 == 0 else ("threads", "sequential")
        answers = {}
        for mode in modes:
            started = perf_counter()
            if mode == "sequential":
                answers[mode] = check_sequential(NUMBERS)
            else:
                answers[mode] = check_in_threads(NUMBERS, workers)
            timings[mode].append(perf_counter() - started)
        if answers["sequential"] != answers["threads"]:
            raise AssertionError("Варианты выполнили разную работу")
    return median(timings["sequential"]), median(timings["threads"])


def main() -> None:
    workers = 4
    sequential, threads = measure(workers)
    print(f"Python: {sys.version.split()[0]}; GIL включена: {sys._is_gil_enabled()}")
    print(f"Последовательно: {sequential:.3f} с")
    print(f"{workers} потока: {threads:.3f} с")
    print(f"Ускорение: {sequential / threads:.2f}")


if __name__ == "__main__":
    main()
