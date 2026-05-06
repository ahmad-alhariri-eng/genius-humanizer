from genius_humanizer import GeniusHumanizer
import sys
import os

def main():
    print("==================================================")
    print("   GENIUS TEXT HUMANIZER (AI POWERED)   ")
    print("==================================================")
    
    # Initialize implementation
    try:
        bot = GeniusHumanizer()
    except Exception as e:
        print(f"Critical Error initializing: {e}")
        return

    # Check for command line input
    text_to_process = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.exists(arg):
            print(f"Reading file: {arg}")
            with open(arg, 'r', encoding='utf-8') as f:
                text_to_process = f.read()
        else:
            text_to_process = " ".join(sys.argv[1:])
    
    # Interactive loop if no args
    if not text_to_process:
        print("\nEnter text to humanize (type 'exit' to quit):")
        while True:
            text_to_process = input("\n> ")
            if text_to_process.lower() in ['exit', 'quit']:
                break
            
            print("Thinking...", end="", flush=True)
            result = bot.humanize(text_to_process)
            print(" Done!\n")
            print("--- Result ---")
            print(result)
            print("--------------")
    else:
        print("\nProcessing...", end="", flush=True)
        result = bot.humanize(text_to_process)
        print(" Done!\n")
        print("--- Result ---")
        print(result)
        print("--------------")

if __name__ == "__main__":
    main()
