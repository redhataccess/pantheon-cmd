#!/bin/bash

ROOT_REPO=$(git rev-parse --show-toplevel)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd $ROOT_REPO
if [ ! -f "build.yml" ]; then
        sh $SCRIPT_DIR/generate-build-yml.sh > build.yml
        echo "build.yml succsessfully generated";
    else
        read -p "build.yml already exists. Do you want to overwrite it? [y/N] " yn
        case $yn in
            [Yy]*)
            sh $SCRIPT_DIR/generate-build-yml.sh > build.yml && echo "build.yml succsessfully generated"; exit;;
            [Nn]*)
            echo "exiting..."; exit;;
            *)
    esac
fi
