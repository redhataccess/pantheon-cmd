#!/bin/bash

# ==================================================
# Created by: Andrew Dahms
# Created on: 08 June, 2021
#
# Usage: sh make.sh 1.0
# ==================================================

CURRENT_DIR=`pwd`

echo 'Building pantheon-cmd...'

# Check arguments
if [ -z "$1" ]; then
    echo 'No argument supplied!'
    exit 2
fi

# Create and populate sources directory
if [ ! -d "PantheonCMD/pantheon-cmd-$1" ]; then

    mkdir PantheonCMD/pantheon-cmd-$1

fi

cp PantheonCMD/* PantheonCMD/pantheon-cmd-$1
cp -r PantheonCMD/haml PantheonCMD/pantheon-cmd-$1
cp -r PantheonCMD/resources PantheonCMD/pantheon-cmd-$1
cp -r PantheonCMD/utils PantheonCMD/pantheon-cmd-$1
cp -r PantheonCMD/locales PantheonCMD/pantheon-cmd-$1

cd PantheonCMD

# Package sources ditectory
tar cvf pantheon-cmd-$1.tar pantheon-cmd-$1

gzip -f pantheon-cmd-$1.tar

cd ..

# Move build files to the local build root
cp PantheonCMD/pantheon-cmd-$1.tar.gz ~/rpmbuild/SOURCES
cp build/pantheon-cmd.spec ~/rpmbuild/SPECS

# Build the package
cd ~/rpmbuild/SPECS/

rpmbuild -ba pantheon-cmd.spec

# Return to PWD
cd $CURRENT_DIR

rm -rf PantheonCMD/pantheon-cmd-$1
rm PantheonCMD/pantheon-cmd-$1.tar.gz

# Retrieve package
cp ~/rpmbuild/RPMS/noarch/pantheon-cmd* build


