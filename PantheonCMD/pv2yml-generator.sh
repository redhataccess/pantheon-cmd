#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# a simple yay/nay prompt for users
while true; do
    read -p "Are you at the root of your repository where you want to create a pantheo2.yml? [y/N] " yn
    case $yn in
        [Yy]*)
        read -p "Do you want to create the pantheon2.yml in $PWD directory? [y/N] " yn
        case $yn in
            [Yy]*)
            if [ ! -f "pantheon2.yml" ]; then
                sh $SCRIPT_DIR/generate-pv2-yml.sh > pantheon2.yml
                echo "pantheon2.yml succsessfully generated";
            else
                read -p "pantheon2.yml already exists. Do you want to overwrite it? [y/N] " yn
                case $yn in
                    [Yy]*)
                    sh $SCRIPT_DIR/generate-pv2-yml.sh > pantheon2.yml && echo "pantheon2.yml succsessfully generated"; exit;;
                    [Nn]*)
                    echo "exiting..."; exit;;
                    *)
                    echo "Please answer yes or no.";;
                esac
            fi
            exit;;
            [Nn]*)
            echo "exiting..."; exit;;
            *)
            echo "Please answer yes or no.";;
        esac;;
        [Nn]*)
        echo "Please navigate to the root of the repository where you want to create the pantheo2.yml."; exit;;
        *)
        echo "Please answer yes or no.";;
    esac
done
