import requests
import json

def hit_text_api(video_path,files_passed=[],frame_timestamps=[],url=""):
    if video_path:
        params = {'video_path':video_path}
    else:
        params=None
    #files
    files=[]

    if files_passed:
        for fle in files_passed:
            file_extension=fle.split('/')[-1].split('.')[-1]
            if 'm' not in file_extension:
                files.append(('files',(fle.split('/')[-1],open(fle,'rb'),'image/png')))#('files',(image_name,open image,type))
            #if its a video
            else:
                files = {'video_file':open(fle,'rb')}
    else:
        files=None
    if frame_timestamps:
        data = {'frame_timestamps': frame_timestamps }
    else:
        data=None
    print("api inputs: data {} , parmas {} , files={}".format(data,params,files))
    response = requests.post(url, params=params, data=data,files=files)
    
    print(response)
    # return json.loads(response.text)


url1 = "http://36f6-35-236-202-93.ngrok.io/transcript_through_video/"
print(hit_text_api(video_path="/content/temp.mp4",files_passed=["temp.mp4"],frame_timestamps=[],url=url1))
