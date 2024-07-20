import speech_recognition as sr


def main():
  print('Setting up Recognizer')
  r = sr.Recognizer()
  
  print('Opening Microphone')
  try:
    with sr.Microphone() as source:
      print('Listening to microphone')
      audio = r.listen(source, timeout=5)
      
      print("recognizing audio")
      text = r.recognize(audio)
      print("You said: " + text)
  except Exception as e:
    print(f"An error occurred: {e}")


if __name__ == "__main__":
  main()