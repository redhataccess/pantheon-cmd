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
All additions and updates to the script are welcome.

## Packaging the Script
After you update the manifest updater and test the changes, you can build an RPM-based package for the script so that it can be installed on systems that use *yum* or *dnf*.

1. Install the `svn` and `rpmbuild` packages installed on your system:
   ```shell
   # on RHEL
   $ sudo yum install subversion
   $ sudo yum install rpm-build

   # on Fedora
   $ sudo dnf install subversion
   $ sudo dnf install rpm-build
   ```  
2. Open *./build/pantheon-cmd.spec*.
3. Increment the value of the *Release* number.
4. Run the build script:
   ```shell
   $ sh make.sh 1.0
   ```

## Installing the script
Install the RPM and all Ruby gem dependencies.

1. Install the RPM:
   ```shell
   $ sudo dnf localinstall build/pantheon-cmd-1.0-X.el8.noarch.rpm
   ```
2. Install Ruby gem dependencies:
   ```shell
   $ sudo gem install asciidoctor concurrent-ruby haml tilt
   ```

The script is installed on your local machine.
The script provides the `pcmd` command.
Enter `pcmd -h` in your terminal to view the basic usage instructions.

## Licenscing

This script uses locale attributes files from the AsciiDoctor repository.

For more information, see https://github.com/asciidoctor/asciidoctor/tree/master/data/locale
