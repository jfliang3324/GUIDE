from bs4 import BeautifulSoup
import re
import time
import os
download_cmd='''
curl '{photo_url}' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'origin: https://www.kuaishou.com' \
  -H 'pragma: no-cache' \
  -H 'range: bytes=0-' \
  -H 'referer: https://www.kuaishou.com/short-video/{id}' \
  -H 'sec-ch-ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: video' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: cross-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36' -o {video_path}
'''

def get_photo_url(file_path):
    with open(file_path) as obj:
        data = BeautifulSoup(obj, "html.parser")
        scirpts=data.find_all("script")
        real_script=None
        for scirpt in scirpts:
            if len(scirpt.getText())>=200:
                real_script=scirpt.getText()
        if real_script==None:
            return None
        real_script=real_script.replace("\\u002F","/")
        real_script=real_script.replace('\\"','"')   
        # print(real_script)
        f=open("./self.json","w")
        f.write(real_script)
        f.close()
        match = re.search(r'"photoUrl":"(https?://[^"]+)"', real_script)
        if match:
            photo_url = match.group(1)
            print(photo_url)
            return photo_url
        else:
            return None

def get_v2_url(url,v2_url_dir):
    url=url.strip()
    id=url.split("/")[-1]
    print(id)
    out_file=v2_url_dir+"/"+id+".txt"

    f=open(out_file,"w")
    f.close()
    curl_cmd = "curl "+url+" > "+ out_file
    print(f"CURL_CMD\n:{curl_cmd}\nCURL_CMD")
    if not os.path.exists(out_file):
        f=open(out_file,"w")
        f.close()
    
    with open(out_file,"r") as f:
        text=f.read()
    retry_count=0 
    while len(text)<=200 or ("photoUrl" in text and "v2.kwaicdn" not in text) or  ("photoUrl" in text and "v1.kwaicdn" not in text) :  
        retry_count+=1
        print(f"RETRY Time:{retry_count}")
        time.sleep(2)
        os.system(curl_cmd)
        print(f"CURL_CMD\n:{curl_cmd}\nCURL_CMD")
        with open(out_file,"r") as f:
            text=f.read()
        if len(text)>200 and "photoUrl" not in text:
            break
        if retry_count==10:#retry 10 times
            print(f"RETRY Time>={retry_count}. Break Now!")
            break
    return out_file
def get_video(photo_url,video_path,id):
    print(photo_url)
    download_photo_cmd=download_cmd.format(photo_url=photo_url,id=id,video_path=video_path)
    os.system(download_photo_cmd)

# path
v2_url_dir=""
photoUrl_dir=""
shortvideo_url_path=""
video_dir=""

from tqdm import tqdm
with open(shortvideo_url_path,"r") as f:
    data=f.readlines()
    count=0
    for shortvideo_url in tqdm(data):

        id=shortvideo_url.strip().split("/")[-1]

        v2_out_file=get_v2_url(shortvideo_url,v2_url_dir)

        photo_url=get_photo_url(v2_out_file)
        photo_url_out_path=photoUrl_dir+"/"+v2_out_file.split("/")[-1]
        if photo_url==None:
            continue
        with open(photo_url_out_path,"w",encoding="utf-8") as f:
            f.write(photo_url)

        video_path=video_dir+"/"+id+".mp4"
        get_video(photo_url=photo_url,video_path=video_path,id=id)

        