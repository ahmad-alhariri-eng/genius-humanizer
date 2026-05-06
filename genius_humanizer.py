import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import random
import re

class GeniusHumanizer:
    """
    Anti-Detection Humanizer v3.0
    Key insight: T5 output is STILL AI text. So we use T5 sparingly (30%)
    and rely heavily on rule-based transformations that have NO AI fingerprint.
    
    Detection signals we target:
    1. PERPLEXITY - inject uncommon/surprising word choices
    2. BURSTINESS - dramatic sentence length variation
    3. ENTROPY - break uniform patterns
    4. PREDICTABILITY - restructure sentences manually
    5. UNIFORMITY - vary everything (length, structure, vocabulary)
    """

    def __init__(self, use_gpu=False):
        print("Initializing Genius Humanizer v3.0...")
        self.device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")

        model_name = "Vamsi/T5_Paraphrase_Paws"
        try:
            print(f"Loading AI Model: {model_name}...")
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(model_name).to(self.device)
            print("AI Model Loaded Successfully.")
        except Exception as e:
            print(f"Failed to load AI Model: {e}")
            raise

        self._build_word_maps()
        self._last_starter_type = None

    def _build_word_maps(self):
        """Build all replacement maps."""
        # Multi-alternative synonyms (randomly chosen = higher perplexity)
        self.synonyms = {
            "moreover": ["on top of that", "plus", "and honestly"],
            "furthermore": ["also", "and beyond that", "adding to this"],
            "however": ["but", "that said", "then again", "still though"],
            "therefore": ["so", "because of this", "that's why"],
            "additionally": ["also", "on top of that", "plus"],
            "consequently": ["so", "as a result", "which led to"],
            "subsequently": ["then", "after that", "later on"],
            "utilize": ["use", "work with", "rely on"],
            "demonstrate": ["show", "prove", "highlight"],
            "commence": ["start", "kick off", "begin"],
            "terminate": ["end", "stop", "wrap up"],
            "endeavor": ["try", "attempt", "make an effort"],
            "approximately": ["about", "around", "roughly"],
            "nevertheless": ["still", "even so", "regardless"],
            "assist": ["help", "support", "back up"],
            "objective": ["goal", "aim", "target"],
            "construct": ["build", "put together", "create"],
            "numerous": ["many", "a lot of", "plenty of", "quite a few"],
            "primary": ["main", "key", "central", "core"],
            "components": ["parts", "pieces", "elements"],
            "regarding": ["about", "when it comes to", "as for"],
            "obtain": ["get", "pick up", "grab"],
            "retain": ["keep", "hold on to", "maintain"],
            "substantial": ["significant", "major", "serious"],
            "implement": ["carry out", "put into action", "apply"],
            "facilitate": ["help", "make easier", "enable"],
            "significant": ["major", "notable", "meaningful"],
            "fundamental": ["basic", "core", "essential"],
            "comprehensive": ["thorough", "detailed", "in-depth"],
            "particularly": ["especially", "specifically", "notably"],
            "essentially": ["basically", "at its core", "in simple terms"],
            "effectively": ["in practice", "really", "for all intents"],
            "increasingly": ["more and more", "gradually"],
            "individuals": ["people", "folks"],
            "sufficient": ["enough", "adequate", "plenty"],
            "determine": ["figure out", "find out", "work out"],
            "indicate": ["show", "point to", "suggest"],
            "establish": ["set up", "create", "form"],
            "enhance": ["improve", "boost", "strengthen"],
            "prior": ["before", "earlier", "previous"],
            "predominant": ["main", "dominant", "leading"],
            "undoubtedly": ["no doubt", "clearly", "for sure"],
            "paramount": ["critical", "top priority", "absolutely key"],
            "perpetuate": ["keep going", "continue", "carry on"],
            "mitigating": ["reducing", "lessening", "cutting down on"],
            "streamline": ["simplify", "make smoother", "speed up"],
            "proactive": ["ahead of time", "forward-thinking", "early"],
            "pedagogical": ["teaching", "educational", "instructional"],
            "methodology": ["approach", "method", "way of doing things"],
            "remediation": ["correction", "fixing", "catching up"],
            "intervention": ["step in", "action", "support"],
            "collaboration": ["teamwork", "working together", "partnership"],
            "framework": ["structure", "system", "setup"],
            "maximize": ["get the most out of", "make the most of"],
            "ultimately": ["in the end", "at the end of the day", "finally"],
        }

        # Phrase-level replacements (AI loves these exact phrases)
        self.phrase_replacements = {
            "it is important to note": ["worth mentioning", "one thing to keep in mind"],
            "it should be noted that": ["keep in mind that", "notice that"],
            "plays a crucial role": ["matters a lot", "is really important"],
            "a wide range of": ["all sorts of", "many different", "various"],
            "in order to": ["to", "so that we can", "for the purpose of"],
            "on the other hand": ["but then", "flip side is", "alternatively"],
            "as a result": ["so", "because of this", "which meant"],
            "in addition to": ["besides", "on top of", "along with"],
            "in conclusion": ["to wrap up", "all in all", "at the end of the day"],
            "for instance": ["like", "take for example", "say"],
            "in recent years": ["lately", "over the past few years", "these days"],
            "in recent decades": ["over the last several years", "in the past generation"],
            "a significant shift": ["a real change", "a big shake-up", "a noticeable move"],
            "raises several important concerns": ["brings up some real worries", "isn't without its problems"],
            "must be approached thoughtfully": ["needs careful handling", "requires some real thought"],
            "the landscape of": ["the world of", "how we think about"],
            "around the world": ["globally", "across the globe", "everywhere"],
            "the potential for": ["the risk of", "the chance of", "the possibility of"],
            "presents a significant challenge": ["is a real problem", "makes things harder"],
            "despite these advantages": ["but even with all that", "still though"],
            "tremendous opportunities": ["huge potential", "real promise", "big possibilities"],
        }

        # Contractions
        self.contractions = [
            (" do not ", " don't "), (" does not ", " doesn't "),
            (" did not ", " didn't "), (" is not ", " isn't "),
            (" are not ", " aren't "), (" was not ", " wasn't "),
            (" were not ", " weren't "), (" cannot ", " can't "),
            (" could not ", " couldn't "), (" should not ", " shouldn't "),
            (" would not ", " wouldn't "), (" will not ", " won't "),
            (" have not ", " haven't "), (" has not ", " hasn't "),
            (" I am ", " I'm "), (" we are ", " we're "),
            (" they are ", " they're "), (" it is ", " it's "),
            (" that is ", " that's "), (" let us ", " let's "),
            (" I have ", " I've "), (" you have ", " you've "),
            (" we have ", " we've "), (" they have ", " they've "),
            (" I will ", " I'll "), (" we will ", " we'll "),
            (" they will ", " they'll "), (" there is ", " there's "),
            (" who is ", " who's "), (" what is ", " what's "),
        ]

        # Sentence starters grouped by tone
        self.starters = {
            "casual": ["Look,", "Thing is,", "Here's the deal:", "So basically,"],
            "reflective": ["When you think about it,", "What's interesting is that",
                           "If you step back,", "It's worth noting that"],
            "contrast": ["That said,", "On the flip side,", "But here's the catch:",
                          "Then again,", "Oddly enough,"],
        }

        # Parenthetical asides (humans add these mid-sentence)
        self.asides = [
            " -- and this is key -- ", " (which is honestly surprising) ",
            " -- at least in theory -- ", " (believe it or not) ",
            " -- for better or worse -- ", " (and I mean that seriously) ",
            " -- which matters more than people realize -- ",
        ]

    # ═══════════════════════════════════════════════
    #  MAIN PIPELINE
    # ═══════════════════════════════════════════════

    def humanize(self, text, progress_callback=None):
        paragraphs = self._split_paragraphs(text)
        result = []
        total = len(paragraphs)

        for idx, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            if self._is_heading(para):
                result.append(para)
            else:
                humanized = self._process_paragraph(para)
                result.append(humanized)

            if progress_callback:
                progress_callback(int((idx + 1) / total * 100))

        return "\n\n".join(result)

    def _process_paragraph(self, para):
        sentences = self._split_sentences(para)
        processed = []

        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue
            if self._is_heading(sent) or len(sent.split()) < 4:
                processed.append(sent)
                continue

            # KEY DECISION: Only 30% go through T5, rest are rule-based
            if random.random() < 0.30:
                try:
                    p = self._paraphrase_t5(sent)
                    if len(p.split()) >= 3 and len(p) > len(sent) * 0.3:
                        sent = p
                except Exception:
                    pass

            # ALL sentences get rule-based processing (this is NOT AI-detectable)
            sent = self._replace_phrases(sent)
            sent = self._replace_words(sent)
            sent = self._apply_contractions(sent)
            sent = self._restructure_sentence(sent)

            # Occasionally add parenthetical aside
            if len(sent.split()) > 15 and random.random() < 0.12:
                sent = self._inject_aside(sent)

            processed.append(sent)

        # Burstiness: vary sentence lengths
        processed = self._engineer_burstiness(processed)

        # Sparse starters (1 per ~7 sentences)
        processed = self._inject_starters(processed)

        text = " ".join(processed)
        return self._polish(text)

    # ═══════════════════════════════════════════════
    #  SPLITTING / DETECTION
    # ═══════════════════════════════════════════════

    def _split_paragraphs(self, text):
        paras = re.split(r'\n\s*\n', text)
        if len(paras) <= 1:
            paras = text.split('\n')
        return paras

    def _split_sentences(self, text):
        return re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    def _is_heading(self, text):
        t = text.strip()
        if not t:
            return False
        if len(t.split()) <= 8 and t.istitle():
            return True
        if re.match(r'^(chapter|part|title|section|appendix|table of contents|full text)\b', t, re.IGNORECASE):
            return True
        if re.match(r'^[IVXLCDM]+[\.\)]\s', t) or re.match(r'^\d+[\.\)]\s', t):
            return True
        if ":" in t[:40] and len(t.split(":")[0].split()) < 6 and len(t) < 120:
            return True
        return False

    # ═══════════════════════════════════════════════
    #  T5 PARAPHRASE (used sparingly — 30% of sentences)
    # ═══════════════════════════════════════════════

    def _paraphrase_t5(self, sentence):
        text = "paraphrase: " + sentence + " </s>"
        encoding = self.tokenizer(text, padding=True, return_tensors="pt")
        input_ids = encoding["input_ids"].to(self.device)
        attention_masks = encoding["attention_mask"].to(self.device)

        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_masks,
            max_length=256,
            do_sample=True,
            top_k=60,
            top_p=0.92,
            temperature=1.08,
            repetition_penalty=1.15,
            num_return_sequences=2
        )

        candidates = []
        for output in outputs:
            decoded = self.tokenizer.decode(output, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            candidates.append(decoded)

        # Pick the one most different from original
        best = candidates[0]
        best_diff = 0
        orig_words = set(sentence.lower().split())
        for c in candidates:
            diff = len(set(c.lower().split()).symmetric_difference(orig_words))
            if len(c.split()) >= len(sentence.split()) * 0.5 and diff > best_diff:
                best_diff = diff
                best = c
        return best

    # ═══════════════════════════════════════════════
    #  RULE-BASED TRANSFORMS (NO AI fingerprint!)
    # ═══════════════════════════════════════════════

    def _replace_phrases(self, sentence):
        """Replace AI-favorite phrases with human alternatives."""
        lower = sentence.lower()
        for phrase, alts in self.phrase_replacements.items():
            if phrase in lower:
                replacement = random.choice(alts)
                # Preserve case of first char
                idx = lower.find(phrase)
                if idx == 0 or (idx > 0 and sentence[idx - 1] in '. '):
                    replacement = replacement[0].upper() + replacement[1:]
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                sentence = pattern.sub(replacement, sentence, count=1)
                lower = sentence.lower()
        return sentence

    def _replace_words(self, sentence):
        """Replace individual AI-favorite words."""
        words = sentence.split()
        new_words = []
        for word in words:
            clean = word.lower().strip(",.!?;:\"'()-")
            punct_start = ""
            punct_end = ""
            for c in word:
                if c in "\"'(-":
                    punct_start += c
                else:
                    break
            for c in reversed(word):
                if c in ",.!?;:\"')-":
                    punct_end = c + punct_end
                else:
                    break

            if clean in self.synonyms and random.random() < 0.70:
                replacement = random.choice(self.synonyms[clean])
                if word and word[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]
                new_words.append(punct_start + replacement + punct_end)
            else:
                new_words.append(word)
        return " ".join(new_words)

    def _apply_contractions(self, sentence):
        for full, contracted in self.contractions:
            if full in sentence and random.random() < 0.85:
                sentence = sentence.replace(full, contracted, 1)
        return sentence

    def _restructure_sentence(self, sentence):
        """Restructure sentences to break AI patterns."""
        words = sentence.split()
        if len(words) < 8:
            return sentence

        # Move trailing prepositional phrases to the front (20% chance)
        if random.random() < 0.20:
            # Look for "by/through/with/in [phrase]" at end
            match = re.search(r',?\s+(by|through|with|in|across|around)\s+(.+?)[.!?]$', sentence, re.IGNORECASE)
            if match:
                prep_phrase = match.group(1) + " " + match.group(2)
                main = sentence[:match.start()].strip()
                # Move to front
                sentence = prep_phrase.capitalize() + ", " + main[0].lower() + main[1:] + "."

        # Switch "X can Y" → "Y is possible through X" (10% chance)
        if random.random() < 0.10:
            match = re.match(r'^(.+?)\s+can\s+(.+?)([.!?])$', sentence)
            if match:
                subject = match.group(1)
                action = match.group(2)
                punct = match.group(3)
                sentence = f"It's possible to {action} using {subject.lower()}{punct}"

        return sentence

    def _inject_aside(self, sentence):
        """Insert a parenthetical aside mid-sentence for human feel."""
        words = sentence.split()
        if len(words) < 10:
            return sentence
        # Insert after roughly the middle
        mid = len(words) // 2
        # Find a good insertion point (after a comma or natural break)
        insert_at = mid
        for i in range(max(0, mid - 3), min(len(words), mid + 3)):
            if words[i].endswith(","):
                insert_at = i + 1
                break

        aside = random.choice(self.asides)
        words.insert(insert_at, aside)
        return " ".join(words)

    # ═══════════════════════════════════════════════
    #  BURSTINESS (sentence length variation)
    # ═══════════════════════════════════════════════

    def _engineer_burstiness(self, sentences):
        result = []
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent or self._is_heading(sent):
                result.append(sent)
                continue

            wc = len(sent.split())

            # Split very long sentences
            if wc > 28 and random.random() < 0.4:
                parts = self._try_split(sent)
                result.extend(parts)
                continue

            # Add short punch after long sentence
            if wc > 18 and random.random() < 0.12:
                result.append(sent)
                punches = ["That's huge.", "Think about that.", "Pretty remarkable.",
                           "And it worked.", "That changed everything.", "No small feat."]
                result.append(random.choice(punches))
                continue

            result.append(sent)
        return result

    def _try_split(self, sentence):
        for pattern in [r',\s+(but|and|so|which|while|because|since)\s+', r';\s+']:
            match = re.search(pattern, sentence)
            if match:
                first = sentence[:match.start()].strip().rstrip(",") + "."
                second = sentence[match.end():].strip()
                if second and second[0].islower():
                    second = second[0].upper() + second[1:]
                if len(first.split()) >= 4 and len(second.split()) >= 4:
                    return [first, second]
        return [sentence]

    # ═══════════════════════════════════════════════
    #  STARTER INJECTION (sparse, rotating)
    # ═══════════════════════════════════════════════

    def _inject_starters(self, sentences):
        result = []
        last_had = False
        count = 0
        max_count = max(1, len(sentences) // 7)

        types = list(self.starters.keys())

        for sent in sentences:
            sent = sent.strip()
            if not sent or self._is_heading(sent):
                result.append(sent)
                last_had = False
                continue

            should = (not last_had and count < max_count
                      and len(sent.split()) > 10 and random.random() < 0.15
                      and sent[0].isupper())

            if should:
                # Pick a different type than last time
                available = [t for t in types if t != self._last_starter_type]
                chosen_type = random.choice(available) if available else random.choice(types)
                starter = random.choice(self.starters[chosen_type])

                first_word = sent.split()[0].lower().rstrip(",")
                starter_first = starter.split()[0].lower().rstrip(",")
                if first_word != starter_first:
                    sent = f"{starter} {sent[0].lower() + sent[1:]}"
                    self._last_starter_type = chosen_type
                    count += 1
                    last_had = True
                else:
                    last_had = False
            else:
                last_had = False

            result.append(sent)
        return result

    # ═══════════════════════════════════════════════
    #  POLISH
    # ═══════════════════════════════════════════════

    def _polish(self, text):
        text = re.sub(r'  +', ' ', text)
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r',,+', ',', text)
        text = text.replace(". .", ".")
        text = re.sub(r'\.\s+([a-z])', lambda m: '. ' + m.group(1).upper(), text)
        return text.strip()


if __name__ == "__main__":
    gh = GeniusHumanizer()
    text = "Artificial Intelligence has fundamentally transformed the landscape of modern education."
    print("Original:", text)
    print("Genius:", gh.humanize(text))
