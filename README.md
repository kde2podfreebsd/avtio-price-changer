[@avito_price_changer_bot](https://t.me/avito_price_changer_bot)

```
make docker_build
docker build -t avito_price_changer .
[+] Building 0.7s (11/11) FINISHED                                                                                       docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                     0.0s
 => => transferring dockerfile: 451B                                                                                                     0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                      0.5s
 => [internal] load .dockerignore                                                                                                        0.0s
 => => transferring context: 2B                                                                                                          0.0s
 => [1/6] FROM docker.io/library/python:3.11-slim@sha256:80bcf8d243a0d763a7759d6b99e5bf89af1869135546698be4bf7ff6c3f98a59                0.0s
 => [internal] load build context                                                                                                        0.0s
 => => transferring context: 71.00kB                                                                                                     0.0s
 => CACHED [2/6] WORKDIR /app                                                                                                            0.0s
 => CACHED [3/6] RUN apt-get update     && apt-get install -y --no-install-recommends gcc libpq-dev     && rm -rf /var/lib/apt/lists/*   0.0s
 => CACHED [4/6] COPY requirements.txt .                                                                                                 0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements.txt                                                                      0.0s
 => [6/6] COPY . .                                                                                                                       0.1s
 => exporting to image                                                                                                                   0.0s
 => => exporting layers                                                                                                                  0.0s
 => => writing image sha256:dd664490b3a49874ac237465e6a099d0b0f51e32af4ff494eda0eee4ddd5f959                                             0.0s
 => => naming to docker.io/library/avito_price_changer   
```

```
make docker_run
docker run -it -p 8000:8000 avito_price_changer
Update prices
```
