import sys, os
from pocketsphinx import *
from sphinxbase import *
import pyaudio
import logging

import my_logging

pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)

Running = False

# Create a decoder with certain model

config=None
mic_device_index=0
keywords=None
kws_file="keywords"

def save_keywords_to_file(new_keywords):
    my_logging.logger.info(f"will use keywords: {keywords}")
    with open(os.path.join(work_dir,kws_file), "w+") as text_file:
        for keyword in keywords:
            text_file.write(f"{keyword}/1e-20/\n")

def init(new_keywords, device_index):
    global config
    global keywords
    global mic_device_index

    mic_device_index=device_index
    keywords=new_keywords
    save_keywords_to_file(new_keywords)

    #to suppress pocketsphinx messages
    #self.asr.set_property('logfn', '/dev/null')
    
    logging.getLogger("pocketsphinx").setLevel(logging.CRITICAL)
    logging.getLogger("sphinxbase").setLevel(logging.CRITICAL)
  
    modeldir = os.path.dirname(pocketsphinx.__file__)+"/model"
    config = Decoder.default_config()
    config.set_string('-hmm', os.path.join(modeldir, 'en-us'))
    config.set_string('-dict', os.path.join(modeldir, 'cmudict-en-us.dict'))

    #config.set_string('-keyphrase', keywords[0])
    #config.set_float('-kws_threshold', 0.1)
    config.set_string('-kws', os.path.join(work_dir,kws_file))
    #to suppress logging
    config.set_string('-logfn', '/dev/null')
  

def stop_wait():
    global Running
    Running=False

def wait_for_keyword():
    global Running
    Running=True
    keywordFound=False
    p=None
    stream=None

    try:

        p = pyaudio.PyAudio()
        stream = p.open(input_device_index=mic_device_index, 
            format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048*8)
        stream.start_stream()

        # Process audio chunk by chunk. On keyphrase detected perform action and restart search
        decoder = Decoder(config)
        decoder.start_utt()
        while Running:
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
            else:
                break
            if decoder.hyp() != None:
                for seg in decoder.seg():
                    if seg.word in keywords:
                        keywordFound = True
                        break
                decoder.end_utt()
                if keywordFound:
                    break
                decoder.start_utt()
    except Exception as e:
        my_logging.logger.exception("psphinx pyaudio exception:")
    finally:
        # stop stream (4)
        if stream:
            stream.stop_stream()
            stream.close()

        # close PyAudio (5)
        if p:
            p.terminate()

    return keywordFound
