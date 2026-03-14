#!/bin/bash
# Appends bundled library licenses to the LICENSE file for binary wheel distributions.
set -eu

cd "$(dirname "$0")/.."

echo "------------------------------" >> LICENSE
echo "This binary distribution of cyipopt also bundles the following software" >> LICENSE
for bundled_license in licenses_manylinux_bundled_libraries/*.txt; do
    cat "$bundled_license" >> LICENSE
done
