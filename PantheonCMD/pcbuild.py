#!/usr/libexec/platform-python

import concurrent.futures
import glob
import os
import pcutil
import re
import shutil
import subprocess
import sys
import yaml
import time

current_count = 1


# Process files
def process_file(file_name, attributes_file_location, lang, content_count):

    script_dir = os.path.dirname(os.path.realpath(__file__))

    global current_count

    print('\033[1mBuilding {0:d}/{1:d}:\033[0m {2:s}'.format(current_count, content_count,file_name))

    current_count +=1

    # Create a temporary copy of the file, inject the attributes, and write content
    with open(file_name + '.tmp', 'w') as output_file:

        output_file.write('include::' + attributes_file_location + '[]\n\n')

        if lang:

            if lang == 'ja-JP':

                output_file.write('include::' + script_dir + '/locales/attributes-ja.adoc[]\n\n')

        coalesced_content = subprocess.run(['ruby', script_dir + '/utils/asciidoc-coalescer.rb', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        regex_images = 'image:(:?)(.*?)\/([a-zA-Z0-9_-]+)\.(.*?)\['

        output_file.write(re.sub(regex_images,r'image:\1\3.\4[',coalesced_content.stdout.decode('utf-8')))

    # Run AsciiDoctor on the temporary copy
    if lang and lang == 'ja-JP':

        cmd = ('asciidoctor -a imagesdir=images -a lang=ja -T ' + script_dir + '/haml/html5/ -E haml ' +  file_name + '.tmp').split()

    else:

        cmd = ('asciidoctor -a imagesdir=images -T ' + script_dir + '/haml/html5/ -E haml ' +  file_name + '.tmp').split()

    output = subprocess.run(cmd, stderr=subprocess.PIPE)

    if output.stderr: 
            
        print(output.stderr.decode('utf-8'))

    shutil.move(file_name.replace('.adoc', '.adoc.html'),'build/' + os.path.split(file_name)[1].replace('.adoc', '.html'))

    # Delete the temporary copy
    os.remove(file_name + '.tmp')    


# Attempt to build all files in the pantheon2.yml file
def build_content(content_files, yaml_file_location, lang):

    script_dir = os.path.dirname(os.path.realpath(__file__))

    content_count = len(content_files)

    # Parse the main YAML file
    with open(yaml_file_location + 'pantheon2.yml', 'r') as f:

        main_yaml_file = yaml.safe_load(f)

    # Remove build directory if it exists
    if os.path.exists('build'):

        shutil.rmtree('build')

    # Create a build directory
    os.makedirs('build')

    os.makedirs('build/images')

    # Copy resources
    for resource in main_yaml_file["resources"]:

        for name in glob.glob(resource):

            if name.endswith(('jpg','jpeg','png','svg')):

                shutil.copy(name, 'build/images/')

            else:

                shutil.copy(name, 'build/')

    # Copy styling resources
    shutil.copytree(script_dir + '/resources', 'build/resources')

    for item, members in main_yaml_file.items():

        if item == 'variants':

            attributes_file_location = yaml_file_location + members[0]["path"]

            break

    with concurrent.futures.ThreadPoolExecutor() as pool:

        for content_file in content_files:

            pool.submit(process_file, content_file, attributes_file_location, lang, len(content_files))

    print()
