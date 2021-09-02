#!/bin/bash

# find if the target branch is master or main
master_main=$(git rev-parse --abbrev-ref origin/HEAD | cut -d/ -f2)

# find current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# find the changed files between master and current branch
changed_files=$(git diff --diff-filter=ACM --name-only "$master_main"..."$current_branch" -- '*.adoc')

prefix_assembly_files=$(echo "$changed_files" | tr ' ' '\n' | grep -e '.*/\(assembly\)_.*\.adoc' | tr '\n' ' ')

prefix_module_files=$(echo "$changed_files" | tr ' ' '\n' | grep -e '.*/\(proc\|con\|ref\)_.*\.adoc' | tr '\n' ' ')

no_prefix_files=$(echo "$changed_files" | tr ' ' '\n' | grep -ve '.*/\(proc\|con\|ref\|assembly\)_.*\.adoc' | tr '\n' ' ')

#remove comments?

if [ ! -z "$no_prefix_files" ]; then
    no_prefix_modules=$(echo $no_prefix_files | while read line; do grep -l ":_module-type:" $line; done )

    no_moudle_type_files=$(echo $no_prefix_files | while read line; do grep -HLE ":_module-type:" $line; done )

    no_prefix_assemblies=$(echo $no_moudle_type_files | while read line; do grep -l "^include::.*\.adoc.*\]" $line; done )

    undetermined_file_type=$(echo $no_prefix_files | while read line; do grep -HLE ":_module-type:|^include::.*\.adoc.*\]" $line; done )
fi

if [ ! -z "$prefix_assembly_files" ] || [ ! -z "$no_prefix_assemblies" ]; then
    all_assemblies="${prefix_assembly_files} ${no_prefix_assemblies}"
elif [ -z "$prefix_assembly_files" ] || [ ! -z "$no_prefix_assemblies"]; then
    all_assemblies=$no_prefix_assemblies
elif [ ! -z "$prefix_assembly_files" ] || [ -z "$no_prefix_assemblies"]; then
    all_assemblies=$prefix_assembly_files
fi

if [ ! -z "$prefix_module_files" ] || [ ! -z "$no_prefix_modules" ]; then
    all_modules="${prefix_module_files} ${no_prefix_modules}"
elif [ -z "$prefix_module_files" ] || [ ! -z "$no_prefix_modules" ]; then
    all_modules=$no_prefix_modules
elif [ ! -z "$prefix_module_files" ] || [ -z "$no_prefix_modules" ]; then
    all_modules=$prefix_module_files
fi
