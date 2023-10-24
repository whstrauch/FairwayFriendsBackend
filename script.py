from datetime import datetime
import time



def main():
    
    import requests

    # Warm up, so you don't measure flask internal memory usage
    for _ in range(10):
        requests.get('http://127.0.0.1:5000/')

    # Memory usage before API calls
    resp = requests.get('http://127.0.0.1:5000/memory')
    print(f'Memory before API call {int(resp.json().get("memory"))}')


    # Start some API Calls
    for _ in range(50):
        requests.get('http://127.0.0.1:5000/')

    # Memory usage after
    resp = requests.get('http://127.0.0.1:5000/memory')
    print(f'Memory after API call: {int(resp.json().get("memory"))}')




if __name__ == "__main__":
    main()