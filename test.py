import whisper
import time

model = whisper.load_model("tiny")
start = time.time()
result = model.transcribe(r"C:\Users\hp\Desktop\Agent\downloades\-0uJMbWOjEc.wav_chunk_0.wav")
print(f"Done in {time.time() - start:.1f} seconds")
print(result["text"])