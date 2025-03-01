import os
import time
import threading
from queue import Queue
import multiprocessing


# Абсолютний шлях до директорії з файлами
DIRECTORY = r"C:\Projects\MasterSc\computer_systems\hw\hw_4"

# Ключові слова для пошуку
KEYWORDS = ["error", "success", "warning", "failed", "completed"]


# Функція для пошуку ключових слів у файлі
def search_keywords_in_file(file_path, keywords):
    found_keywords = {word: [] for word in keywords}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().lower()
            for word in keywords:
                if word in content:
                    found_keywords[word].append(file_path)
    except Exception as e:
        print(f"Помилка при обробці {file_path}: {e}")
    return found_keywords


# Багатопотокова функція пошуку
def threaded_search(file_list, keywords, result_queue):
    for file in file_list:
        result = search_keywords_in_file(file, keywords)
        result_queue.put(result)


# Основна функція для запуску багатопотокового пошуку
def run_threading(files):
    result_queue = Queue()
    threads = []
    num_threads = min(4, len(files))  # Не більше 4 потоків
    chunk_size = len(files) // num_threads

    for i in range(num_threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != num_threads - 1 else len(files)
        thread = threading.Thread(
            target=threaded_search, args=(files[start:end], KEYWORDS, result_queue)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Збір фінального результату
    final_result = {word: [] for word in KEYWORDS}
    while not result_queue.empty():
        result = result_queue.get()
        for word, paths in result.items():
            final_result[word].extend(paths)

    return final_result



# Багатопроцесорна реалізація
def process_search(files, keywords, queue):
    result = {word: [] for word in keywords}
    for file in files:
        file_result = search_keywords_in_file(file, keywords)
        for word, paths in file_result.items():
            result[word].extend(paths)
    queue.put(result)


def run_multiprocessing(files):
    queue = multiprocessing.Queue()
    processes = []
    num_processes = min(4, len(files))  # Не більше 4 процесів
    chunk_size = (len(files) + num_processes - 1) // num_processes  # Ділимо файли рівномірно

    for i in range(num_processes):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(files))  # Виправлено межі діапазону
        process = multiprocessing.Process(target=process_search, args=(files[start:end], KEYWORDS, queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    final_result = {word: [] for word in KEYWORDS}
    while not queue.empty():
        result = queue.get()
        for word, paths in result.items():
            final_result[word].extend(paths)

    return final_result



if __name__ == "__main__":
    # Перевірка, чи існує директорія
    if not os.path.exists(DIRECTORY):
        print(f"Помилка: Директорія {DIRECTORY} не існує!")
    else:
        # Отримання списку файлів у папці
        all_files = [
            os.path.join(DIRECTORY, f)
            for f in os.listdir(DIRECTORY)
            if f.endswith(".txt")
        ]

        # Запуск багатопотокової обробки
        print("Запуск багатопотокової версії...")
        start_time = time.time()
        threading_result = run_threading(all_files)
        print(f"Час виконання threading: {time.time() - start_time:.4f} сек")

        # Виведення результатів
        for word, files in threading_result.items():
            print(f"{word}: {files}")

# Перевірка існування директорії
    if not os.path.exists(DIRECTORY):
        print(f"Помилка: Директорія '{DIRECTORY}' не існує!")
    else:
        # Отримуємо список файлів
        all_files = [os.path.join(DIRECTORY, f) for f in os.listdir(DIRECTORY) if f.endswith(".txt")]

        if not all_files:
            print("Помилка: У директорії немає .txt файлів!")
        else:
            print("\nЗапуск багатопроцесорної версії...")
            start_time = time.time()
            multiprocessing_result = run_multiprocessing(all_files)
            print(f"Час виконання multiprocessing: {time.time() - start_time:.4f} сек")

            # Виведення результатів
            for word, files in multiprocessing_result.items():
                print(f"{word}: {files}")