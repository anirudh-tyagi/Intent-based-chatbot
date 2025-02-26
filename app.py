import pickle
import random
import ssl
import nltk
import re
import string
import json
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Initialize NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')
stopwords_set = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# These intents file is also available on this repo named as intents.json
intents = [
    {
      "tag": "greeting",
      "patterns": [
        "Hi",
        "Hello",
        "Hey",
        "How are you?",
        "Good morning",
        "Good afternoon",
        "What's up?",
        "Hi there",
        "Greetings"
      ],
      "responses": [
        "Hello! How can I help you today?",
        "Hi there! How's it going?",
        "Hey! What can I do for you?",
        "Good morning! How are you today?",
        "Hi! How can I assist you?"
      ]
    },
    {
      "tag": "goodbye",
      "patterns": [
        "Goodbye",
        "Bye",
        "See you later",
        "Take care",
        "See you soon",
        "Later",
        "Have a nice day",
        "Catch you later"
      ],
      "responses": [
        "Goodbye! Have a great day!",
        "See you later! Take care!",
        "Goodbye, take care of yourself!",
        "Catch you later!",
        "See you soon, stay safe!"
      ]
    },
    {
      "tag": "thanks",
      "patterns": [
        "Thank you",
        "Thanks",
        "I appreciate it",
        "You're awesome",
        "Thanks a lot",
        "Thank you so much"
      ],
      "responses": [
        "You're welcome! Let me know if you need anything else.",
        "Happy to help! Anytime.",
        "You're welcome! Don't hesitate to ask if you need more assistance.",
        "Glad I could help! 😊",
        "It's my pleasure! Let me know if you need more assistance."
      ]
    },
    {
      "tag": "apology",
      "patterns": [
        "Sorry",
        "Apologies",
        "I didn't mean that",
        "My bad",
        "I apologize",
        "Excuse me"
      ],
      "responses": [
        "No problem at all!",
        "It's alright, no need to apologize.",
        "No worries, we all make mistakes!",
        "It's okay, everything’s fine!",
        "Don’t worry about it!"
      ]
    },
    {
      "tag": "help",
      "patterns": [
        "Can you help me?",
        "I need help",
        "Help me out",
        "I don’t understand",
        "Can you assist me?",
        "I need assistance",
        "What should I do?"
      ],
      "responses": [
        "Of course! What do you need help with?",
        "I’m here to assist you! What’s the problem?",
        "How can I help you today?",
        "Feel free to ask anything, I’m here to help!",
        "Let me know how I can assist you."
      ]
    },
    {
      "tag": "weather",
      "patterns": [
        "What's the weather like?",
        "Is it raining today?",
        "Do I need an umbrella?",
        "What's the temperature?",
        "Will it snow today?",
        "Is it sunny?"
      ],
      "responses": [
        "I can't check the weather right now, but you can easily find it online!",
        "Sorry, I don't have access to current weather information.",
        "It’s a good idea to check a weather website or app for that.",
        "I’m afraid I can’t provide weather information, but you can check a weather service."
      ]
    },
    {
      "tag": "complaint",
      "patterns": [
        "I’m not happy with this",
        "This is frustrating",
        "I’m not satisfied",
        "This doesn’t work",
        "I have an issue",
        "There is a problem",
        "I’m upset with this"
      ],
      "responses": [
        "I’m sorry to hear that! Can you tell me more about the issue?",
        "I apologize for the inconvenience. How can I assist you in resolving this?",
        "Let me know how I can help improve your experience.",
        "I’m really sorry for this issue. I’ll do my best to assist you.",
        "Please share the details, and I’ll do my best to resolve it."
      ]
    },
    {
      "tag": "small_talk",
      "patterns": [
        "How are you?",
        "What’s up?",
        "How’s it going?",
        "What are you doing?",
        "How’s your day going?",
        "What’s happening?"
      ],
      "responses": [
        "I’m doing great, thank you for asking! How about you?",
        "I’m here, ready to assist you!",
        "I’m just here, chatting with you!",
        "All good! How can I help today?",
        "I’m doing great, thanks for asking! What can I do for you?"
      ]
    },
    {
      "tag": "joke",
      "patterns": [
        "Tell me a joke",
        "Make me laugh",
        "Tell me something funny",
        "Give me a joke",
        "I need a good laugh"
      ],
      "responses": [
        "Why don't skeletons fight each other? They don't have the guts!",
        "Why was the math book sad? Because it had too many problems.",
        "Why don’t eggs tell each other secrets? Because they might crack up!",
        "I told my computer I needed a break, now it won’t stop sending me KitKats.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
      ]
    },
    {
      "tag": "quote",
      "patterns": [
        "Tell me a quote",
        "Give me some inspiration",
        "I need motivation",
        "Give me a quote",
        "Inspire me"
      ],
      "responses": [
        "“The only way to do great work is to love what you do.” – Steve Jobs",
        "“Success is not the key to happiness. Happiness is the key to success.” – Albert Schweitzer",
        "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson",
        "“Believe you can and you’re halfway there.” – Theodore Roosevelt",
        "“Success is not final, failure is not fatal: It is the courage to continue that counts.” – Winston Churchill"
      ]
    },
    {
      "tag": "motivation",
      "patterns": [
        "I feel down",
        "I’m not motivated",
        "Can you motivate me?",
        "I feel unproductive",
        "I need encouragement"
      ],
      "responses": [
        "Believe in yourself! You've got this!",
        "Every small step counts. Keep going!",
        "The future depends on what you do today. Keep pushing forward!",
        "Success comes to those who persevere. Stay strong!",
        "Don't give up! Every setback is a setup for a comeback."
      ]
    },
    {
      "tag": "time",
      "patterns": [
        "What time is it?",
        "Can you tell me the time?",
        "What’s the time?",
        "What time do you have?",
        "Can you check the time for me?"
      ],
      "responses": [
        "I can't check the time right now, but you can check it on your device!",
        "You can easily find the time on your phone or watch!",
        "Sorry, I can’t check the time, but you can check any clock nearby!"
      ]
    },
    {
      "tag": "thanks_for_help",
      "patterns": [
        "Thanks for helping",
        "You’ve been helpful",
        "I appreciate your help",
        "Thanks for the assistance",
        "That was very helpful"
      ],
      "responses": [
        "You're very welcome! Glad I could help.",
        "I'm happy to assist anytime!",
        "I'm glad I could be of help, don't hesitate to ask more.",
        "Thank you for your kind words! Feel free to ask if you need anything else."
      ]
    },
    {
      "tag": "random_fact",
      "patterns": [
        "Tell me a random fact",
        "Give me a fact",
        "Share something interesting",
        "Tell me something cool",
        "I want to learn something new"
      ],
      "responses": [
        "Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient tombs that are over 3,000 years old!",
        "Here’s a fun fact: Bananas are berries, but strawberries are not!",
        "Here's an interesting one: The shortest war in history lasted just 38 to 45 minutes between Britain and Zanzibar in 1896.",
        "Here’s a cool fact: A day on Venus is longer than a year on Venus!",
        "Did you know? You can’t hum while holding your nose."
      ]
    },
    {
      "tag": "fact_about_me",
      "patterns": [
        "Tell me about you",
        "Who are you?",
        "What is your name?",
        "What can you do?"
      ],
      "responses": [
        "I'm a chatbot created to assist you! How can I help today?",
        "I’m here to answer your questions and make your day easier.",
        "I’m a virtual assistant here to help with whatever you need!",
        "I’m your friendly chatbot, ready to assist with your inquiries!"
      ]
    },
    {
      "tag": "movie_recommendation",
      "patterns": [
        "Suggest a movie",
        "Give me a movie to watch",
        "What should I watch?",
        "Recommend a movie for me",
        "Can you suggest a good movie?"
      ],
      "responses": [
        "If you love action, I recommend 'Mad Max: Fury Road'. If you're in the mood for comedy, try 'The Hangover'.",
        "If you're a fan of sci-fi, 'Inception' is a great pick!",
        "How about 'The Shawshank Redemption' for a classic drama?",
        "I recommend 'The Matrix' for an exciting sci-fi movie.",
        "If you like thrillers, 'Gone Girl' is a must-watch."
      ]
    },
    {
      "tag": "book_recommendation",
      "patterns": [
        "Recommend a book",
        "Give me a book suggestion",
        "What book should I read?",
        "Tell me a good book",
        "Can you suggest a book?"
      ],
      "responses": [
        "If you're into fantasy, 'Harry Potter' is a great choice!",
        "Try 'Sapiens: A Brief History of Humankind' by Yuval Noah Harari if you're into non-fiction.",
        "For a classic, I’d recommend '1984' by George Orwell.",
        "If you enjoy thrillers, try 'The Girl with the Dragon Tattoo'.",
        "How about 'The Alchemist' by Paulo Coelho for a life-changing read?"
      ]
    },
    {
      "tag": "general_information",
      "patterns": [
        "Tell me about technology",
        "What is AI?",
        "How does the internet work?",
        "Explain blockchain",
        "What is machine learning?"
      ],
      "responses": [
        "AI stands for Artificial Intelligence, and it refers to the simulation of human intelligence in machines.",
        "The internet is a network of networks that allows computers worldwide to communicate with each other.",
        "Blockchain is a decentralized digital ledger used for securely recording transactions across many computers.",
        "Machine learning is a subset of AI that focuses on building systems that can learn from data and make decisions."
      ]
    }
  ]

# Preprocessing 
def regex_tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def data_preprocess(text):
    tokens = regex_tokenize(text)
    processed_tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in string.punctuation and word not in stopwords_set
    ]
    return processed_tokens

# Model and vectorizer initialization
def train_model():
    # Prepare training data
    patterns = []
    labels = []
    for intent in intents:
        for pattern in intent["patterns"]:
            patterns.append(pattern)
            labels.append(intent["tag"])

    # Convert patterns into numerical data using TF-IDF
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(patterns)
    
    # Train a simple classifier (Naive Bayes)
    model = MultinomialNB()
    model.fit(X_train, labels)
    
    return model, vectorizer

# Train the model and vectorizer
model, vectorizer = train_model()

# Chatbot function
def chatbot(user_inp):
    user_inp = data_preprocess(user_inp)
    user_inp_vectorized = vectorizer.transform([' '.join(user_inp)])
    
    # Predict the intent
    tag = model.predict(user_inp_vectorized)[0]
    
    # Find the response
    for intent in intents:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    
    return "Sorry, I didn't understand that."

# Streamlit app setup
st.title("Intent-Based ChatBot")

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me here...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})    


    ans = chatbot(prompt)
    with st.chat_message("assistant"):
        st.markdown(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})