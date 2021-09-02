#!/bin/bash

# find if the target branch is master or main
master_main=$(git rev-parse --abbrev-ref origin/HEAD | cut -d/ -f2)

# find current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# find the changed files between master and current branch
changed_files=$(git diff --diff-filter=ACM --name-only "$master_main"..."$current_branch" -- '*.adoc')

prefix_assembly_files=$(echo "$changed_files" | grep "assembly_|assembly-")

prefix_module_files=$(echo "$changed_files" | grep -E "proc_|proc-|con_|con-|ref_|ref-")

no_prefix_files=$(echo "$changed_files" | tr ' ' '\n' | grep -ve '.*/\(proc\|con\|ref\|assembly\)_.*\.adoc' | tr '\n' ' ')

#remove comments?

if [ ! -z "$no_prefix_files" ]; then
    no_prefix_modules=$(echo $no_prefix_files | while read line; do grep -l ":_module-type:" $line; done )

    no_moudle_type_files=$(echo $no_prefix_files | while read line; do grep -HLE ":_module-type:" $line; done )

    no_prefix_assemblies=$(echo $no_moudle_type_files | while read line; do grep -l "^include::.*\.adoc.*\]" $line; done )

    undetermined_file_type=$(echo $no_prefix_files | while read line; do grep -HLE ":_module-type:|^include::.*\.adoc.*\]" $line; done )
    no_prefix_assemblies=
fi
