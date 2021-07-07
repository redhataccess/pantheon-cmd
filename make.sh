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

# Get HAML templates
mkdir PantheonCMD/haml

echo 'Getting remote resources...'

for FILE in block_admonition.html.haml block_image.html.haml block_page_break.html.haml block_stem.html.haml block_video.html.haml inline_button.html.haml inline_menu.html.haml block_audio.html.haml block_listing.html.haml block_paragraph.html.haml block_table.html.haml document.html.haml inline_callout.html.haml inline_quoted.html.haml block_colist.html.haml block_literal.html.haml block_pass.html.haml block_thematic_break.html.haml embedded.html.haml inline_footnote.html.haml section.html.haml block_dlist.html.haml block_olist.html.haml block_preamble.html.haml block_toc.html.haml helpers.rb inline_image.html.haml block_example.haml.haml block_open.html.haml block_quote.html.haml block_ulist.html.haml inline_anchor.html.haml inline_indexterm.html.haml block_floating_title.html.haml block_outline.html.haml block_sidebar.html.haml block_verse.html.haml inline_break.html.haml inline_kbd.html.haml
do
  echo Getting $FILE...
  curl https://raw.githubusercontent.com/redhataccess/pantheon/master/pantheon-bundle/src/main/resources/apps/pantheon/templates/haml/html5/$FILE -o PantheonCMD/haml/$FILE -s > /dev/null
done

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

# Remove temporary HAML files
rm -rf PantheonCMD/haml
