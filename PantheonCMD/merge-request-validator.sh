#!/bin/bash

# find if the target branch is master or main
master_main=$(git rev-parse --abbrev-ref origin/HEAD | cut -d/ -f2)

# find current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# find the changed files between master and current branch
changed_files=$(git diff --diff-filter=ACM --name-only "$master_main"..."$current_branch" -- '*.adoc')

prefix_assemblies=$(echo "$changed_files" | tr ' ' '\n' | grep -e '.*/\(assembly\).*\.adoc' | tr '\n' ' ')

prefix_modules=$(echo "$changed_files" | tr ' ' '\n' | grep -e '.*/\(proc\|con\|ref\).*\.adoc' | tr '\n' ' ')

no_prefix_files=$(echo "$changed_files" | tr ' ' '\n' | grep -ve '.*/\(proc\|con\|ref\|assembly\).*\.adoc' | tr '\n' ' ')

# Getting rid of the comments
function erase_comments {
    filenames="$1"
    sed -re "\|^////|,\|^////|d" "$1" | sed -re "\|^//.*$|d"
}

export -f erase_comments

#xargs -P 0 -I %% bash -c 'erase_comments "%%" | grep -q ":_module-type:" && echo "%%"' )

if [ ! -z "$no_prefix_files" ]; then
    no_prefix_modules=$(echo $no_prefix_files | while read line; do grep -l ":_module-type:" $line; done )

    no_moudle_type_files=$(echo $no_prefix_files | while read line; do grep -HLE ":_module-type:" $line; done )

    no_prefix_assemblies=$(echo $no_moudle_type_files | while read line; do grep -l "^include::.*\.adoc.*\]" $line; done )

    undetermined_file_type=$(echo $no_prefix_files | while read line; do grep -HLE ":_module-type:|^include::.*\.adoc.*\]" $line; done )
fi

if [ ! -z "$prefix_assemblies" ] || [ ! -z "$no_prefix_assemblies" ]; then
    all_assemblies="${prefix_assemblies} ${no_prefix_assemblies}"
elif [ -z "$prefix_assemblies" ] || [ ! -z "$no_prefix_assemblies"]; then
    all_assemblies=$no_prefix_assemblies
elif [ ! -z "$prefix_assemblies" ] || [ -z "$no_prefix_assemblies"]; then
    all_assemblies=$prefix_assemblies
fi

if [ ! -z "$prefix_modules" ] || [ ! -z "$no_prefix_modules" ]; then
    all_modules="${prefix_modules} ${no_prefix_modules}"
elif [ -z "$prefix_modules" ] || [ ! -z "$no_prefix_modules" ]; then
    all_modules=$no_prefix_modules
elif [ ! -z "$prefix_modules" ] || [ -z "$no_prefix_modules" ]; then
    all_modules=$prefix_modules
fi

changed_files=$(echo $changed_files)
all_assemblies=$(echo $all_assemblies)
all_modules=$(echo $all_modules)
undetermined_file_type=$(echo $undetermined_file_type)

export changed_files
export all_assemblies
export all_modules
export undetermined_file_type

script=`realpath $0`
path_to_script=`dirname $script`

python $path_to_script/mr-validate-wrapper.py
