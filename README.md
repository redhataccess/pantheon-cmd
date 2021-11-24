# Pantheon CMD

Pantheon CMD is a Python-based command-line tool that allows you to generate a rendered preview of modular documentation using the new HAML templates.

Installing Pantheon CMD using RPM allows you to perform actions using the predefined aliases such as: 
* `pcmd validate`
* `pcmd generate`
* `pcmd preview`

Alternatively, you can clone this repository and add the following `pcmd` scripts on $PATH, but the ability to use predefined aliases will not be possible.

## Directory Structure

The top level of this repository contains the following files and directories:

**build**
A directory that contains the following files:
* latest RPM for the script
* SPEC file used to generate the RPM.

**make.sh**
A script used to package the script as an RPM-based package that can be installed using *yum* or *dnf*.

**PantheonCMD**
A directory containing the source files for the script, and the man page file.

## Updating the Script
All additions and updates to the script are welcome.

## Packaging the Script
After you update Pantheon CMD and test the changes, build an RPM-based package for the script to be installed on systems that use *yum* or *dnf*.

* Prerequisites:
    * A user has registered their SSH keys with GitHub.

1. Install the `svn` and `rpmbuild` packages on your system:
   ```shell
   # on RHEL
   $ sudo yum install subversion
   $ sudo yum install rpm-build

   # on Fedora
   $ sudo dnf install subversion
   $ sudo dnf install rpm-build
   ```  
2. Clone this repository.
   ```shell
   $ git clone git@github.com:redhataccess/pantheon-cmd.git
   ```
3. Open *./build/pantheon-cmd.spec*.
4. Increment the value of the *Release* number.
    As an example, `Release:   1%{?dist}` increments the version of the build to `1.0.1`, where `{?dist}` identifies of your Linux distribution.
5. Run the build script:
   ```shell
   $ sh make.sh 1.0
   ```
   As a result, the `build/pantheon-cmd-1.0-X.<your-distribution-and-version>.noarch.rpm` file is generated in the root of the repository. This file will be used in the following step.

## Installing Pantheon CMD

Install Pantheon CMD on a local system.

## Installing Pantheon CMD on RHEL and Fedora

Install the RPM and all Ruby gem dependencies.

1. Install the RPM:
   ```shell
   $ sudo dnf localinstall build/pantheon-cmd-1.0-X.el8.noarch.rpm
   ```
   Note that your `rpm` filename might differ based on your Linux distribution.
   * Example:
        *  `el8` for RHEL 8
        *  `fc34` for Fedora 34

2. Install Ruby gem dependencies:
   ```shell
   $ sudo gem install asciidoctor concurrent-ruby haml tilt
   ```

The script is installed on your local machine.
The script provides the `pcmd` command.
Enter `pcmd -h` in your terminal to view the basic usage instructions.

## Installing Pantheon CMD on OSX

Install the dependencies and copy the source files into your local binaries directory.

1. Clone the repository:
   ```shell
   $ git clone
   ```

2. Run the `osx-cmd-intallation.sh` installation script:
   ```shell
   $ /bin/bash osx-cmd-intallation.sh
   ```

## Licensing

This script uses locale attributes files from the AsciiDoctor repository.

For more information, see https://github.com/asciidoctor/asciidoctor/tree/master/data/locale
