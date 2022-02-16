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

# install required packages
echo 'Installing package dependencies...'
sudo dnf install python3 ruby subversion rpm-build

echo 'Installing ruby gem dependencies...'
sudo gem install asciidoctor concurrent-ruby haml tilt
# do we still need pygit2?
pip3 install pygit2

echo 'Creating resources directories...'
for dir in "PantheonCMD/haml" "PantheonCMD/locales"; do if [ ! -d "$dir" ]; then mkdir $dir; fi; done

echo 'Getting HAML templates...'
svn checkout https://github.com/redhataccess/pantheon/trunk/pantheon-bundle/src/main/resources/apps/pantheon/templates/haml/html5 PantheonCMD/haml

echo 'Getting locales...'
svn checkout https://github.com/asciidoctor/asciidoctor/trunk/data/locale PantheonCMD/locales
rm -rf PantheonCMD/{haml,locales}/.svn

echo 'Updating styling references...'
sed -i 's/^-\ pantheonCssPath.*/-\ pantheonCssPath\ \=\ \"resources\/rhdocs.min.css\"/' PantheonCMD/haml/document.html.haml
sed -i 's/href\=\"https\:\/\/static\.redhat\.com\/libs\/redhat\/redhat-font\/2\/webfonts\/red-hat-font\.css/href\=\"resources\/red-hat-font.css/' PantheonCMD/haml/document.html.haml

echo 'Copying the source files to the local binaries directory...'
sudo cp -r PantheonCMD /usr/local/bin

# do we need to account for different shells?
# exit code is 0 so setting +e
echo 'Adding an alias to the current shell...'
if [[ $SHELL = '/bin/bash' ]]; then
    set +e && alias pcmd='/usr/bin/python3 /usr/local/bin/PantheonCMD/pcmd.py $@' && source ~/.bashrc
elif [[ $SHELL = '/bin/tcsh' ]]; then
    set +e && alias pcmd '/usr/bin/python3 /usr/local/bin/PantheonCMD/pcmd.py $@' && source ~/.tcshrc
elif [[ $SHELL = '/bin/csh' ]]; then
    set +e && alias pcmd '/usr/bin/python3 /usr/local/bin/PantheonCMD/pcmd.py $@' && source ~/.cshrc
fi

rm -rf PantheonCMD/{haml,locales}

trap : 0

echo >&2 '
*** DONE ***
'
