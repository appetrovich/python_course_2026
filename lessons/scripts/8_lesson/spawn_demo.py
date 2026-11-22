from multiprocessing import get_context


def show_square(number):
    print("Квадрат:", number * number, flush=True)


def main():
    context = get_context("spawn")
    process = context.Process(target=show_square, args=(7,))
    process.start()
    try:
        process.join(timeout=5)
        if process.is_alive():
            raise TimeoutError("Дочерний процесс не завершился")
        if process.exitcode != 0:
            raise RuntimeError(f"Код завершения: {process.exitcode}")
    finally:
        if process.is_alive():
            process.terminate()
        process.join()
        process.close()


if __name__ == "__main__":
    main()
