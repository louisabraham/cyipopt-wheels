#!/bin/bash
# Compiles Ipopt and its dependencies (MUMPS + OpenBLAS) for manylinux wheel builds.
# This script is intended to run inside a manylinux_2_28 container.
set -eu

# Install efficient BLAS & LAPACK library
yum install -y openblas-devel

pushd /tmp

# MUMPS (Linear solver used by Ipopt)
git clone https://github.com/coin-or-tools/ThirdParty-Mumps --depth=1 --branch releases/3.0.4
pushd ThirdParty-Mumps
sh get.Mumps
./configure --with-lapack="-L/usr/include/openblas -lopenblas"
make
make install
popd

# Ipopt (The solver itself)
git clone https://github.com/coin-or/Ipopt --depth=1 --branch releases/3.14.11
pushd Ipopt
./configure --with-lapack="-L/usr/include/openblas -lopenblas"
make
make install
popd

popd

ldconfig
