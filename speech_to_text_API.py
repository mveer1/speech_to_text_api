import os
import uvicorn
import traceback
from fastapi import FastAPI, File, UploadFile, Form
from typing import List,Optional

from text_recognition.main_fn import GenTextOutput, process_input
from metadata_extraction.final_metadata_extraction import metadata_main
from speech_to_text import get_transcript

app = FastAPI(debug=True)

#two end points: 
#    two end points, one will accept a media file video or audio, will return a transcript (additonal functionality of adding words), 
#                    another will be,  accept a video, run ocr, get the top keywords, send them to speech_to_text, return the transcript.

@app.post("/main_transcript/")
def get_transcript_api(file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    """
    args:
        file: file to be uploaded
    function: 
        this function will accept a media file video or audio, will return a transcript.
    """
    try:
        keywords = []
        if text:
            keywords = text.split(",")
        
        print("RECIEVED FILE:", file.filename)
        #save the file to a temp location at file_path
        if file:
            if not os.path.exists("./tmp/"):
                os.mkdir("./tmp/")
            file_path = os.path.join("./tmp/" , file.filename)
            print("Saving the file temporarily at:", file_path)
            with open(file_path, "wb") as f:
                f.write(file.file.read())
                
        transcript, _ =  get_transcript(file_path, keywords)
        print("EXECUTION COMPLETED, Size of the Transcript:", len(transcript))
    except Exception as e:
        print("error:", e)
        traceback.print_exc()
    return transcript

@app.post("/transcript_through_video/")
def get_transcript_through_video(video_file: Optional[UploadFile] = File(None)):
    """
    args:
        video_file: video file to be uploaded, mp4 or ts

    function: 
        this function will accept a video, run ocr on the video, get the top keywords, send them to speech_to_text, return the transcript.
    """
    
    #run gen_text_output on video_file, get the keywords
    keywords = []
    print("RECIEVED FILE:", video_file, video_file.filename)

    image_list , frame_timestamps , is_video , destination = process_input(files=[video_file])#, video_path=file_path)
    print("PROCESSED INPUT", "dest:", destination, "is_video:", is_video, "image_list:", len(image_list), "frame_timestamps:", len(frame_timestamps))

    text_output = GenTextOutput(image_list = image_list, frame_timestamps= frame_timestamps)    
    print("GOT TEXT OUTPUT:", text_output)
    
    keywords_dict = metadata_main( frames_data = text_output)
    print(keywords_dict)


uvicorn.run(app, host='0.0.0.0', port=8080)





