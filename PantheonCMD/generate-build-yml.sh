#!/bin/bash

#define parameters
repo_name=$(basename $PWD)

#define the template
cat  << EOF
# Your repository name goes here
repository: $repo_name
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
