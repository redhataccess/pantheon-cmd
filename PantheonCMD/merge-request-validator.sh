#!/bin/bash

# find if the target branch is master or main
master_main=$(git rev-parse --abbrev-ref origin/HEAD | cut -d/ -f2)

# find current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# find the changed files between master and current branch
changed_files=$(git diff --diff-filter=ACM --name-only "$master_main"..."$current_branch" -- '*.adoc' ':!*master.adoc')

# some error handlin for when the files are present on PR but not in local repo
for file in $changed_files; do
    if [ ! -f "$file" ]; then
        echo "$file exist in the remote repository but is not present in your local repository. Please commit and push your local changes and try again."
        exit 1
    fi
done

# collect assemblies with prefix in the name
prefix_assemblies=$(echo "$changed_files" | tr ' ' '\n' | grep -e '.*/\(assembly\).*\.adoc')

# collect modules with prefix in the name
prefix_modules=$(echo "$changed_files" | tr ' ' '\n' | grep -e '.*/\(proc\|con\|ref\).*\.adoc')

# collect files with no prefix in the name
no_prefix_files=$(echo "$changed_files" | tr ' ' '\n' | grep -ve '.*/\(proc\|con\|ref\|assembly\).*\.adoc')

# get rid of the comments
function erase_comments {
    filenames="$1"
    sed -re "\|^////|,\|^////|d" "$1" | sed -re "\|^//.*$|d"
}

export -f erase_comments

# if there are files with no prefix
if [ ! -z "$no_prefix_files" ]; then
    # check if files have a module type tag and classify those as modules
    no_prefix_modules=$(echo -e "$no_prefix_files" | xargs -P 0 -I %% bash -c 'erase_comments "%%" | grep -q ":_module-type: \(PROCEDURE\|CONCEPT\|REFERENCE\)" && echo "%%"')

    # collect files with no module type tag
    no_moudle_type_files=$(echo -e "$no_prefix_files" | xargs -P 0 -I %% bash -c 'erase_comments "%%" | grep -q ":_module-type: \(PROCEDURE\|CONCEPT\|REFERENCE\)" || echo "%%"')

    # check if files with no module type tag have includes and classify those as assemblies
    no_prefix_assemblies=$(echo -e "$no_moudle_type_files" | xargs -P 0 -I %% bash -c 'erase_comments "%%" | grep -q "^include::.*\.adoc.*\]" && echo "%%"')

    # collect files that have no module type tag or includes and classify those as undetermined file type
    undetermined_file_type=$(echo -e "$no_prefix_files" | xargs -P 0 -I %% bash -c 'erase_comments "%%" | grep -qE ":_module-type: \(PROCEDURE\|CONCEPT\|REFERENCE\)|^include::.*\.adoc.*\]" || echo "%%"')
fi

# concatenate assemblies with and without prefix
if [ ! -z "$prefix_assemblies" ] || [ ! -z "$no_prefix_assemblies" ]; then
    all_assemblies="${prefix_assemblies} ${no_prefix_assemblies}"
elif [ -z "$prefix_assemblies" ] || [ ! -z "$no_prefix_assemblies"]; then
    all_assemblies=$no_prefix_assemblies
elif [ ! -z "$prefix_assemblies" ] || [ -z "$no_prefix_assemblies"]; then
    all_assemblies=$prefix_assemblies
fi

# concatenate modules with and without prefix
if [ ! -z "$prefix_modules" ] || [ ! -z "$no_prefix_modules" ]; then
    all_modules="${prefix_modules} ${no_prefix_modules}"
elif [ -z "$prefix_modules" ] || [ ! -z "$no_prefix_modules" ]; then
    all_modules=$no_prefix_modules
elif [ ! -z "$prefix_modules" ] || [ -z "$no_prefix_modules" ]; then
    all_modules=$prefix_modules
fi

# echo all variables to get rid of weird spacing from concatenation
changed_files=$(echo $changed_files)
all_assemblies=$(echo $all_assemblies)
all_modules=$(echo $all_modules)
undetermined_file_type=$(echo $undetermined_file_type)

# export variables
export changed_files
export all_assemblies
export all_modules
export undetermined_file_type

# determine path to script
script=`realpath $0`
path_to_script=`dirname $script`

# call python wrapper for validation
python $path_to_script/mr-validate-wrapper.py
