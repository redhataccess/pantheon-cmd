#!/bin/bash

#define parameters
repo_name=$(basename $PWD)

find_images_dir=$(find . -type d -name "images")

#if images dir is detected record, otherwise create a placeholder
if [ ! -z "$find_images_dir" ]; then
    images_dir=$(for i in $find_images_dir; do echo "  - ${i/\.\/}/*.png" && echo "  - ${i/\.\/}/*.svg"; done)
else
    images_dir=$(printf '  - PATH/TO/YOUR/IMAGES/DIRECTORY/*.png\n  - PATH/TO/YOUR/IMAGES/DIRECTORY/*.svg')
fi

#define the template
cat  << EOF
server: https://pantheon.corp.redhat.com
# Your repository name goes here
repository: $repo_name
variants:
  # Your chosen name goes here
  - name: PLACEHOLDER
    # Path to your attributes file goes here
    path: PATH/TO/attributes.adoc
    canonical: true

assemblies:
    # Your assemblies go here
  - PATH/TO/ASSEMBLIES/assembly_TEMPLATE-ASSEMBLY.adoc


modules:
    # Your modules go here
  - PATH/TO/MODULES/con_TEMPLATE_CONCEPT.adoc
  - PATH/TO/MODULES/proc_TEMPLATE_PROCEDURE.adoc
  - PATH/TO/MODULES/ref_TEMPLATE_REFERENCE.adoc


resources:
  # Path to your images directory goes here
$images_dir
EOF
