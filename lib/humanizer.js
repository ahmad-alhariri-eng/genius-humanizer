/**
 * Genius Humanizer — Node.js wrapper for the Python engine
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const PYTHON_DIR = path.join(__dirname, '..', 'python');
const c = {
    reset: '\x1b[0m', bold: '\x1b[1m',
    red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m',
    blue: '\x1b[34m', cyan: '\x1b[36m', dim: '\x1b[2m',
};

// ─── Find Python executable ───
function findPython() {
    const candidates = ['python3', 'python', 'py'];
    for (const cmd of candidates) {
        try {
            const version = execSync(`${cmd} --version 2>&1`, { encoding: 'utf8' }).trim();
            if (version.includes('Python 3')) {
                return cmd;
            }
        } catch (e) {
            continue;
        }
    }
    return null;
}

// ─── Check Python is available ───
function checkPython() {
    const python = findPython();
    if (!python) {
        console.error(`${c.red}${c.bold}Error: Python 3 is not installed or not in PATH.${c.reset}`);
        console.error(`${c.yellow}Please install Python 3.8+ from https://python.org${c.reset}`);
        process.exit(1);
    }
    return python;
}

// ─── Run a Python script ───
function runPythonScript(scriptName, args = [], options = {}) {
    return new Promise((resolve, reject) => {
        const python = checkPython();
        const scriptPath = path.join(PYTHON_DIR, scriptName);

        if (!fs.existsSync(scriptPath)) {
            reject(new Error(`Python script not found: ${scriptPath}`));
            return;
        }

        const proc = spawn(python, [scriptPath, ...args], {
            cwd: PYTHON_DIR,
            stdio: options.inherit ? 'inherit' : ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
        });

        let stdout = '';
        let stderr = '';

        if (!options.inherit) {
            proc.stdout.on('data', (data) => {
                const text = data.toString();
                stdout += text;
                if (options.onStdout) options.onStdout(text);
            });

            proc.stderr.on('data', (data) => {
                const text = data.toString();
                stderr += text;
                if (options.onStderr) options.onStderr(text);
            });
        }

        proc.on('close', (code) => {
            if (code === 0) {
                resolve(stdout.trim());
            } else {
                reject(new Error(stderr || `Python process exited with code ${code}`));
            }
        });

        proc.on('error', (err) => {
            reject(new Error(`Failed to start Python: ${err.message}`));
        });
    });
}

// ─── Humanize a file ───
async function humanizeFile(filePath, outputFile) {
    console.log(`${c.cyan}Input:${c.reset}  ${filePath}`);

    if (!outputFile) {
        const dir = path.dirname(filePath);
        const ext = path.extname(filePath);
        const base = path.basename(filePath, ext);
        outputFile = path.join(dir, `${base}_humanized${ext}`);
    }

    console.log(`${c.cyan}Output:${c.reset} ${outputFile}`);
    console.log(`${c.dim}─────────────────────────────────────────${c.reset}`);
    console.log(`${c.yellow}Processing... This may take a few minutes.${c.reset}\n`);

    try {
        const result = await runPythonScript('cli_humanize.py', [filePath], {
            onStderr: (text) => {
                // Show progress messages from Python
                if (text.includes('Progress:') || text.includes('Loading') || text.includes('Model')) {
                    process.stderr.write(`${c.dim}${text}${c.reset}`);
                }
            }
        });

        // Write output
        fs.writeFileSync(outputFile, result, 'utf8');

        console.log(`\n${c.dim}─────────────────────────────────────────${c.reset}`);
        console.log(`${c.green}${c.bold}✓ Done!${c.reset} Humanized text saved to: ${c.cyan}${outputFile}${c.reset}`);

        // Show stats
        const originalWords = fs.readFileSync(filePath, 'utf8').split(/\s+/).length;
        const humanizedWords = result.split(/\s+/).length;
        console.log(`${c.dim}  Original:  ${originalWords} words${c.reset}`);
        console.log(`${c.dim}  Humanized: ${humanizedWords} words${c.reset}`);

    } catch (err) {
        console.error(`\n${c.red}Error: ${err.message}${c.reset}`);
        console.error(`${c.yellow}Run 'genius-humanizer --setup' to install dependencies.${c.reset}`);
        process.exit(1);
    }
}

// ─── Humanize piped text ───
async function humanizeText(text) {
    console.log(`${c.yellow}Processing piped input (${text.split(/\s+/).length} words)...${c.reset}\n`);

    // Write to temp file
    const tmpFile = path.join(PYTHON_DIR, '_tmp_input.txt');
    fs.writeFileSync(tmpFile, text, 'utf8');

    try {
        const result = await runPythonScript('cli_humanize.py', [tmpFile], {
            onStderr: (text) => {
                if (text.includes('Progress:')) {
                    process.stderr.write(`${c.dim}${text}${c.reset}`);
                }
            }
        });

        // Output to stdout for piping
        console.log(result);
    } finally {
        // Clean up
        if (fs.existsSync(tmpFile)) fs.unlinkSync(tmpFile);
    }
}

// ─── Launch GUI ───
async function launchGUI() {
    const python = checkPython();
    const guiScript = path.join(PYTHON_DIR, 'gui_app.py');

    if (!fs.existsSync(guiScript)) {
        console.error(`${c.red}GUI script not found: ${guiScript}${c.reset}`);
        process.exit(1);
    }

    console.log(`${c.green}Starting GUI application...${c.reset}`);

    const proc = spawn(python, [guiScript], {
        cwd: PYTHON_DIR,
        stdio: 'inherit',
        detached: true,
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });

    proc.unref();
}

// ─── Setup Python dependencies ───
async function runSetup() {
    console.log(`${c.cyan}${c.bold}Installing Python dependencies...${c.reset}\n`);

    const python = checkPython();
    const reqFile = path.join(PYTHON_DIR, 'requirements.txt');

    if (!fs.existsSync(reqFile)) {
        console.error(`${c.red}requirements.txt not found${c.reset}`);
        process.exit(1);
    }

    try {
        execSync(`${python} -m pip install -r "${reqFile}"`, {
            stdio: 'inherit',
            cwd: PYTHON_DIR,
        });
        console.log(`\n${c.green}${c.bold}✓ All dependencies installed successfully!${c.reset}`);
        console.log(`${c.dim}You can now run: genius-humanizer <file>${c.reset}`);
    } catch (err) {
        console.error(`\n${c.red}Failed to install dependencies. Please run manually:${c.reset}`);
        console.error(`${c.yellow}pip install -r ${reqFile}${c.reset}`);
        process.exit(1);
    }
}

// ─── Quick test ───
async function runTest() {
    console.log(`${c.cyan}Running quick test...${c.reset}\n`);

    const testText = "Artificial Intelligence has fundamentally transformed the landscape of modern education. Educational institutions around the world are increasingly adopting AI-powered tools to enhance learning outcomes and streamline administrative processes.";

    const tmpFile = path.join(PYTHON_DIR, '_tmp_test.txt');
    fs.writeFileSync(tmpFile, testText, 'utf8');

    try {
        console.log(`${c.dim}Original:${c.reset}`);
        console.log(`${testText}\n`);

        const result = await runPythonScript('cli_humanize.py', [tmpFile], {
            onStderr: (text) => {
                process.stderr.write(`${c.dim}${text}${c.reset}`);
            }
        });

        console.log(`\n${c.green}${c.bold}Humanized:${c.reset}`);
        console.log(result);
        console.log(`\n${c.green}✓ Test passed!${c.reset}`);
    } catch (err) {
        console.error(`\n${c.red}Test failed: ${err.message}${c.reset}`);
        console.error(`${c.yellow}Run 'genius-humanizer --setup' first.${c.reset}`);
    } finally {
        if (fs.existsSync(tmpFile)) fs.unlinkSync(tmpFile);
    }
}

module.exports = { humanizeFile, humanizeText, launchGUI, runSetup, runTest, checkPython };
