import streamlit as st
import speech_recognition as sr
import pyttsx3
import pyautogui
import webbrowser
import threading
import queue

engine = pyttsx3.init()
recognizer = sr.Recognizer()
engine_lock = threading.Lock()
speech_queue = queue.Queue()
stop_listening = threading.Event()

gif_path = 'M:\gem\oo1.gif'

def add_custom_html_css():
    st.markdown("""
        <style>
        .header {
            font-size: 40px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
        }
        .subheader {
            font-size: 20px;
            color: #555;
            margin-bottom: 20px;
        }
        .button-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        
        .custom-button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            cursor: pointer;
            border-radius: 12px;
            transition-duration: 0.4s;
        }
        .custom-button:hover {
            background-color: white;
            color: #4CAF50;
            border: 2px solid #4CAF50;
        }
       
 

        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='header'>Voice Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='subheader'>Your AI-powered voice assistant, ready to assist you with tasks!</div>", unsafe_allow_html=True)


def listen_for_command():
    with sr.Microphone() as source:
        st.write("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            st.write("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            st.write("Could not understand audio. Please try again.")
            enqueue_speech("Could not understand the audio, please repeat.")
            return None
        except sr.RequestError:
            st.write("Unable to access the Google Speech Recognition API.")
            enqueue_speech("There seems to be an issue with the Google API.")
            return None
        except sr.WaitTimeoutError:
            st.write("Listening timed out. Please try again.")
            return None

def enqueue_speech(response_text):
    speech_queue.put(response_text)

def process_speech_queue():
    while not speech_queue.empty():
        response_text = speech_queue.get()
        with engine_lock:
            try:
                engine.say(response_text)
                engine.runAndWait()
            except RuntimeError:
                st.write("Speech engine is busy. Please try again later.")

tasks = []
listeningToTask = False

def execute_command(command):
    global tasks
    global listeningToTask

    triggerKeyword = "bixby"
    if triggerKeyword in command:
        if listeningToTask:
            tasks.append(command.replace(triggerKeyword, "").strip())
            listeningToTask = False
            enqueue_speech(f"Added task. You have {len(tasks)} tasks.")
        elif "add a task" in command:
            listeningToTask = True
            enqueue_speech("Sure, what is the task?")
        elif "list tasks" in command:
            if tasks:
                enqueue_speech("Here are your tasks:")
                for task in tasks:
                    enqueue_speech(task)
            else:
                enqueue_speech("Your task list is empty.")
        elif "take a screenshot" in command:
            pyautogui.screenshot("screenshot.png")
            enqueue_speech("I took a screenshot for you.")
        elif "open chrome" in command:
            enqueue_speech("Opening Chrome.")
            webbrowser.open("https://www.google.com/")
        elif command in ["stop", "exit", "completed"]:
            enqueue_speech("Stopping listening.")
            stop_listening.set()
        else:
            enqueue_speech("Sorry, I'm not sure how to handle that command.")
    else:
        enqueue_speech("No trigger keyword detected. Command not executed.")

def speech_thread():
    while not stop_listening.is_set():
        process_speech_queue()

def main():
    add_custom_html_css()  # Add custom HTML and CSS

    st.write("This is your virtual assistant, ready to help.")

    stop_listening.clear()

    if threading.active_count() < 2: 
        threading.Thread(target=speech_thread, daemon=True).start()

    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    if st.button("Start Listening", key="start"):
        st.image(gif_path, width=300)
        with st.spinner("Listening..."):
            command = listen_for_command()
            if command:
                execute_command(command)
    
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Stop Listening"):
        stop_listening.set()
        st.write("Stopped listening.")

if __name__ == "__main__":
    main()
