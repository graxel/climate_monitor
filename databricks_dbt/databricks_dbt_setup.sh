# Get username and server directory (where this script is located)
USER_NAME=$(whoami)
BRIX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Climate Monitor Setup ==="
echo "User name: $USER_NAME  Server directory: $BRIX_DIR"
echo ""

# update system
sudo apt update && sudo apt upgrade -y

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# build uv environment
uv python install 3.13
cd "$BRIX_DIR"
uv init
