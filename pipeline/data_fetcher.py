17s

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/NBA-Predictions/NBA-Predictions/pipeline/data_fetcher.py", line 18, in fetch_season_games
    response = requests.get(url, timeout=15)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/api.py", line 87, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/api.py", line 71, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 651, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 784, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 742, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='data.nba.com', port=443): Read timed out. (read timeout=15)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/NBA-Predictions/NBA-Predictions/main.py", line 62, in <module>
    main()
  File "/home/runner/work/NBA-Predictions/NBA-Predictions/main.py", line 11, in main
    raw_data = fetch_season_games('2025-26')
  File "/home/runner/work/NBA-Predictions/NBA-Predictions/pipeline/data_fetcher.py", line 61, in fetch_season_games
    raise ConnectionError(f"❌ Failed to reach alternate NBA CDN endpoint: {e}")
ConnectionError: ❌ Failed to reach alternate NBA CDN endpoint: HTTPSConnectionPool(host='data.nba.com', port=443): Read timed out. (read timeout=15)
Error: Process completed with exit code 1.
