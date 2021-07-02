#!/usr/libexec/platform-python

import os
import glob
import pcutil
import re
import shutil
import sys
import yaml

# Get the directory where the script is installed; use to find resources
script_dir = os.path.dirname(os.path.realpath(__file__))


# Process files
def process_file(name, main_attributes_file, lang):

    global script_dir

    # Create a temporary copy of the file, inject the attributes, and write content
    with open(name + '.tmp', 'w') as output_file:

        output_file.write('include::' + main_attributes_file + '[]\n\n')

        if lang:

            if lang == 'ja-JP':

                output_file.write('include::' + script_dir + '/locales/attributes-ja.adoc[]\n\n')

        coalesced_content = os.popen('ruby ' + script_dir + '/utils/asciidoc-coalescer.rb ' + name).read()

        regex_images = 'image:(:?)(.*?)\/([a-zA-Z0-9_-]+)\.(.*?)\['

        output_file.write(re.sub(regex_images,r'image:\1\3.\4[',coalesced_content))

    # Run AsciiDoctor on the temporary copy
    if lang:

        if lang == 'ja-JP':

            os.system('asciidoctor -a imagesdir=images -a lang=ja -T ' + script_dir + '/haml/html5/ -E haml ' + name + '.tmp')

    else:

        os.system('asciidoctor -a imagesdir=images -T ' + script_dir + '/haml/html5/ -E haml ' + name + '.tmp')

    shutil.move(name.replace('.adoc', '.adoc.html'),'build/' + os.path.split(name)[1].replace('.adoc', '.html'))

    # Delete the temporary copy
    os.remove(name + '.tmp')    


# Attempt to build all files in the pantheon2.yml file
def build_all(lang):

    yaml_file_location = pcutil.get_yaml_file()

    content_counts = pcutil.count_content(yaml_file_location)

    global script_dir

    main_attributes_file = ''

    # Remove build directory if it exists
    if os.path.exists('build'):

        shutil.rmtree('build')

    # Parse the main YAML file
    with open(yaml_file_location + 'pantheon2.yml', 'r') as f:

        main_yaml_file = yaml.load(f)

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

    for item, docc in main_yaml_file.items():

        if item == 'variants':

            main_attributes_file = yaml_file_location + docc[0]["path"]

    print("Building assemblies:\n")

    current_assembly_count = 1

    for assembly in main_yaml_file["assemblies"]:

        for name in glob.glob(assembly):

            print('\033[1mBuilding {0:d}/{1:d}:\033[0m {2:s}...'.format(current_assembly_count,content_counts['assemblies'],name))

            process_file(name, main_attributes_file, lang)

            current_assembly_count += 1

    print()

    print("Building modules:\n")

    current_module_count = 1

    for module in main_yaml_file["modules"]:

        for name in glob.glob(module):

            print('\033[1mBuilding {0:d}/{1:d}:\033[0m {2:s}...'.format(current_module_count,content_counts['modules'],name))

            process_file(name, main_attributes_file, lang)

            current_module_count += 1


# Attempt to build only those files specified as an argument on the command line
def build_subset(files,lang):

    yaml_file_location = pcutil.get_yaml_file()

    global script_dir

    target_files = glob.glob(files)
    total_files = len(target_files)
    current_count = 1

    # Remove build directory if it exists
    if os.path.exists('build'):

        shutil.rmtree('build')

    # Parse the main YAML file
    with open(yaml_file_location + 'pantheon2.yml', 'r') as f:

        main_yaml_file = yaml.load(f)

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

    for item, docc in main_yaml_file.items():

        if item == 'variants':

            main_attributes_file = yaml_file_location + docc[0]["path"]

    # Attempt to build specified files
    for target_file in target_files:

        print('\033[1mBuilding {0:d}/{1:d}:\033[0m {2:s}...'.format(current_count,total_files,target_file))

        if not target_file.endswith('adoc'):

            print ("Not an AsciiDoc file; skipping...")

            current_count += 1

            continue

        elif not os.path.exists(target_file):

            print ("File does not exist; skipping...")

            current_count += 1

            continue

        else:

            process_file(target_file, main_attributes_file, lang)

        current_count += 1
