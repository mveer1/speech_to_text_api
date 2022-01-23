import os
import sys
import time
import uvicorn


project_dir = os.getcwd()
#add current dir to python library path for importing
sys.path.insert(1, project_dir)

from typing import List,Optional
from fastapi.responses import JSONResponse
from typing import Any, Dict, AnyStr, List, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Form, Request,Body
from text_recognition.main_fn import GenTextOutput , process_input
from metadata_extraction.final_metadata_extraction import metadata_main
from metadata_extraction.keyword_search_utils.search_response_utils import extract_entity , delete_file
from metadata_extraction.keyword_search_utils.speech_to_text_utils import speech_to_text_main , get_transcript

#initialize fast api client
app = FastAPI(debug=True)


#datatype for api input 
JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


#adding CORS(for allowing to hit from different addresses)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#class for handling wrong input 
class All_Exceptions(Exception):
    def __init__(self , message: str , status_code: int):
        self.message = message
        self.status_code = status_code


@app.exception_handler(All_Exceptions)
async def input_data_exception_handler(request: Request, exc: All_Exceptions):    
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! {exc.message} "}
    )




@app.post("/v1/video_analatics/")
def get_metadata_info(files: Optional[List[UploadFile]] = File(None),video_path:str=None,frame_timestamps:Optional[List[int]]=None):
	'''
	This function is used to get the metadata from the input data.
	Arguments:
		files: This is the input data which is a video file.(optional)
		video_path: This is the path of the video file present on the same server.(optional)
		frame_timestamps: This is the list of the frame timestamps.(timestamps fro the frames to be extracted from the video )(optional)

	return:
		metadata: json object containing all the metadata extracted from the video and audio
	'''
	#start time
	start_time = time.time()
	try:
		#process input data 
		images_list , frame_timestamps , is_video , destination = process_input( files = files , video_path = video_path , frame_timestamps = frame_timestamps )
		#is_video: boolean value indicating if the input is a video or not , destination: path to the video file

		if images_list==-1:
			raise All_Exceptions("Invalid input data",400)
		
		#call the text recognition function and get the json
		text_output = GenTextOutput( image_list = images_list , frame_timestamps = frame_timestamps )
		print(f"total time for OCR is: {time.time() - start_time}")
		metadata_start_time = time.time()
		#call the metadata extraction function and get the metadata json
		metadata = metadata_main( frames_data = text_output )
		print(f"total time taken for metadata extraction is: {time.time() - metadata_start_time}")

		#run speech to text if video is passed 
		if is_video:
			#get transcript and number of speakers
			framed_keywords = metadata['features_from_video'].get('keywords',{})
			words_list_to_add  = [ ky for ky in framed_keywords.keys() ]
			text_from_speech = get_transcript( input_file_path = destination , words_list = words_list_to_add )
			entity_from_speech = extract_entity( text_to_check = text_from_speech )
			
			metadata['speech_to_text'] = {}
			metadata['speech_to_text']['text_extracted'] = text_from_speech
			metadata['speech_to_text']['entity_extracted'] = entity_from_speech

			#delete mp4 file 
			delete_file( file_path = destination )
			#delete wav file
			destination = destination.replace('.mp4','.wav')
			delete_file( file_path = destination )	

		print(f"total time taken is: {time.time() - start_time}")
	
	except Exception as e:
		print("error occured error is: {}".format(e))
		error_message = "Internal server error , please try with different input parameters or contact the developer  "
		raise All_Exceptions(message= error_message, status_code = 500)
	
	
	return metadata


@app.post("/v1/metadata/")
def get_metadata_info( frames_data: JSONStructure = None ):
	'''
	This function calls the metadata extraction function and returns the metadata json.
	Arguments:
		frames_data: This is the input data which is a json object containing the frames data.(from Text API)
	return: 
		A JSON structure containing the metadata for the video
	'''
	#start time
	start_time = time.time()

	#check if the json passed is valid
	if not isinstance(frames_data,dict):
		raise All_Exceptions("Invalid input data",400)

	try:
		#call the metadata extraction function and get the metadata json
		metadata = metadata_main( frames_data = frames_data )
		
	
	except Exception as e:
		print(f"error occured error is: {e}")
		raise All_Exceptions(message= "Internal server error , please try with different input parameters or contact the developer  ", status_code = 500)
	
	print(f"total time taken is: {time.time() - start_time}")
	
	return metadata


if __name__ == "__main__":
    uvicorn.run('final_main:app', host='0.0.0.0', port=8080)
