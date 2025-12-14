<#
.SYNOPSIS
    Argus Intelligence Platform - Windows Setup Script

.DESCRIPTION
    Sets up the Argus Intelligence Platform development environment on Windows.
    Compatible with PowerShell 5.1+ and PowerShell 7+.
    Idempotent - safe to run multiple times.

.PARAMETER Backend
    Set up backend only

.PARAMETER Frontend
    Set up frontend only

.PARAMETER Models
    Download Ollama models only

.PARAMETER SkipModels
    Skip Ollama model download

.PARAMETER Force
    Force reinstallation even if already set up

.EXAMPLE
    .\setup-windows.ps1
    Full setup (backend, frontend, and models)

.EXAMPLE
    .\setup-windows.ps1 -Backend
    Set up backend only

.EXAMPLE
    .\setup-windows.ps1 -Frontend -SkipModels
    Set up frontend only, skip model download

.EXAMPLE
    .\setup-windows.ps1 -Force
    Force complete reinstallation
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage="Set up backend only")]
    [switch]$Backend,

    [Parameter(HelpMessage="Set up frontend only")]
    [switch]$Frontend,

    [Parameter(HelpMessage="Download Ollama models only")]
    [switch]$Models,

    [Parameter(HelpMessage="Skip Ollama model download")]
    [switch]$SkipModels,

    [Parameter(HelpMessage="Force reinstallation")]
    [switch]$Force
)

# Set strict mode for better error catching
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Store original location to restore at the end
$OriginalLocation = Get-Location

# Determine what to set up based on flags
$SetupBackend = $Backend -or (!$Frontend -and !$Models)
$SetupFrontend = $Frontend -or (!$Backend -and !$Models)
$SetupModels = $Models -or (!$SkipModels -and !$Frontend -and !$Backend)

#region Helper Functions

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet('Info','Success','Warning','Error')]
        [string]$Type = 'Info'
    )

    $color = switch ($Type) {
        'Info'    { 'Cyan' }
        'Success' { 'Green' }
        'Warning' { 'Yellow' }
        'Error'   { 'Red' }
    }

    $prefix = switch ($Type) {
        'Info'    { '[*]' }
        'Success' { '[✓]' }
        'Warning' { '[!]' }
        'Error'   { '[✗]' }
    }

    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Get-PythonCommand {
    # Try different Python command variations
    $pythonCommands = @('python', 'python3', 'py')
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            return $cmd
        }
    }
    return $null
}

function Test-MinimumVersion {
    param(
        [string]$Version,
        [int]$MinMajor,
        [int]$MinMinor = 0
    )

    if ($Version -match '(\d+)\.(\d+)') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        return ($major -gt $MinMajor) -or ($major -eq $MinMajor -and $minor -ge $MinMinor)
    }
    return $false
}

function Invoke-CommandWithErrorHandling {
    param(
        [string]$Command,
        [string]$ErrorMessage,
        [switch]$IgnoreErrors
    )

    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -ne 0 -and !$IgnoreErrors) {
            throw "$ErrorMessage (Exit code: $LASTEXITCODE)"
        }
    }
    catch {
        if ($IgnoreErrors) {
            Write-Status $_.Exception.Message 'Warning'
        }
        else {
            Write-Status $_.Exception.Message 'Error'
            throw
        }
    }
}

#endregion

#region Prerequisite Checks

function Test-Prerequisites {
    Write-Section "Checking Prerequisites"

    $allPrereqsMet = $true

    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    Write-Status "PowerShell Version: $psVersion" 'Info'

    if ($psVersion.Major -lt 5) {
        Write-Status "PowerShell 5.1 or higher required (found $psVersion)" 'Error'
        $allPrereqsMet = $false
    }

    # Check Python
    Write-Status "Checking Python..." 'Info'
    $pythonCmd = Get-PythonCommand

    if ($pythonCmd) {
        try {
            $pythonVersion = & $pythonCmd --version 2>&1 | Out-String
            $pythonVersion = $pythonVersion.Trim()
            Write-Status "Found $pythonVersion" 'Success'

            if (!(Test-MinimumVersion -Version $pythonVersion -MinMajor 3 -MinMinor 11)) {
                Write-Status "Python 3.11+ recommended (found $pythonVersion)" 'Warning'
            }

            # Store the working Python command globally
            $script:PythonCommand = $pythonCmd
        }
        catch {
            Write-Status "Python found but unable to get version" 'Warning'
            $allPrereqsMet = $false
        }
    }
    else {
        Write-Status "Python not found in PATH" 'Error'
        Write-Status "Download from: https://www.python.org/downloads/" 'Info'
        Write-Status "Make sure to check 'Add Python to PATH' during installation" 'Info'
        $allPrereqsMet = $false
    }

    # Check Node.js
    if ($SetupFrontend) {
        Write-Status "Checking Node.js..." 'Info'

        if (Test-Command 'node') {
            try {
                $nodeVersion = node --version 2>&1
                Write-Status "Found Node.js $nodeVersion" 'Success'

                if (!(Test-MinimumVersion -Version $nodeVersion -MinMajor 18)) {
                    Write-Status "Node.js 18+ recommended (found $nodeVersion)" 'Warning'
                }
            }
            catch {
                Write-Status "Node.js found but unable to get version" 'Warning'
            }

            if (Test-Command 'npm') {
                try {
                    $npmVersion = npm --version 2>&1
                    Write-Status "Found npm v$npmVersion" 'Success'
                }
                catch {
                    Write-Status "npm found but unable to get version" 'Warning'
                }
            }
            else {
                Write-Status "npm not found" 'Error'
                $allPrereqsMet = $false
            }
        }
        else {
            Write-Status "Node.js not found" 'Error'
            Write-Status "Download from: https://nodejs.org/" 'Info'
            $allPrereqsMet = $false
        }
    }

    # Check Ollama (optional but recommended)
    if ($SetupModels) {
        Write-Status "Checking Ollama..." 'Info'

        if (Test-Command 'ollama') {
            try {
                $ollamaVersion = ollama --version 2>&1 | Out-String
                $ollamaVersion = $ollamaVersion.Trim()
                Write-Status "Found $ollamaVersion" 'Success'
                $script:OllamaAvailable = $true
            }
            catch {
                Write-Status "Ollama found but unable to get version" 'Warning'
                $script:OllamaAvailable = $false
            }
        }
        else {
            Write-Status "Ollama not found" 'Warning'
            Write-Status "Download from: https://ollama.com/download/windows" 'Info'
            Write-Status "AI features will not work without Ollama" 'Warning'
            $script:OllamaAvailable = $false
        }
    }

    if (!$allPrereqsMet) {
        throw "Prerequisites check failed. Please install missing components and try again."
    }

    Write-Status "All prerequisites met!" 'Success'
}

#endregion

#region Backend Setup

function Initialize-Backend {
    Write-Section "Backend Setup"

    # Navigate to backend directory
    $backendPath = Join-Path $OriginalLocation "backend"

    if (!(Test-Path $backendPath)) {
        throw "Backend directory not found: $backendPath"
    }

    Set-Location $backendPath

    # Check if virtual environment already exists
    $venvPath = Join-Path $backendPath "venv"
    $venvExists = Test-Path $venvPath

    if ($venvExists -and !$Force) {
        Write-Status "Virtual environment already exists" 'Info'
        $response = Read-Host "Recreate virtual environment? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Status "Skipping virtual environment creation" 'Info'
            $venvExists = $true
        }
        else {
            Write-Status "Removing existing virtual environment..." 'Info'
            Remove-Item -Path $venvPath -Recurse -Force
            $venvExists = $false
        }
    }
    elseif ($venvExists -and $Force) {
        Write-Status "Removing existing virtual environment (Force mode)..." 'Info'
        Remove-Item -Path $venvPath -Recurse -Force
        $venvExists = $false
    }

    # Create virtual environment
    if (!$venvExists) {
        Write-Status "Creating Python virtual environment..." 'Info'
        Invoke-CommandWithErrorHandling `
            -Command "& $script:PythonCommand -m venv venv" `
            -ErrorMessage "Failed to create virtual environment"
        Write-Status "Virtual environment created successfully" 'Success'
    }

    # Activate virtual environment and install dependencies
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

    if (!(Test-Path $activateScript)) {
        throw "Virtual environment activation script not found: $activateScript"
    }

    Write-Status "Activating virtual environment..." 'Info'

    try {
        # Activate the virtual environment
        & $activateScript

        Write-Status "Upgrading pip..." 'Info'
        Invoke-CommandWithErrorHandling `
            -Command "python -m pip install --upgrade pip --quiet" `
            -ErrorMessage "Failed to upgrade pip"

        # Check if requirements.txt exists
        $requirementsPath = Join-Path $backendPath "requirements.txt"
        if (!(Test-Path $requirementsPath)) {
            throw "requirements.txt not found: $requirementsPath"
        }

        Write-Status "Installing Python dependencies (this may take a few minutes)..." 'Info'
        Invoke-CommandWithErrorHandling `
            -Command "pip install -r requirements.txt --quiet" `
            -ErrorMessage "Failed to install Python dependencies"

        Write-Status "Backend dependencies installed successfully" 'Success'
    }
    finally {
        # Note: Deactivation in PowerShell is handled by closing the script
    }

    # Create .env file if it doesn't exist
    $envPath = Join-Path $backendPath ".env"

    if (!(Test-Path $envPath) -or $Force) {
        Write-Status "Creating default .env file..." 'Info'

        $envContent = @"
# Application
APP_NAME=Argus Intelligence Platform
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./storage/database/research_tool.db

# AI Providers
DEFAULT_EMBEDDING_PROVIDER=local
DEFAULT_LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=gurubot/llama3-guru-uncensored:latest

# Optional API Keys (only if using cloud AI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# OSINT APIs (Optional)
SHODAN_API_KEY=
VT_API_KEY=
HIBP_API_KEY=

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
"@

        $envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline
        Write-Status "Default .env file created" 'Success'
        Write-Status "Edit backend/.env to add your API keys if needed" 'Info'
    }
    else {
        Write-Status ".env file already exists (skipping)" 'Info'
    }

    Write-Status "Backend setup complete!" 'Success'
}

#endregion

#region Frontend Setup

function Initialize-Frontend {
    Write-Section "Frontend Setup"

    # Navigate to frontend directory
    $frontendPath = Join-Path $OriginalLocation "frontend"

    if (!(Test-Path $frontendPath)) {
        throw "Frontend directory not found: $frontendPath"
    }

    Set-Location $frontendPath

    # Check if node_modules already exists
    $nodeModulesPath = Join-Path $frontendPath "node_modules"

    if ((Test-Path $nodeModulesPath) -and !$Force) {
        Write-Status "node_modules already exists" 'Info'
        $response = Read-Host "Reinstall dependencies? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Status "Skipping npm install" 'Info'
            return
        }
        Write-Status "Removing existing node_modules..." 'Info'
        Remove-Item -Path $nodeModulesPath -Recurse -Force
    }
    elseif ((Test-Path $nodeModulesPath) -and $Force) {
        Write-Status "Removing existing node_modules (Force mode)..." 'Info'
        Remove-Item -Path $nodeModulesPath -Recurse -Force
    }

    Write-Status "Installing Node.js dependencies (this may take a few minutes)..." 'Info'

    try {
        # Use npm ci if package-lock.json exists, otherwise npm install
        $packageLockPath = Join-Path $frontendPath "package-lock.json"

        if (Test-Path $packageLockPath) {
            Invoke-CommandWithErrorHandling `
                -Command "npm ci" `
                -ErrorMessage "Failed to install Node.js dependencies"
        }
        else {
            Invoke-CommandWithErrorHandling `
                -Command "npm install" `
                -ErrorMessage "Failed to install Node.js dependencies"
        }

        Write-Status "Frontend dependencies installed successfully" 'Success'
    }
    catch {
        Write-Status "npm install failed. Trying with --legacy-peer-deps..." 'Warning'
        Invoke-CommandWithErrorHandling `
            -Command "npm install --legacy-peer-deps" `
            -ErrorMessage "Failed to install Node.js dependencies even with --legacy-peer-deps"
    }

    Write-Status "Frontend setup complete!" 'Success'
}

#endregion

#region Ollama Models Setup

function Initialize-OllamaModels {
    Write-Section "Ollama Models Setup"

    if (!$script:OllamaAvailable) {
        Write-Status "Ollama not available, skipping model download" 'Warning'
        Write-Status "Install Ollama from: https://ollama.com/download/windows" 'Info'
        Write-Status "Then run: ollama pull nomic-embed-text" 'Info'
        Write-Status "Then run: ollama pull gurubot/llama3-guru-uncensored:latest" 'Info'
        return
    }

    Write-Status "Downloading Ollama models (this may take a while)..." 'Info'
    Write-Status "Models are several GB in size" 'Warning'

    # Check if models are already downloaded
    try {
        $existingModels = ollama list 2>&1 | Out-String

        # Check embedding model
        if ($existingModels -match 'nomic-embed-text') {
            Write-Status "Embedding model (nomic-embed-text) already downloaded" 'Info'
        }
        else {
            Write-Status "Downloading embedding model (nomic-embed-text)..." 'Info'
            Invoke-CommandWithErrorHandling `
                -Command "ollama pull nomic-embed-text" `
                -ErrorMessage "Failed to download embedding model" `
                -IgnoreErrors
        }

        # Check LLM model
        if ($existingModels -match 'gurubot/llama3-guru-uncensored') {
            Write-Status "LLM model (gurubot/llama3-guru-uncensored:latest) already downloaded" 'Info'
        }
        else {
            Write-Status "Downloading LLM model (gurubot/llama3-guru-uncensored:latest)..." 'Info'
            Invoke-CommandWithErrorHandling `
                -Command "ollama pull gurubot/llama3-guru-uncensored:latest" `
                -ErrorMessage "Failed to download LLM model" `
                -IgnoreErrors
        }

        Write-Status "Ollama models setup complete!" 'Success'
    }
    catch {
        Write-Status "Failed to download Ollama models" 'Warning'
        Write-Status $_.Exception.Message 'Warning'
        Write-Status "You can download them manually later with:" 'Info'
        Write-Status "  ollama pull nomic-embed-text" 'Info'
        Write-Status "  ollama pull gurubot/llama3-guru-uncensored:latest" 'Info'
    }
}

#endregion

#region Main Script

try {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host " Argus Intelligence Platform - Windows Setup" -ForegroundColor Cyan
    Write-Host " PowerShell $($PSVersionTable.PSVersion)" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""

    if ($Force) {
        Write-Status "Force mode enabled - will reinstall everything" 'Warning'
    }

    # Display what will be set up
    Write-Status "Setup configuration:" 'Info'
    if ($SetupBackend) { Write-Status "  • Backend (Python)" 'Info' }
    if ($SetupFrontend) { Write-Status "  • Frontend (Node.js)" 'Info' }
    if ($SetupModels) { Write-Status "  • Ollama Models" 'Info' }
    Write-Host ""

    # Check prerequisites
    Test-Prerequisites

    # Run requested setups
    if ($SetupBackend) {
        Initialize-Backend
        Set-Location $OriginalLocation
    }

    if ($SetupFrontend) {
        Initialize-Frontend
        Set-Location $OriginalLocation
    }

    if ($SetupModels) {
        Initialize-OllamaModels
        Set-Location $OriginalLocation
    }

    # Success summary
    Write-Section "Setup Complete!"

    Write-Status "Successfully set up:" 'Success'
    if ($SetupBackend) { Write-Status "  ✓ Backend" 'Success' }
    if ($SetupFrontend) { Write-Status "  ✓ Frontend" 'Success' }
    if ($SetupModels -and $script:OllamaAvailable) { Write-Status "  ✓ Ollama Models" 'Success' }

    Write-Host ""
    Write-Status "To start the application:" 'Info'
    Write-Host ""

    if ($SetupBackend) {
        Write-Status "1. Start Backend (PowerShell):" 'Info'
        Write-Host "   cd backend" -ForegroundColor White
        Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
        Write-Host ""
        Write-Status "   Or use: .\start-backend.bat" 'Info'
        Write-Host ""
    }

    if ($SetupFrontend) {
        Write-Status "2. Start Frontend (PowerShell):" 'Info'
        Write-Host "   cd frontend" -ForegroundColor White
        Write-Host "   npm run dev" -ForegroundColor White
        Write-Host ""
        Write-Status "   Or use: .\start-frontend.bat" 'Info'
        Write-Host ""
    }

    Write-Status "Then open: http://localhost:5173" 'Info'
    Write-Host ""

    # Exit successfully
    exit 0
}
catch {
    Write-Host ""
    Write-Status "Setup failed!" 'Error'
    Write-Status $_.Exception.Message 'Error'

    if ($_.ScriptStackTrace) {
        Write-Host ""
        Write-Host "Stack trace:" -ForegroundColor Red
        Write-Host $_.ScriptStackTrace -ForegroundColor Red
    }

    Write-Host ""
    Write-Status "Please fix the errors above and run the script again" 'Info'
    Write-Status "For help, visit: https://github.com/Taimaishu/-argus-intelligence-platform" 'Info'

    # Exit with error
    exit 1
}
finally {
    # Restore original location
    Set-Location $OriginalLocation
}

#endregion
