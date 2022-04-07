import requests, zipfile, time, io, os


def download_zip(url, folder):
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(folder)


with open('sbg_download_links.txt') as f:
    lines = f.readlines()
    counter = 0
    start = time.time()

    for url in lines:
        location_id = url[-18:-13]
        folder_name = f"DGM/{location_id}"

        url = url[:-1]

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        download_zip(url, folder_name)
        counter += 1

        print(f"Downloaded {counter}/199 files in {round(time.time()-start,2)}s")
