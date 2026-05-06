@echo off
echo ===================================================
echo Installing AI Genius Dependencies (Deep Learning)
echo ===================================================
echo.
echo 1. Installing PyTorch (CPU version for stability)...
pip install torch torchvision torchaudio
if %errorlevel% neq 0 goto error

echo.
echo 2. Installing Transformers...
pip install transformers --default-timeout=1000
if %errorlevel% neq 0 goto error

echo.
echo 3. Installing SentencePiece...
pip install sentencepiece --default-timeout=1000
if %errorlevel% neq 0 goto error

echo.
echo 4. Installing spaCy & Language Tools...
pip install spacy --default-timeout=1000
if %errorlevel% neq 0 goto error

echo.
echo 5. Downloading spaCy English Model (Small)...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 goto error

echo.
echo ===================================================
echo ✅ All Genius Dependencies Installed Successfully!
echo ===================================================
pause
exit /b 0

:error
echo.
echo ❌ Installation Failed. Please check your internet connection.
pause
exit /b 1
