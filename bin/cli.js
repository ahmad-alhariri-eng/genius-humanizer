#!/usr/bin/env node

/**
 * Genius Humanizer CLI
 * AI-powered text humanizer that bypasses AI detection tools.
 * 
 * Usage:
 *   genius-humanizer <file>           Humanize a text file
 *   genius-humanizer --gui            Launch the GUI application
 *   genius-humanizer --setup          Install Python dependencies
 *   genius-humanizer --test           Run a quick test
 *   genius-humanizer --help           Show help
 */

const { humanizeFile, humanizeText, launchGUI, runSetup, runTest, checkPython } = require('../lib/humanizer');
const path = require('path');
const fs = require('fs');

// ─── Colors for terminal output ───
const c = {
    reset: '\x1b[0m',
    bold: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    dim: '\x1b[2m',
};

function printBanner() {
    console.log(`
${c.magenta}${c.bold}╔══════════════════════════════════════════════════╗
║         GENIUS TEXT HUMANIZER v1.0.0              ║
║     AI Detection Bypass Engine (Anti-GPTZero)     ║
╚══════════════════════════════════════════════════╝${c.reset}
`);
}

function printHelp() {
    printBanner();
    console.log(`${c.cyan}${c.bold}USAGE:${c.reset}

  ${c.green}genius-humanizer${c.reset} <file>              Humanize a .txt, .md, or .docx file
  ${c.green}genius-humanizer${c.reset} --gui               Launch the desktop GUI
  ${c.green}genius-humanizer${c.reset} --setup             Install required Python packages
  ${c.green}genius-humanizer${c.reset} --test              Quick test with sample text
  ${c.green}genius-humanizer${c.reset} --help              Show this help message
  
${c.cyan}${c.bold}EXAMPLES:${c.reset}

  ${c.dim}# Humanize an article file${c.reset}
  genius-humanizer article.txt

  ${c.dim}# Humanize and save to specific output file${c.reset}
  genius-humanizer article.txt -o humanized.txt

  ${c.dim}# Launch the graphical interface${c.reset}
  genius-humanizer --gui

  ${c.dim}# Pipe text from stdin${c.reset}
  echo "AI generated text here" | genius-humanizer

${c.cyan}${c.bold}REQUIREMENTS:${c.reset}

  - Python 3.8+ must be installed
  - Run ${c.green}genius-humanizer --setup${c.reset} to install Python dependencies

${c.cyan}${c.bold}HOW IT WORKS:${c.reset}

  The engine targets 5 AI detection signals:
  ${c.yellow}1.${c.reset} Perplexity  — Injects uncommon word choices
  ${c.yellow}2.${c.reset} Burstiness  — Creates dramatic sentence length variation
  ${c.yellow}3.${c.reset} Entropy     — Breaks uniform structural patterns
  ${c.yellow}4.${c.reset} Uniformity  — Varies vocabulary and rhythm
  ${c.yellow}5.${c.reset} Predictability — Restructures sentence patterns
`);
}

// ─── Main ───
async function main() {
    const args = process.argv.slice(2);

    // No arguments — check for piped input
    if (args.length === 0) {
        // Check if stdin is piped
        if (!process.stdin.isTTY) {
            let input = '';
            process.stdin.setEncoding('utf8');
            for await (const chunk of process.stdin) {
                input += chunk;
            }
            if (input.trim()) {
                printBanner();
                await humanizeText(input.trim());
                return;
            }
        }
        printHelp();
        return;
    }

    const arg = args[0];

    // Flags
    if (arg === '--help' || arg === '-h') {
        printHelp();
        return;
    }

    if (arg === '--gui') {
        printBanner();
        console.log(`${c.cyan}Launching GUI...${c.reset}\n`);
        await launchGUI();
        return;
    }

    if (arg === '--setup') {
        printBanner();
        await runSetup();
        return;
    }

    if (arg === '--test') {
        printBanner();
        await runTest();
        return;
    }

    // File argument
    const filePath = path.resolve(arg);
    if (!fs.existsSync(filePath)) {
        console.error(`${c.red}Error: File not found: ${filePath}${c.reset}`);
        process.exit(1);
    }

    const ext = path.extname(filePath).toLowerCase();
    if (!['.txt', '.md', '.docx'].includes(ext)) {
        console.error(`${c.red}Error: Unsupported file type '${ext}'. Use .txt, .md, or .docx${c.reset}`);
        process.exit(1);
    }

    // Determine output file
    let outputFile = null;
    const outputIdx = args.indexOf('-o');
    if (outputIdx !== -1 && args[outputIdx + 1]) {
        outputFile = path.resolve(args[outputIdx + 1]);
    }

    printBanner();
    await humanizeFile(filePath, outputFile);
}

main().catch(err => {
    console.error(`${c.red}Fatal error: ${err.message}${c.reset}`);
    process.exit(1);
});
