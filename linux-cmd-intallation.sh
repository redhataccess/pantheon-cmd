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

# clone repo

# install required packages
sudo dnf install subversion
sudo dnf install rpm-build


if [[ $(basename "$PWD") = "pantheon-cmd" ]]; then
    release_number=$(grep -o -P '(?<=Release:   ).*(?=%{)' build/pantheon-cmd.spec)
    incremented_release_number=$((release_number+1))
else
    echo "Navigate to the pantheon-cmd directory."
    exit 2
fi

sh make.sh $incremented_release_number

# install dependencies
sudo gem install asciidoctor concurrent-ruby haml tilt

sudo dnf install build/pantheon-cmd-*.noarch.rpm

trap : 0

echo >&2 '
*** DONE ***
'
