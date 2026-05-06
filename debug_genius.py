from genius_humanizer import GeniusHumanizer
import sys

def debug():
    print("Initializing...")
    gh = GeniusHumanizer()
    
    text = "The artificial intelligence algorithm efficiently utilizes big data to demonstrate significant improvements in performance."
    
    print(f"\nOriginal Full Text: {text}")
    print("-" * 50)
    
    # Access internal method to debug paraphrase logic manually
    # We will split manually like the class does
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    for i, sent in enumerate(sentences):
        if not sent.strip(): continue
        
        print(f"\nSentence {i+1}: '{sent}'")
        
        # 1. Raw T5 Paraphrase
        try:
            paraphrased = gh._paraphrase(sent)
            print(f"   -> T5 Output:    '{paraphrased}'")
            if paraphrased.strip() == sent.strip():
                print("   ⚠️ WARNING: Output identical to input!")
        except Exception as e:
            print(f"   -> T5 ERROR: {e}")
            paraphrased = sent
            
        # 2. Human Touch
        final = gh._add_human_touch(paraphrased)
        print(f"   -> Final Touch:  '{final}'")

if __name__ == "__main__":
    debug()
