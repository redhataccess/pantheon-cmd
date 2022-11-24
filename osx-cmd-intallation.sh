#!/bin/bash

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

# Check if homebrew is installed
if [[ $(command -v brew) == "" ]]; then
    # Install Homebrew
    echo 'Installing Homebrew...'
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    :
fi

echo 'Installing package dependencies...'

brew install python3 ruby subversion

echo 'Installing ruby gem dependencies...'

sudo gem install asciidoctor concurrent-ruby haml tilt

pip3 install pygit2

echo 'Creating resources directories...'

# Create resource directories
mkdir PantheonCMD/{haml,locales}

# Get HAML templates
echo 'Getting HAML templates...'

svn checkout https://github.com/redhataccess/pantheon/trunk/pantheon-bundle/src/main/resources/apps/pantheon/templates/haml/html5 PantheonCMD/haml

# Get locales
echo 'Getting locales...'

svn checkout https://github.com/asciidoctor/asciidoctor/trunk/data/locale PantheonCMD/locales

rm -rf PantheonCMD/{haml,locales}/.svn

echo 'Updating styling references...'

# Replace remote CSS locations with local ones
sed -i '' 's/^-\ pantheonCssPath.*/-\ pantheonCssPath\ \=\ \"resources\/rhdocs.min.css\"/' PantheonCMD/haml/document.html.haml
sed -i '' 's/href\=\"https\:\/\/static\.redhat\.com\/libs\/redhat\/redhat-font\/2\/webfonts\/red-hat-font\.css/href\=\"resources\/red-hat-font.css/' PantheonCMD/haml/document.html.haml

echo 'Copying the source files to the local binaries directory...'

cp -r PantheonCMD /usr/local/bin

echo 'Adding an alias to ~/.zshrc file...'

alias pcmd="/usr/bin/python3 /usr/local/bin/PantheonCMD/pcmd.py $@"

echo 'Sourcing your ~/.zshrc file...'

source ~/.zshrc

trap : 0

echo >&2 '
*** DONE ***
'
