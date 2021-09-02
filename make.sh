#!/bin/bash

# ==================================================
# Created by: Andrew Dahms
# Created on: 08 June, 2021
#
# Usage: sh make.sh 1.0
# ==================================================

# Error handling
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
terminate()
{
    echo >&2 '
*** terminated ***
'
    echo "\"$last_command\" command failed with exit code $?."
    exit 1
}

trap 'terminate' 0

set -e

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

# Get HAML templates
mkdir PantheonCMD/haml

echo 'Getting HAML templates...'

svn checkout https://github.com/redhataccess/pantheon/trunk/pantheon-bundle/src/main/resources/apps/pantheon/templates/haml/html5 PantheonCMD/haml


# Get locales
mkdir PantheonCMD/locales

echo 'Getting locales...'

svn checkout https://github.com/asciidoctor/asciidoctor/trunk/data/locale PantheonCMD/locales

rm -rf PantheonCMD/{haml,locales}/.svn

# Replace remote CSS locations with local ones
sed -i 's/^-\ pantheonCssPath.*/-\ pantheonCssPath\ \=\ \"resources\/rhdocs.min.css\"/' PantheonCMD/haml/document.html.haml
sed -i 's/href\=\"https\:\/\/static\.redhat\.com\/libs\/redhat\/redhat-font\/2\/webfonts\/red-hat-font\.css/href\=\"resources\/red-hat-font.css/' PantheonCMD/haml/document.html.haml

# with find cp doesn't print 'omitting directory'
find PantheonCMD/* -maxdepth 0 -type f -exec cp {} PantheonCMD/pantheon-cmd-$1 \;
cp -r PantheonCMD/{haml,resources,locales} PantheonCMD/pantheon-cmd-$1

# Package sources ditectory
tar cvfz PantheonCMD/pantheon-cmd-$1.tar.gz -C PantheonCMD/ pantheon-cmd-$1

# Create rpmbuild dir and structure if it doesn't already exist
if [ ! -d "~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS}" ]; then
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS}
fi

# Move build files to the local build root
cp PantheonCMD/pantheon-cmd-$1.tar.gz ~/rpmbuild/SOURCES

cp build/pantheon-cmd.spec ~/rpmbuild/SPECS

# Build the package
rpmbuild -ba ~/rpmbuild/SPECS/pantheon-cmd.spec

rm -rf PantheonCMD/pantheon-cmd-$1*

# Retrieve package
cp ~/rpmbuild/RPMS/noarch/pantheon-cmd* build/

rm -rf PantheonCMD/haml
rm -rf PantheonCMD/locales

trap : 0

echo >&2 '
*** DONE ***
'
