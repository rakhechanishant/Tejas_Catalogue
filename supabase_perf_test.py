import os
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from supabase import create_client

def test_query(supabase_client, offset=0, batch_size=1000):
    start_time = time.time()
    try:
        response = supabase_client.table('products').select('*').range(offset, offset + batch_size - 1).execute()
        latency = time.time() - start_time
        success = response.data is not None
        error_msg = "" if success else "No data returned"
        record_count = len(response.data) if success else 0
        return success, latency, record_count, error_msg
    except Exception as e:
        latency = time.time() - start_time
        return False, latency, 0, str(e)

def run_benchmark(concurrency, total_requests):
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_KEY not found in env!")
        return

    print(f"Initializing Supabase client targeting: {url}")
    supabase_client = create_client(url, key)
    
    print("\n" + "="*50)
    print(f"RUNNING LATENCY & CONCURRENCY BENCHMARK")
    print(f"Total Requests: {total_requests}")
    print(f"Concurrency level (threads): {concurrency}")
    print("="*50)
    
    latencies = []
    successes = 0
    failures = 0
    total_records_fetched = 0
    errors = {}

    start_bench = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(test_query, supabase_client): i for i in range(total_requests)}
        
        for future in as_completed(futures):
            success, latency, record_count, err = future.result()
            latencies.append(latency)
            if success:
                successes += 1
                total_records_fetched += record_count
            else:
                failures += 1
                errors[err] = errors.get(err, 0) + 1
            
            # Print a progress indicator
            progress = len(latencies)
            if progress % max(1, total_requests // 10) == 0 or progress == total_requests:
                print(f" Completed {progress}/{total_requests} requests...")

    total_time = time.time() - start_bench
    
    # Calculate stats
    latencies.sort()
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = latencies[0] if latencies else 0
    max_latency = latencies[-1] if latencies else 0
    p50_latency = latencies[int(len(latencies) * 0.5)] if latencies else 0
    p95_latency = latencies[int(len(latencies) * 0.95)] if latencies else 0
    p99_latency = latencies[int(len(latencies) * 0.99)] if latencies else 0
    qps = total_requests / total_time if total_time > 0 else 0

    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    print(f"Total Time Taken:     {total_time:.2f} seconds")
    print(f"Queries Per Second:   {qps:.2f} QPS")
    print(f"Success Rate:         {(successes/total_requests)*100:.1f}% ({successes} success, {failures} fail)")
    print(f"Total Records Loaded: {total_records_fetched}")
    print(f"Min Latency:          {min_latency*1000:.1f} ms")
    print(f"Average Latency:      {avg_latency*1000:.1f} ms")
    print(f"Median (p50) Latency: {p50_latency*1000:.1f} ms")
    print(f"p95 Latency:          {p95_latency*1000:.1f} ms")
    print(f"p99 Latency:          {p99_latency*1000:.1f} ms")
    print("="*50)
    
    if errors:
        print("\nErrors encountered:")
        for err, count in errors.items():
            print(f" - {err}: {count} occurrences")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supabase DB Latency and Concurrency Benchmark")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent query threads")
    parser.add_argument("--requests", type=int, default=50, help="Total number of queries to make")
    args = parser.parse_args()
    
    run_benchmark(args.concurrency, args.requests)
