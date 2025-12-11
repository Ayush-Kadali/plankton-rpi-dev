#!/bin/bash
# One-time setup: Initialize git on RPi

set -e

# Load config
source .rpi_config 2>/dev/null || {
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
    RPI_PROJECT_DIR="~/plankton"
    GIT_BRANCH="main"
}

echo "========================================"
echo "🔧 SETUP GIT ON RASPBERRY PI"
echo "========================================"
echo ""

read -p "Have you set up SSH keys for GitHub on RPi? (y/n): " SSH_READY

if [ "$SSH_READY" != "y" ]; then
    echo ""
    echo "Setting up GitHub access on RPi..."
    echo ""

    ssh -t "$RPI_USER@$RPI_HOST" << 'ENDSSH'
        # Generate SSH key if not exists
        if [ ! -f ~/.ssh/id_rsa ]; then
            echo "Generating SSH key..."
            ssh-keygen -t rsa -b 4096 -C "rpi@plankton" -f ~/.ssh/id_rsa -N ""
        fi

        echo ""
        echo "📋 Copy this public key to GitHub:"
        echo "   https://github.com/settings/keys"
        echo ""
        cat ~/.ssh/id_rsa.pub
        echo ""
        read -p "Press Enter after adding the key to GitHub..."
ENDSSH
fi

echo ""
echo "Cloning repository on RPi..."

# Get repo URL
REPO_URL=$(git config --get remote.origin.url)
echo "Repository: $REPO_URL"

# Clone on RPi
ssh "$RPI_USER@$RPI_HOST" << ENDSSH
    # Remove existing directory if present
    if [ -d "$RPI_PROJECT_DIR" ]; then
        echo "Directory exists, updating..."
        cd $RPI_PROJECT_DIR
        git fetch origin
        git reset --hard origin/$GIT_BRANCH
    else
        echo "Cloning repository..."
        git clone $REPO_URL $RPI_PROJECT_DIR
        cd $RPI_PROJECT_DIR
        git checkout $GIT_BRANCH
    fi

    echo ""
    echo "Running setup script..."
    cd $RPI_PROJECT_DIR
    chmod +x setup_rpi.sh
    ./setup_rpi.sh
ENDSSH

echo ""
echo "✅ RPi setup complete!"
echo ""
echo "You can now use:"
echo "  ./sync_to_rpi.sh       # Sync changes"
echo "  ./run_on_rpi.sh        # Run detection"
echo "  ./quick_deploy.sh      # Sync + Run + Retrieve"
echo ""
echo "========================================"
