import streamlit as st
import cv2
import os
import tempfile
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
import shutil
import pafy

#3-1 version to incorporate granularity + youtube link 

st.set_page_config(page_title="Video to Text Demo", layout="wide")

st.title("Delphi Demo: Video Extraction Tool")

with st.sidebar:
    st.write("This is a demo created by Esperanto Technologies.")

col1, col2 = st.columns([0.55,0.45], gap="medium")
global vidcap

#Source: https://discuss.streamlit.io/t/clear-input-box-after-hitting-enter/33824/2
# if 'user_input' not in st.session_state:
#     st.session_state.user_input = ""

# if 'user_widget' not in st.session_state:
#     st.session_state.user_widget = ""

if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "frame_slider" not in st.session_state:
    st.session_state['frame_slider'] = 2

#https://discuss.streamlit.io/t/clearing-all-selected-items-check-box-radio-buttons-selectbox/16605
if "collage_slider" not in st.session_state:
    st.session_state["collage_slider"] = 5

#https://discuss.streamlit.io/t/any-plan-to-support-the-value-of-sidebar-slider-update/16052/3 
if "time_slider" not in st.session_state:
    st.session_state['time_slider'] = (0,0)

#https://discuss.streamlit.io/t/are-there-any-ways-to-clear-file-uploader-values-without-using-streamlit-form/40903 
if "file_uploader" not in st.session_state:
    st.session_state['file_uploader'] = 0

#Source: https://discuss.streamlit.io/t/how-do-you-clear-the-input-box-after-hitting-enter/45691/5
# def clear_text():
#     st.session_state.user_input = st.session_state.user_widget
#     st.session_state.user_widget = ""
#     st.session_state.disabled = True

def reset():
    st.session_state.user_input = ""
    st.session_state.user_widget = ""
    st.session_state.messages = []
    st.session_state.disabled = False
    st.session_state['frame_slider'] = 2
    st.session_state["collage_slider"] += 1
    st.session_state['time_slider'] = (0,int(durationInSeconds))
    # st.session_state.file_uploader += 1 
    # st.rerun()

# previous code to extract images from video (by sampling rate)  
#Source: https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
# def extractIndividual(frameRate):
#     frameRate = (end-start) // (frames - 1) #because a frame is already captured at 0 ms
#     def getFrame(sec):
#         #set current position of the video, its measuring unit is milliseconds
#         vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000) 
#         #frame is an image array vector captured based on the default frames per second defined explicitly or implicitly
#         hasFrames,image = vidcap.read()
#         if hasFrames and (sec <= end):
#             # Saves frames as JPG file to corresponding folder
#             cv2.imwrite(os.path.join(dirname,"image"+str(count)+".jpg"), image)
#         return hasFrames

#     count = 1
#     sec = start
#     dirname = str(frames) + "_individual_frames"
#     os.mkdir(dirname)
#     # os.path.join(dirname, face_file_name)
#     success = getFrame(sec)
#     while success:
#         count = count + 1
#         sec = sec + frameRate
#         # sec = round(sec, 2)
#         success = getFrame(sec)

# code to extract individual images from video
def extractIndividual(frames):
    # frame_count=int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    # skip_interval = max(int(frame_count/(frames - 1)), 1)
    frameRate = (end-start) / (frames - 1)
    #[WORK] low priority: if user already created the same frames, don't let them do it again
    dirname = str(start) + "to" + str(end) + "_" + str(frames) + "_individual_frames"
    os.mkdir(dirname)
    sec = start

    for counter in range(frames):
        #Set the current position of the video
        vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000) 
        #Read the current frame
        ret, frame = vidcap.read()
        if not ret:
            break
        cv2.imwrite(os.path.join(dirname,"image"+str(counter)+".jpg"), frame)
        sec += frameRate

# OR concatenate those images into 1 image
def extractCollage(collage):
    # width, height = 300, 400
    frames_list = []
    images = []
    sec = start
    # get the frame count
    # frame_count=int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    #Calculate the interval at which frames will be added to the list, based on selection
    if (collage == "2x2"):
        seq_length = 4
        frameRate = (end-start) / (seq_length - 1)
    elif (collage == "3x3"):
        seq_length = 9
        frameRate = (end-start) / (seq_length - 1)
    elif (collage == "2x4"):
        seq_length = 8
        frameRate = (end-start) / (seq_length - 1)
    elif (collage == "4x2"):
        seq_length = 8
        frameRate = (end-start) / (seq_length - 1)

    for counter in range(seq_length):   
        #Set the current time position of the video
        vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000) 
        #Read the current frame
        ret, frame = vidcap.read()
        if not ret:
            break
        #Resize the image
        index = [2,1,0]
        frame = frame[:,:,index]
        # frame=cv2.resize(frame, (height, width))
        frame = frame/255
        #Append to the frame
        frames_list.append(frame)
        sec += frameRate

    images.append(frames_list)

    for frame_list in images:
        for i, frame in enumerate(frame_list):
            # grid_image = np.concatenate([np.concatenate(frame_list[i:i+2], axis=1) for i in range(0, 4, 2)], axis=0)
            # Reshape the frames into a 1x9 row
            # row_image = np.concatenate(frame_list, axis=1)

            # reshape the frames into a grid
            if (collage == "2x2"):
                grid_image = np.concatenate([np.concatenate(frame_list[i:i+2], axis=1) for i in range(0, 4, 2)], axis=0)
            elif (collage == "3x3"):
                grid_image = np.concatenate([np.concatenate(frame_list[i:i+3], axis=1) for i in range(0, 9, 3)], axis=0)
            elif (collage == "2x4"):
                grid_image = np.concatenate([np.concatenate(frame_list[i:i+4], axis=1) for i in range(0, 8, 4)], axis=0)
            elif (collage == "4x2"):
                grid_image = np.concatenate([np.concatenate(frame_list[i:i+2], axis=1) for i in range(0, 8, 2)], axis=0)
        break
    cv2.imwrite(str(start) +"to"+ str(end) +"_"+collage+".jpg", cv2.cvtColor((grid_image * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))

#column code
with col1:
    upload, link = False, False
    type_vid = st.radio("Choose method of upload", ["Upload From Computer", "Youtube Link"])

    if (type_vid == "Upload From Computer"):
        uploaded_file = st.file_uploader("Upload a video:", key=st.session_state.file_uploader)
        if (uploaded_file != None): 
            upload = True
    elif (type_vid == "Youtube Link"):
        youtube = st.text_input("Or paste a youtube link:")
        if (youtube != ""): 
            link = True
    
    if (upload or link):
        if (upload):
            st.video(uploaded_file)
            
            #Process video: https://discuss.streamlit.io/t/how-to-access-uploaded-video-in-streamlit-by-open-cv/5831/7
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            vidcap = cv2.VideoCapture(tfile.name)
            
            # count the number of frames and calculate length of video (seconds)
            fps = vidcap.get(cv2.CAP_PROP_FPS)
            print("fps", fps)
            totalNoFrames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
            print("total no frames", totalNoFrames)
            durationInSeconds = totalNoFrames // fps

        elif (link):
            st.video(youtube)
            video = pafy.new(youtube)
            best = video.getbest(preftype="mp4")
            vidcap = cv2.VideoCapture(best.url)

            # count the number of frames and calculate length of video (seconds)
            fps = vidcap.get(cv2.CAP_PROP_FPS)
            print("fps", fps)
            totalNoFrames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
            print("total no frames", totalNoFrames)
            durationInSeconds = totalNoFrames // fps

        #user selection of start and end times 
        #[WORK] (low priority) Change to manually entering start and end times?
        start,end = st.slider("Select start and end time", 0.0, (durationInSeconds), 
                              step=0.1, key="time_slider", disabled=st.session_state.disabled)

        st.button("Reset Parameters",on_click=reset)

with col2:
    if (upload or link):
        st.write("###")
        st.write("###")
        st.write("###")
        st.write("###")
        st.write("###")
        tab1, tab2 = st.tabs(["Individual Frames", "Collage Concatenation"])

        with tab1:
            st.write("###")
            #user slider for how many images user wants to extract
            frames = st.slider("Number of Individual Frames to Extract", min_value=2, max_value=16,
                            key="frame_slider", disabled=st.session_state.disabled)
            
            st.write("###")
            framesButton = st.button("Extract Images", key="tabular1")
            if (framesButton):
                extractIndividual(frames)
                shutil.make_archive(str(start) + "to" + str(end) + "_"+str(frames)+"frames", 'zip', 
                                    str(start) + "to" + str(end) + "_"+str(frames)+"_individual_frames")
                st.download_button(":violet[Download Images]",
                                   data=open(str(start) +"to"+str(end)+"_"+str(frames)+"frames.zip", 'rb'),
                                   file_name=str(start) +"to"+str(end)+"_"+str(frames)+"frames.zip", 
                                   mime='application/zip')
            
        with tab2:
            st.write("###")
            #radio button to select what format of concatenated images
            collage = st.radio("Collage of Images to Extract", ["2x2", "3x3", "2x4", "4x2"],
                               key=st.session_state.collage_slider)
            
            st.write("###")
            collageButton = st.button("Extract Image", key="tabular2")
            if (collageButton):
                extractCollage(collage)
                st.download_button(":violet[Download Image]",
                                data=open(str(start) +"to"+ str(end) +"_"+collage+".jpg", 'rb').read(),
                                file_name=str(start) +"to"+ str(end) +"_"+collage+'.jpg', 
                                mime='image/jpg')
                

#should be functioning like GPT, where model and user trades answers
#source: https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
        
# if "messages" not in st.session_state:
#     st.session_state.messages = []

#chatgpt-like container => to finish with real models
# with col2:
#     with st.container(border=True): #empty box containing chat
        
#         if (uploaded_file != None): 
            
#             # only if user inputs something, show chatting box
#             if (st.session_state.user_input != ""):

#                 # Display chat messages from history on app rerun
#                 for message in st.session_state.messages:
#                     print(message)
#                     with st.chat_message(message["role"]):
#                         st.markdown(message["content"])

#                 user = st.chat_message("user")
#                 model = st.chat_message("assistant")
#                 user.markdown(st.session_state.user_input)
            
#                 # Add user message to chat history
#                 st.session_state.messages.append({"role": "user", "content": st.session_state.user_input})

#                 #assistant response
#                 response = f"Echo: {st.session_state.user_input}"

#                 # Display assistant response in chat message container
#                 model.markdown(response)
#                 # Add assistant response to chat history
#                 st.session_state.messages.append({"role": "assistant", "content": response})
                
