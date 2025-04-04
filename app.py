import os
import json
import random
from datetime import datetime
from flask import Flask, jsonify
import schedule
import time
import threading

app = Flask(__name__)

# Configuration
GITHUB_REPO_PATH = "static/content"  # Path to content within your repository
QUOTES_FILE = os.path.join(GITHUB_REPO_PATH, "quotes.json")
OUTPUT_FILE = os.path.join(GITHUB_REPO_PATH, "daily_content.json")

def get_all_audio_files():
    """Get all audio files from the audio directory."""
    audio_dir = os.path.join(GITHUB_REPO_PATH, "audio")
    return [f"audio/{file}" for file in os.listdir(audio_dir) if file.endswith(('.mp3', '.ogg', '.wav'))]

def get_all_background_images():
    """Get all background image files from the images directory."""
    images_dir = os.path.join(GITHUB_REPO_PATH, "images")
    return [f"images/{file}" for file in os.listdir(images_dir) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

def get_all_quotes():
    """Load quotes from the quotes.json file."""
    with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_daily_content():
    """Generate daily content and save to JSON file."""
    try:
        # Get available content
        quotes = get_all_quotes()
        audio_files = get_all_audio_files()
        background_images = get_all_background_images()
        
        # Select random content for today
        today_quote = random.choice(quotes)
        today_audio = random.choice(audio_files)
        today_background = random.choice(background_images)
        
        # Create daily content object
        daily_content = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "quote": {
                "text": today_quote["text"],
                "author": today_quote["author"]
            },
            "audio": today_audio,
            "background": today_background
        }
        
        # Save to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(daily_content, f, ensure_ascii=False, indent=2)
            
        print(f"Daily content generated for {daily_content['date']}")
        return daily_content
    except Exception as e:
        print(f"Error generating daily content: {e}")
        return {"error": str(e)}

@app.route('/generate', methods=['GET'])
def generate_endpoint():
    """Endpoint to manually trigger generation of daily content."""
    result = generate_daily_content()
    return jsonify(result)

@app.route('/current', methods=['GET'])
def get_current_content():
    """Endpoint to get the current daily content."""
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            content = json.load(f)
        return jsonify(content)
    except Exception as e:
        return jsonify({"error": str(e)})

def schedule_daily_generation():
    """Function to set up scheduled generation."""
    schedule.every().day.at("00:01").do(generate_daily_content)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs(os.path.join(GITHUB_REPO_PATH, "audio"), exist_ok=True)
    os.makedirs(os.path.join(GITHUB_REPO_PATH, "images"), exist_ok=True)
    
    # Create an example quotes file if it doesn't exist
    if not os.path.exists(QUOTES_FILE):
        example_quotes = [
            {"text": "The best way to predict the future is to create it.", "author": "Abraham Lincoln"},
            {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
            {"text": "The purpose of our lives is to be happy.", "author": "Dalai Lama"},
            {"text": "Get busy living or get busy dying.", "author": "Stephen King"},
            {"text": "You only live once, but if you do it right, once is enough.", "author": "Mae West"}
        ]
        with open(QUOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(example_quotes, f, ensure_ascii=False, indent=2)
    
    # Generate initial content if needed
    if not os.path.exists(OUTPUT_FILE):
        generate_daily_content()
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_daily_generation)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
