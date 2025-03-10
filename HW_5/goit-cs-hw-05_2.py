import requests
import re
import matplotlib.pyplot as plt
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

def fetch_text_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text) #Delete all not alphabetic symbols
    return text

def map_function(text):
    words = text.split()
    return [(word, 1) for word in words]

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(shuffled_values):
    reduced = {}
    for key, values in shuffled_values:
        reduced[key] = sum(values)
    return reduced

def map_reduce(text):
    with ThreadPoolExecutor() as executor:
        mapped_values = executor.submit(map_function, text).result()
        shuffled_values = executor.submit(shuffle_function, mapped_values).result()
        reduced_values = executor.submit(reduce_function, shuffled_values).result()
    return reduced_values

def visualize_top_words(word_counts, top_n=10):
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_words)

    plt.figure(figsize=(10, 6))
    plt.barh(words[::-1], counts[::-1], color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top_n} Most Frequent Words')
    plt.show()

if __name__ == '__main__':
    url = input("Input the URL of the text: ")
    text = fetch_text_from_url(url)
    text = preprocess_text(text)
    word_counts = map_reduce(text)
    visualize_top_words(word_counts)