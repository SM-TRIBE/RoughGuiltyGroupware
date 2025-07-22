# This script will be executed by Render to build your service.

# Exit on any error
set -o errexit

echo "==> Installing Rust toolchain..."
# Install the Rust compiler and its package manager, Cargo.
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add the Rust toolchain to the system's PATH for this build.
export PATH="$HOME/.cargo/bin:$PATH"
echo "==> Rust toolchain installed."

echo "==> Installing Python dependencies..."
# Now, install the Python packages. pip can now compile the Rust-based dependency.
pip install -r requirements.txt
echo "==> Python dependencies installed successfully."
