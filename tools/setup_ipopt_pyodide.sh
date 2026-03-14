#!/bin/bash
# Downloads pre-built wasm32 Ipopt libraries and headers for Pyodide builds.
# Libraries from https://louisabraham.github.io/ipopt-wasm/
set -eu

INSTALL_DIR="/tmp/ipopt_wasm"
IPOPT_VERSION="3.14.19"
BASE_URL="https://louisabraham.github.io/ipopt-wasm"
IPOPT_RAW="https://raw.githubusercontent.com/coin-or/Ipopt/releases/$IPOPT_VERSION"

mkdir -p "$INSTALL_DIR/lib" "$INSTALL_DIR/include/coin-or" "$INSTALL_DIR/lib/pkgconfig"

# Download pre-built wasm32 static libraries
for lib in libipopt.a libmumps.a liblapack.a libflangrt.a; do
    curl -sfL "$BASE_URL/$lib" -o "$INSTALL_DIR/lib/$lib"
done

# Download wasm32 ABI bridges (compiled during build via before-build)
curl -sfL "$BASE_URL/wasm32_bridges.c" -o "$INSTALL_DIR/lib/wasm32_bridges.c"

# Download Ipopt C interface headers
for header in IpStdCInterface.h IpReturnCodes.h IpReturnCodes_inc.h; do
    curl -sfL "$IPOPT_RAW/src/Interfaces/$header" -o "$INSTALL_DIR/include/coin-or/$header"
done
for header in IpoptConfig.h IpTypes.h config_ipopt_default.h; do
    curl -sfL "$IPOPT_RAW/src/Common/$header" -o "$INSTALL_DIR/include/coin-or/$header"
done

# Create pkg-config file
cat > "$INSTALL_DIR/lib/pkgconfig/ipopt.pc" << EOF
prefix=$INSTALL_DIR
libdir=\${prefix}/lib
includedir=\${prefix}/include/coin-or

Name: ipopt
Description: Ipopt (wasm32, pre-built from ipopt-wasm)
Version: $IPOPT_VERSION
Libs: -L\${libdir} \${libdir}/wasm32_bridges.o -lipopt -lmumps -llapack -lflangrt
Cflags: -I\${includedir}
EOF

echo "Ipopt wasm32 libraries installed to $INSTALL_DIR"
