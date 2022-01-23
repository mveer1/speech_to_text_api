#import libraries
from  metadata_extraction.keyword_search_utils.keywords_libraries import *  


#retry function for transcript status and response 

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2 ):
    """Retry calling the decorated function using an exponential backoff.

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry



def crop_video( input_video_path , stime = '' , etime = '' , out_video_name = "output.mp4" ):  
    """
    args: 
        input_video_path: string, path to the input video
        out_video_name : string, name/path of the output video
        stime and etime: string, are the times "relative" to the start of the video in seconds and in format: 00:00:00
    
    function:
        crops the video and saves it to the given out_video_name destination
        # does not return anything just saves the videos
    
    """

    #if both start time and end time are passed then crop the video with start and end option 
    if etime and stime:
        ffmpeg_cmd = f"ffmpeg -y -ss {stime} -i {input_video_path} -to {etime} -c copy {out_video_name}"

    #if only end time is passed crop till the entire video end with only start option
    elif etime and not stime:
        ffmpeg_cmd = f"ffmpeg -y -i {input_video_path} -to {etime} -c copy {out_video_name}"

    elif stime and not etime:
        #cropping the video using ffmpeg, from stime to etime
        ffmpeg_cmd = f"ffmpeg -y -ss {stime} -i {input_video_path}  -c copy {out_video_name}"

    os.system(ffmpeg_cmd)

# crop_video(input_video_path="ANTEN1_20210803_040128_00278.ts", stime="00:00:07", etime="00:00:10", out_video_name="output.mp4")


def add_seconds(input_time, n = 10):
    """
    args:
        n: is the number of seconds to add
        input time: string of format: 00:00:00, input time

    return: 
        new time (seconds added), in the same format
    """


    #splitting the time into hours, minutes and seconds
    hours = input_time.split(":")[0]
    minutes = input_time.split(":")[1]
    seconds = input_time.split(":")[2]

    new_seconds = int(seconds) + n
    new_time = hours + ":" + minutes + ":" + str(new_seconds)
    # adding 10 seconds to the time
    if new_seconds>=60:
        new_minutes = int(input_time.split(":")[-2]) + int(new_seconds/60)
        new_seconds = new_seconds % 60
        if len(str(new_minutes))==1:
            new_minutes = "0" + str(new_minutes)
        if len(str(new_seconds))==1:
            new_seconds = "0" + str(new_seconds)
            
        new_time = f"{hours}:{new_minutes}:{new_seconds}"        
        if int(new_minutes)>=60:
            new_hours = int(hours) + int(new_minutes/60)
            new_minutes = new_minutes % 60
            if len(str(new_hours))==1:
                new_hours = "0" + str(new_hours)
            if len(str(new_minutes))==1:
                new_minutes = "0" + str(new_minutes)
            new_time = str(new_hours) + ":" + str(new_minutes) + ":" + str(new_seconds)

    #return new time
    return new_time

def difference_in_seconds(time1, time2):
    """
    args:
        time1, time2: format- 00:00:00
    return:
        will return the absolute difference in seconds between two times
    """
    #splitting the time into hours, minutes and seconds
    hours1 = time1.split(":")[0]
    minutes1 = time1.split(":")[1]
    seconds1 = time1.split(":")[2]

    hours2 = time2.split(":")[0]
    minutes2 = time2.split(":")[1]
    seconds2 = time2.split(":")[2]

    seconds1 = int(hours1)*3600 + int(minutes1)*60 + int(seconds1)
    seconds2 = int(hours2)*3600 + int(minutes2)*60 + int(seconds2)

    #difference in seconds
    return abs(seconds2 - seconds1)

def get_output_videos(start_time, end_time, input_video_list):
    """
    function will crop the videos in input_video_list to the time range specified by start_time and end_time
    args:
        start_time: [string] start time format: 00:00:00 
        end_time: [string] end time in format: 00:01:00
        input_video_list: python list, of strings with paths of the videos available
    
    return:
        the list of cropped videos

    creates a directory called "cropped_videos" in the current directory
    """

    output_video_list = []
    #output videos dir
    output_videos_dir = "output_videos"

    try:
        os.mkdir( output_videos_dir )
    except:
        shutil.rmtree( output_videos_dir )
        os.mkdir( output_videos_dir )

    for index, video_name in enumerate( input_video_list ):
        video_start = video_name.split("_")[-2]
        video_start = video_start[0:2] + ":" + video_start[2:4] + ":" + video_start[4:6]
        video_end = add_seconds( input_time = video_start , n = 10 )
        out_video_name = f"output_videos/output_{index}.mp4"
        
        #check if the video is in between start and end time 
        if start_time > video_end or end_time < video_start :
            #skip video
            continue

        #start time is in this video.
        if video_start <= start_time <= video_end:
            print("start time lies inside this video:", video_name)
            stime = difference_in_seconds( time1 = start_time , time2 = video_start )
            
            #if end time is also in this video:
            if video_start <= end_time <= video_end:
                etime = difference_in_seconds(time1=end_time, time2=video_start)

                output_video_path = os.path.join( output_videos_dir , "output_final.mp4")

                # crop video as output_final.mp4
                crop_video( input_video_path = video_name , stime = str(stime), etime = str(etime) , out_video_name = output_video_path )
                output_video_list.append( output_video_path )
                break

            #if end is in someother video, we have to make a list 
            else:
                out_video_name = f"output_videos/output_{index}.mp4"
                crop_video( input_video_path = video_name , stime = str(stime), etime = '' , out_video_name = out_video_name )
                output_video_list.append( out_video_name )
                
            #continue

        #if end time is in the video 
        elif video_start <= end_time <= video_end:
            #end time is in this video.
            print("end time lies inside this video:", video_name)
            etime = difference_in_seconds(time1=end_time, time2=video_start)
            crop_video( input_video_path = video_name, stime = '' , etime = str(etime) , out_video_name = out_video_name )
            output_video_list.append( out_video_name )

        #if start and end time are not in the video 
        else:
            #crop_video( input_video_path = video_name , stime = "" , etime = "00:00:10", out_video_name = out_video_name )
            output_video_list.append( input_video_list[index] )
    
    return output_video_list


def words_to_add(words_list, config):
    """
    args:
        words_list: python list of words to add to config
        config: python dictionary object
    
    function:
        this function will add the words in words_list to the config dictionary
    
    return:
        the updated config dictionary
    """

    vocabs = []
    for word in words_list:
        to_add = {"content": word}
        vocabs.append(to_add)
    
    config['transcription_config']["additional_vocab"].extend(vocabs)

    return config 


def submit_audio_to_API( audio_file_path , api_key , api_ip , config  ):
    files = {'data_file': open(audio_file_path, 'rb') }
    headers = {"Authorization": f"Bearer {api_key}" }
    response = requests.post( url = api_ip , files = files , data = {'config':str(config).replace("'",'"')} , headers = headers )
    print(f"response from API is: {response}")
    response_dict = json.loads(response.content.decode('utf-8'))
    print(f"response content: {response_dict } ")#id: {response.id}")
    return response_dict['id']

def concat_transcript_text( transcript_results , min_confidence = 0.3 ):
    #sample: "results": [{"alternatives": [{"confidence": 1.0,"content": "Name","language": "en","speaker": "UU"}],"end_time": 0.33,"start_time": 0.09,"type": "word"},{"alternatives": [{"confidence": 1.0,"content": "it","language": "en","speaker": "UU"}],"end_time": 0.42,"start_time": 0.33,"type": "word"},..]
    #returns concatenated text and number of speakers 
    speakers_set = set()
    concatenated_text = ""
    for wrd in transcript_results:
        if wrd.get('alternatives',[]):
            confidence = wrd['alternatives'][0].get('confidence',0)
            if confidence > min_confidence :
                word = wrd['alternatives'][0].get('content','')
                concatenated_text = concatenated_text + " " + word
                speakers_set.add(wrd['alternatives'][0].get('speaker','UU'))
    
    return concatenated_text , len(speakers_set)


@retry( Exception , tries=4 , delay=15, backoff=2 )
def get_id_transcript( id , api_key , api_url = SPEECH_TO_TEXT_API_IP ):
    #try:
    transcript_text = ""
    number_of_speakers = 1
    headers = {"Authorization": f"Bearer {api_key}" }
    api_url = api_url + str(id) + "/transcript"
    #print(f"api_url: {api_url}\t headers: {headers}")
    #wait for 10 seconds to process the audio file 
    status_reponse = requests.get( url = api_url , headers = headers )
    reponse_content = json.loads(status_reponse.content.decode('utf8'))
    print(f"converted reponse content: {reponse_content}")
    #if reponse is not error we wont get code in the reponse key so ,get is used
    if reponse_content.get('code',200) != 200:
        raise Exception(f"Error in reponse: {reponse_content}")
    
    extracted_text_list = reponse_content.get('results',[])
    transcript_text , number_of_speakers = concat_transcript_text( transcript_results = extracted_text_list )

    return transcript_text , number_of_speakers
        
    # except Exception as er :
    #     pass
    #     print(f"error occured error is: {er}")
    #     traceback.print_exc()
    

def get_audio_transcript( audio_file_path , api_key , api_ip , config ):
    audio_id = submit_audio_to_API( audio_file_path = audio_file_path , api_key = api_key , api_ip = api_ip , config = config )
    time.sleep(20)
    transcript_text , number_of_speakers = get_id_transcript( id = audio_id , api_key = api_key )
    return transcript_text , number_of_speakers


def hit_speech_to_text_api( audio_file_path , words_list , config = SPEECH_TO_TEXT_CONFIG ):
    """
    updates the config using words_list , hits the api with the audio file and gets metadata
    args: 
        audio_file_path: path to the audio file
        words_list: list of keywords to be added in the config file
    
    return:
        transcript_text: text from the audio file
        number_of_speakers: number of speakers in the audio file
    """

    # updating the config file
    config = words_to_add(words_list = words_list, config= config)

    transcript_text , number_of_speakers = get_audio_transcript( audio_file_path = audio_file_path , api_key = SPEECH_TO_TEXT_API_KEY , api_ip = SPEECH_TO_TEXT_API_IP , config = config )
    
    return transcript_text , number_of_speakers


#function that takes either an MP4 or a wav file, and returns the transcript from it
def get_transcript( input_file_path , words_list = [] ):
    """
    args:
        input_file:[str] path to either a .mp4, .ts or a .wav file to send to the api and get back transcript and number of speakers
        words_list:[list] list of keywords to be added in the config file

    function: if the file is not a .wav then convert it to .wav and hit the api, otherwise directly hit the api.
    """

    if input_file_path.lower().endswith((".mp4", ".ts",'.mp3')) :
        
        #convert it to .wav using ffmpeg
        input_file_name = os.path.basename( input_file_path )
        output_file = f"{input_file_name.split('.')[0]}.wav"
        
        ffmpeg_cmd = f"ffmpeg -y -i {input_file_path}  {output_file}"
        os.system(ffmpeg_cmd)
    
    elif input_file_path.lower().endswith('.wav'):
        output_file = input_file_path
    
    #if the file type is not of proper format then just return empty string and 0 number of speakers
    else:
        return '' , 0
    
    # hit api on output_file
    transcript_text, number_of_speakers = hit_speech_to_text_api( audio_file_path = output_file , words_list = words_list )

    return transcript_text , number_of_speakers


def speech_to_text_main(start_time, end_time, input_video_path_list, words_list):
    """
    converts the video to audio and then saves the audio file in the same directory as the video file as out.wav 
    then passes the out.wav file to the API and gets the transcript
    args:
        start_time: string, time of format: 00:00:00 tells from where the audio is to processed
        end_time: string, time of format: 00:00:00 tells till where the audio is to processed
        input_video_path_list: list of videos from where the audio is to be proccessed.
        words_list: list of keywords to be added in the config file
    
    return:
        the transcript and number of speakers
    """
    output_videos = get_output_videos( start_time = start_time , end_time = end_time , input_video_list = input_video_path_list )

    # print(output_videos)
    #Now merge the videos into one output video and convert it into a .wav file using ffmpeg

    # write a the names in output_videos to a file named output_videos.txt
    videos_text_file_path = "output_videos/output_videos.txt"
    with open( videos_text_file_path , "w") as f:
        for video in output_videos:
            video = "file " + video.split("/")[-1]
            f.write(video + "\n")

    merged_video_path = "merged_video.mp4"
    #concat all the files in the text file to one file with ffmpeg
    ffmpef_cmd = f"ffmpeg -y -safe 0 -f concat -segment_time_metadata 1 -i output_videos.txt -vf select=concatdec_select -af aselect=concatdec_select,aresample=async=1 {merged_video_path}"
    os.system(ffmpef_cmd)

    transcript_text , number_of_speakers = get_transcript( input_file = merged_video_path , words_list = words_list )

    return transcript_text, number_of_speakers
