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


def build_content(content_files, lang, repo_location, yaml_file_location):
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
            with open(attributes_file_location,'r') as attributes_file:
                attributes = attributes_file.read()
            break

    try:
        pool = concurrent.futures.ThreadPoolExecutor()
        futures = []
        for content_file in content_files:
            futures.append(pool.submit(process_file, content_file, attributes, lang, content_count))

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


def coalesce_document(main_file, attributes=None):
    """Combines the content from includes into a single, contiguous source file."""
    attributes = attributes or {}
    lines = []

    # Open the file, iterate over lines
    if os.path.exists(main_file):
        with open(main_file) as input_file:
            for line in input_file:
                # Process comments
                if line.startswith('//'):
                    continue
                # Process includes - recusrive
                if line.startswith("include::"):
                    include_file = line.replace("include::", "").split("[")[0]
                    # Replace attributes in includes, if already detected
                    if re.match(r'^\{\S+\}.*', include_file):
                        attribute = re.search(r'\{(.*?)\}',include_file).group(1)
                        if attribute in attributes.keys():
                            include_file = include_file.replace('{' + attribute + '}',attributes[attribute])
                    include_filepath = os.path.join(os.path.dirname(main_file), include_file)
                    lines.extend(coalesce_document(include_filepath,attributes))
                # Build dictionary of found attributes
                elif re.match(r'^:\S+:.*', line):
                    attribute_name = line.split(":")[1].strip()
                    attribute_value = line.split(":")[2].strip()
                    attributes[attribute_name] = attribute_value
                    lines.append(line)
                else:
                    lines.append(line)
    return lines


def process_file(file_name, attributes, lang, content_count):
    """Coalesces files and builds them using an AsciiDoctor sub-process."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    global current_count

    with lock:
        current_count += 1

        print('\033[1mBuilding {0:d}/{1:d}:\033[0m {2:s}'.format(current_count, content_count, file_name))

    # Create a temporary copy of the file, inject the attributes, and write content
    with open(file_name + '.tmp', 'w') as output_file:
        output_file.write(attributes + '\n\n')
        if lang:
            if lang == 'ja-JP':
                output_file.write('include::' + script_dir + '/locales/attributes-ja.adoc[]\n\n')

        coalesced_content = ''.join(coalesce_document(file_name))
        coalesced_content = re.sub(r'\n\s*\n', '\n\n', coalesced_content)

        regex_images = 'image:(:?)(.*?)\/([a-zA-Z0-9_-]+)\.(.*?)\['

        output_file.write(re.sub(regex_images, r'image:\1\3.\4[', coalesced_content))

    # Run AsciiDoctor on the temporary copy
    if lang and lang == 'ja-JP':
        cmd = ('asciidoctor -a toc! -a imagesdir=images -a lang=ja -T ' + script_dir + '/haml/ -E haml ' + file_name + '.tmp').split()
    else:
        cmd = ('asciidoctor -a toc! -a imagesdir=images -T ' + script_dir + '/haml/ -E haml ' + file_name + '.tmp').split()

    output_format = 'html'

    if output_format = 'pdf':

        cmd = ('asciidoctor-pdf -a pdf-themesdir=' + script_dir + '/templates/ -a pdf-theme=' script_dir + '/templates/red-hat.yml -a pdf-fontsdir=' + script_dir + '/fonts' + ' ' + file_name).split()

    # Build the content using AsciiDoctor
    output = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    # Delete the temporary copy
    os.remove(file_name + '.tmp')

    # Move the output file to the build directory
    shutil.move(file_name.replace('.adoc', '.adoc.html'),'build/' + os.path.split(file_name)[1].replace('.adoc', '.html'))
