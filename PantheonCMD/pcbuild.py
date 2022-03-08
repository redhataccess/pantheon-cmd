#!/usr/bin/python3

import concurrent.futures
import glob
import os
import re
import shutil
import subprocess
import threading
import yaml

lock = threading.Lock()

current_count = 0


def build_content(content_files, lang, output_format, repo_location, yaml_file_location):
    """Attempts to build all specified files."""
    content_count = len(content_files)
    global current_count

    current_count = 0

    # Parse the main YAML file
    with open(yaml_file_location, 'r') as f:
        main_yaml_file = yaml.safe_load(f)

    for item, members in main_yaml_file.items():
        if item == 'variants':
            attributes_file_location = repo_location + members[0]["path"]
            attributes, lines = coalesce_document(attributes_file_location)
            break
    try:
        pool = concurrent.futures.ThreadPoolExecutor()
        futures = []
        for content_file in content_files:
            futures.append(pool.submit(process_file, content_file, attributes, lang, output_format, content_count))

        pool.shutdown(wait=True)
    except KeyboardInterrupt:
        print("\nShutting down...\n")

        # Cancel pending futures
        for future in futures:
            if not future.running():
                future.cancel()
        return False

    print()

    return True


def copy_resources(resources):
    """Copy resources such as images and files to the build directory."""
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Copy resources
    for resource in resources:
        if resource.endswith(('jpg', 'jpeg', 'png', 'svg')):
            shutil.copy(resource, 'build/images/')
        else:
            if not os.path.exists('build/files'):
                os.makedirs('build/files')
            shutil.copy(resource, 'build/files/')

    # Copy styling resources
    shutil.copytree(script_dir + '/resources', 'build/resources')


def prepare_build_directory():
    """Removes any existing 'build' directory and creates the directory structure required."""

    # Remove build directory if it exists
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Create a build directory
    os.makedirs('build')
    os.makedirs('build/images')


def resolve_attribute_tree(content, attributes):
    """Attempt to recursively resolve AsciiDoc attributes into a string."""

    continue_processing = True

    while continue_processing:
        if re.match(r'.*\{\S+\}.*', content):
            for attribute in re.search(r'\{(.*?)\}', content).groups():
                if attribute in attributes.keys():
                    content = content.replace('{' + attribute + '}',attributes[attribute])
                else:
                    continue_processing = False
        else:
            continue_processing = False
    return content


def coalesce_document(main_file, attributes=None, depth=0, top_level=True):
    """Combines the content from includes into a single, contiguous source file."""
    attributes = attributes or {}
    comment_block = False
    condition_block = False
    conditions_set = ''
    lines = []
    
    # Create a copy of global attributes
    if top_level:
        attributes_global = attributes.copy()

    # Open the file, iterate over lines
    if os.path.exists(main_file):

        with open(main_file) as input_file:

            # Iterate over content
            for line in input_file:

                # CONDITIONS

                # Line matches the end of a condition_block
                matches = re.match(r'^endif::(.*?)\[\]', line)

                if matches:
                    if matches.group(1) == conditions_set:
                            conditions_set = ''
                            condition_block = False
                    continue

                # Line matches the middle of a condition block
                if condition_block:
                    continue

                # Line matches the start of an ifdef condition
                matches = re.match(r'^ifdef::(\S+)\[(.*?)\]', line)

                if matches:
                    conditions_missing = False
                    conditions = matches.group(1)
                    conditions_set = matches.group(1)

                    # Multiple conditions - single match is enough
                    if conditions.__contains__('+'):
                        conditions_list = conditions.split('+')
                        for condition in conditions_list:
                            if not condition in attributes.keys():
                                conditions_missing = True
                                break

                    # Multiple conditions - all must match
                    elif conditions.__contains__(','):
                        conditions_missing = False
                        conditions_list = conditions.split(',')
                        for condition in conditions_list:
                            if not condition in attributes.keys():
                                conditions_missing = True
                            else:
                                conditions_missing = True
                        if conditions_missing:
                            conditions_missing = False

                    # Single condition
                    elif not conditions in attributes.keys():
                        conditions_missing = True

                    if conditions_missing:
                        if matches.group(2).strip() == '':
                            condition_block = True
                    else:
                        if matches.group(2).strip() != '':
                            lines.append(matches.group(2).strip() + '\n')
                    continue

                # Line matches the start of an ifndef condition
                matches = re.match(r'^ifndef::(\S+)\[(.*?)\]', line)

                if matches:
                    conditions_missing = False
                    conditions = matches.group(1)
                    conditions_set = matches.group(1)

                    # Multiple conditions - single match is enough
                    if conditions.__contains__(','):
                        conditions_list = conditions.split(',')
                        for condition in conditions_list:
                            if condition in attributes.keys():
                                conditions_missing = True
                                break

                    # Multiple conditions - all must match
                    elif conditions.__contains__('+'):
                        conditions_missing = False
                        conditions_list = conditions.split('+')
                        for condition in conditions_list:
                            if condition in attributes.keys():
                                conditions_missing = True
                            else:
                                conditions_missing = True
                        if conditions_missing:
                            conditions_missing = False

                    # Single condition
                    elif conditions in attributes.keys():
                        conditions_missing = True

                    if conditions_missing:
                        if matches.group(2).strip() == '':
                            condition_block = True
                    else:
                        if matches.group(2).strip() != '':
                            lines.append(matches.group(2).strip() + '\n')
                    continue

                # COMMENTS

                # Line matches comment block start or finish
                if re.match(r'^////.*', line.strip()):
                    comment_block = True if not comment_block else False
                    continue

                # Line matches the middle of a comment block
                elif comment_block:
                    continue

                # Line matches an inline comment
                elif re.match(r'^//.*', line.strip()):
                    continue

                # OTHER CONDITIONS

                # Line matches a section header; adjust depth
                elif re.match(r'^=+ \S+', line.strip()):
                    if depth > 0:
                        lines.append(('=' * depth) + line.strip() + '\n')
                    else:
                        lines.append(line.strip() + '\n')

                # Line matches an include; process recusrively
                elif re.match(r'^include::.*', line.strip()):
                    include_depth = 0
                    include_file = line.replace("include::", "").split("[")[0]
                    include_options = line.split("[")[1].split("]")[0].split(',')
                    for include_option in include_options:
                        if include_option.__contains__("leveloffset=+"):
                            include_depth += int(include_option.split("+")[1])
                    # Replace attributes in includes, if their values are defined
                    if re.match(r'.*\{\S+\}.*', include_file):
                        include_file = resolve_attribute_tree(include_file, attributes)
                    include_filepath = os.path.join(os.path.dirname(main_file), include_file)
                    attributes, include_lines = coalesce_document(include_filepath, attributes, include_depth, False)
                    lines.extend(include_lines)

                # Line matches an attribute declaration
                elif re.match(r'^:\S+:.*', line):
                    attribute_name = line.split(":")[1].strip()
                    attribute_value = line.split(":")[2].strip()
                    if attribute_name != 'context':
                        attributes[attribute_name] = attribute_value
                    lines.append(line)
                else:
                    lines.append(line)

            # Add global attribute definitions if main file
            if top_level:
                lines.insert(0,'\n\n')
                for attribute in sorted(attributes_global.keys(),reverse=True):
                    lines.insert(0,':' + attribute + ': ' + attributes_global[attribute] + '\n')
                lines.insert(0,'// Global attributes\n')

    return attributes, lines


def process_file(file_name, attributes, lang, output_format, content_count):
    """Coalesces files and builds them using an AsciiDoctor sub-process."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    global current_count

    with lock:
        current_count += 1

        print('\033[1mBuilding {0:d}/{1:d}:\033[0m {2:s}'.format(current_count, content_count, file_name))

    # Create a temporary copy of the file, inject the attributes, and write content
    with open(file_name + '.tmp', 'w') as output_file:
        if lang:
            if lang.lower() == 'ja-JP':
                output_file.write('include::' + script_dir + '/locales/attributes-ja.adoc[]\n\n')

        # Coalesce document
        coalesced_attributes, coalesced_content = coalesce_document(file_name, attributes, 0, True)

        coalesced_content = ''.join(coalesced_content)
        coalesced_content = re.sub(r'\n\s*\n', '\n\n', coalesced_content)

        # Standardize image references
        regex_images = 'image:(:?)(.*?)\/([a-zA-Z0-9_-]+)\.(.*?)\['

        output_file.write(re.sub(regex_images, r'image:\1\3.\4[', coalesced_content))

    # Resolve language
    language_code = ''

    if lang:
        if lang.lower() == 'ja-jp':
            language_code = '-a lang=ja'

    # Run AsciiDoctor on the temporary copy
    if output_format == 'pdf':
        cmd = ('asciidoctor-pdf ' + language_code + ' -a pdf-themesdir=' + script_dir + '/templates/ -a pdf-theme=' + script_dir + '/templates/red-hat.yml -a pdf-fontsdir=' + script_dir + '/fonts' + ' ' + file_name + '.tmp').split()
    else:
        cmd = ('asciidoctor -a toc! ' + language_code + ' -a imagesdir=images -T ' + script_dir + '/haml/ -E haml ' + file_name + '.tmp').split()

    # Build the content using AsciiDoctor
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Delete the temporary copy
    os.remove(file_name + '.tmp')

    # Move the output file to the build directory
    if output_format == 'pdf':
        file_extension = '.pdf'
    else:
        file_extension = '.html'

    shutil.move(file_name.replace('.adoc', '.adoc' + file_extension),'build/' + os.path.split(file_name)[1].replace('.adoc', file_extension))
