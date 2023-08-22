# Following pip packages need to be installed:
# !pip install git+https://github.com/huggingface/transformers sentencepiece datasets

import string, random, os, sys
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf
from datasets import load_dataset

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def open_directory(path):
    if sys.platform.startswith('darwin'):  # macOS
        os.system('open "{}"'.format(path))
    elif sys.platform.startswith('win'):  # Windows
        os.system('start "" "{}"'.format(path))
    elif sys.platform.startswith('linux'):  # Linux
        os.system('xdg-open "{}"'.format(path))
    else:
        print("Unsupported operating system.")

class SpeechProcessorWrapper:
    def __init__(self):
        super(SpeechProcessorWrapper, self).__init__()

    # model: microsoft/speecht5_tts
    # vocoder: microsoft/speecht5_hifigan
    def init_process(self, model="microsoft/speecht5_tts", vocoder="microsoft/speecht5_hifigan"):
        """
        call only once if you're not switch the model
        """
        self.__processor = SpeechT5Processor.from_pretrained(model)
        self.__model = SpeechT5ForTextToSpeech.from_pretrained(model)
        self.__vocoder = SpeechT5HifiGan.from_pretrained(vocoder)


    # dataset: Matthijs/cmu-arctic-xvectors
    def convert_text_into_audio(self, text, filename, dataset='Matthijs/cmu-arctic-xvectors'):
        """
        call this after calling init_process
        """
        inputs = self.__processor(text=text, return_tensors="pt")

        # load xvector containing speaker's voice characteristics from a dataset
        embeddings_dataset = load_dataset(dataset, split="validation")
        speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

        print(embeddings_dataset.shape)
        print(speaker_embeddings.shape)

        speech = self.__model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=self.__vocoder)

        sf.write(filename, speech.numpy(), samplerate=16000)


# for CUI
# sentences = [
#     'Hello. My Dog is cute.',
# ]
#
# for i in range(len(sentences)):
#     convert_text_into_audio(sentences[i], filename=f'speech{i}.wav')