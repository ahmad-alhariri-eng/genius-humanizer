# Genius Humanizer

> **AI-powered text humanizer** that bypasses AI detection tools like GPTZero, Turnitin, and Originality.ai by targeting the core statistical signals they measure.

[![npm version](https://img.shields.io/npm/v/genius-humanizer.svg)](https://www.npmjs.com/package/genius-humanizer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## How It Works

AI detectors measure 5 key signals. Genius Humanizer targets all of them:

| Signal | What Detectors Look For | What We Do |
|--------|------------------------|------------|
| **Perplexity** | Predictable word choices | Inject uncommon synonyms from 80+ word maps |
| **Burstiness** | Uniform sentence lengths | Create dramatic length variation |
| **Entropy** | Repetitive patterns | Break structural uniformity |
| **Uniformity** | Same rhythm throughout | Vary vocabulary and sentence structure |
| **Predictability** | AI-favorite phrases | Replace 20+ common AI phrases |

**Key Innovation:** Only 30% of sentences go through the T5 AI model. The other 70% use rule-based transformations that have **zero AI fingerprint**.

---

## Installation

### Quick Start (via npx)
```bash
npx genius-humanizer article.txt
```

### Global Install
```bash
npm install -g genius-humanizer
```

### Prerequisites
- **Node.js** v14+
- **Python** 3.8+

After installing, run the setup to install Python dependencies:
```bash
genius-humanizer --setup
```

---

## Usage

### Humanize a file
```bash
genius-humanizer article.txt
# Output: article_humanized.txt

genius-humanizer essay.md -o output.md
# Output: output.md
```

### Pipe from stdin
```bash
echo "AI generated text goes here" | genius-humanizer
```

### Launch GUI
```bash
genius-humanizer --gui
```

### Quick test
```bash
genius-humanizer --test
```

### Supported file types
- `.txt` — Plain text
- `.md` — Markdown
- `.docx` — Microsoft Word

---

## Example

**Input (AI-generated):**
> Artificial Intelligence has fundamentally transformed the landscape of modern education. Educational institutions around the world are increasingly adopting AI-powered tools to enhance learning outcomes and streamline administrative processes.

**Output (Humanized):**
> AI has really changed how we think about modern education. Schools everywhere are more and more using AI-powered tools to boost learning outcomes and simplify administrative processes. That's huge.

---

## API (Programmatic Use)

```javascript
const { humanizeFile, humanizeText } = require('genius-humanizer');

// Humanize a file
await humanizeFile('input.txt', 'output.txt');

// Humanize piped text
await humanizeText('Your AI-generated text here');
```

---

## How Detection Bypass Works

1. **Synonym Diversity** — 80+ AI-favorite words mapped to multiple casual alternatives, randomly chosen each time
2. **Phrase Replacement** — 20+ common AI phrases ("in conclusion", "it is important to note") replaced with human alternatives
3. **Contractions** — 30+ contraction patterns applied (AI rarely contracts; humans almost always do)
4. **Sentence Restructuring** — Prepositional phrase reordering, voice switching
5. **Burstiness Engineering** — Long sentences split, short ones merged, "punch" sentences injected
6. **Parenthetical Asides** — Mid-sentence interjections that humans naturally add
7. **Starter Rotation** — Conversational openers injected sparsely with tone rotation to avoid new patterns

---

## License

MIT © Ahmad
