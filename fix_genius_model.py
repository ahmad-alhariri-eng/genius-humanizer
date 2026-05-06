from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

def load_genius_model():
    print("\nAttempting to load the genius model...")
    model_name = "Vamsi/T5_Paraphrase_Paws"
    
    try:
        print("Loading Tokenizer...")
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        
        print("Loading Model...")
        # Just load normally now, no resume_download args
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        print("\n✅ Model loaded successfully! You are ready to go.")
        return True
    except Exception as e:
        print(f"\n❌ Model Load Failed: {e}")
        return False

if __name__ == "__main__":
    load_genius_model()
