#!/bin/bash

ROOT_REPO=$(git rev-parse --show-toplevel)
SCRIPT_DIR=$(realpath $(dirname "$0"))
REPO_NAME=$(basename $ROOT_REPO)

if [[ -f "$ROOT_REPO/build.yml" ]]; then
    read -p "build.yml already exists. Do you want to overwrite it? [y/N] " -n 1
    echo
    if [[ ! "$REPLY" =~ ^[yY]$ ]]; then
      exit
    fi
fi

cat >$ROOT_REPO/build.yml << EOF
# Your repository name goes here
repository: $REPO_NAME
variants:
  # Your variant name goes here
  - name: PLACEHOLDER
    # Path to your attributes file goes here
    attributes:
      - PATH/TO/_attributes.adoc
    nav: PATH/TO/nav.yml
    build: true
    files:
      # Path to your assemblies, modules, and images go here
      included:
        - PATH/TO/ASSEMBLIES/*.adoc
        - PATH/TO/MODULES/**/*.adoc
        - PATH/TO/images/*.png

EOF

echo "build.yml successfully generated"
