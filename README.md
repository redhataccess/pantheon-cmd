# Pantheon CMD

Pantheon CMD is a Python-based command-line tool that allows you to generate a rendered preview of modular documentation using the new HAML templates.

## Directory Structure

The top level of this repository contains the following files and directories:

**build**
A directory that contains the latest RPM for the script, and the SPEC file used to generate the RPM.

**make.sh**
A script used to package the script as an RPM-based package that can be installed using *yum* or *dnf*.

**PantheonCMD**
A directory containing the source files for the script, and the man page file.

## Updating the Script
All additions and updates to the script are welcome. The following section outlines some of the common updates that may be required to enhance support for new product versions.

## Packaging the Script
After you update the manifest updater and test the changes, you can build an RPM-based package for the script so that it can be installed on systems that use *yum* or *dnf*.

1. Open *./build/pantheon-cmd.spec*.
2. Increment the value of the *Release* number.
3. Run the build script:
   ```
   $ sh make.sh 1.0
   ```
4. Delete all previous versions of the package in the *build* directory.
5. Add the latest version of the package in the *build* directory:
   ```
   $ git add build/pantheon-cmd-1.0-XX.noarch.rpm
   ```
6. Commit the changes:
   ```
   $ git commit -m "<commit message>"
   ```
7. Push the changes back to GitLab:
   ```
   $ git push origin master
   ```

## Installing the script
Install the RPM and all Ruby gem dependencies.

1. Install the RPM:
   ```
   $ sudo dnf localinstall build/pantheon-cmd-1.0-X.el8.noarch.rpm
   ```
2. Install Ruby gem dependencies:
   ```
   $ sudo gem install asciidoctor concurrent-ruby haml tilt
   ```

The script is installed on your local machine.

## Licenscing

This script uses mojavelinux's AsciiDoc coalescer script from the AsciiDoctor extensions lab.

For more information, see https://github.com/asciidoctor/asciidoctor-extensions-lab/blob/master/scripts/asciidoc-coalescer.rb

This script uses locale attributes files from the AsciiDoctor repository.

For more information, see https://github.com/asciidoctor/asciidoctor/tree/master/data/locale
