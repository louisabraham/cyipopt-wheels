#!/bin/bash
# Installs Ipopt via conda-forge (Miniforge) for macOS wheel builds.
# Installs to /tmp/ipopt_conda so pkg-config and delocate can find the libraries.
set -eu

INSTALL_DIR="/tmp/ipopt_conda"

# Download and install Miniforge
curl -L -o /tmp/miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh
bash /tmp/miniforge.sh -b -p "$INSTALL_DIR"

# Install ipopt and pkg-config
"$INSTALL_DIR/bin/conda" install -y -p "$INSTALL_DIR" ipopt pkg-config
