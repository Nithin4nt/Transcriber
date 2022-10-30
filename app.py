import streamlit as st
from pytube import YouTube
import os
import sys
import time
import requests
from zipfile import ZipFile

st.markdown('# 📝 **TRANSCRIBER APP**')
bar = st.progress(0)

api_key = "a547c5d9b76f4231a2b4a39bdd3c4788"


st.warning('Awaiting URL input in the sidebar.')


st.sidebar.header('Input parameter')


with st.sidebar.form(key='my_form'):
	URL = st.text_input('Enter URL of YouTube video:')
	submit_button = st.form_submit_button(label='Go')


if submit_button == True:
    video = YouTube(URL)
    yt = video.streams.get_audio_only()
    filename = yt.download()
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    headers = {'authorization': api_key}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                            headers=headers,
                            data=read_file(filename))
    print(response.json())
    bar.progress(20)
    audio_url = response.json()['upload_url']

    endpoint = "https://api.assemblyai.com/v2/transcript"

    json = {
    "audio_url": audio_url
    }

    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    transcript_input_response = requests.post(endpoint, json=json, headers=headers)

    print(transcript_input_response)
    bar.progress(50)

    transcript_id = transcript_input_response.json()["id"]
    print(transcript_id)
    bar.progress(70)

    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {
        "authorization": api_key,
    }

    transcript_output_response = requests.get(endpoint, headers=headers)

    while transcript_output_response.json()['status'] != 'completed':
        # time.sleep(5)
        # st.warning('Transcription is processing ...')
        transcript_output_response = requests.get(endpoint, headers=headers)

    bar.progress(100)

    print(transcript_output_response.json()['status'])

    

    output = transcript_output_response.json()['text']

    st.header('Output')
    st.success(output)
