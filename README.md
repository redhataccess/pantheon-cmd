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

## Packaging and Installing Pantheon CMD on RHEL and Fedora
After you update Pantheon CMD and test the changes, build an RPM-based package for the script to be installed on systems that use *yum* or *dnf*.

* Prerequisites:
    * A user has registered their SSH keys with GitHub.

1. Clone this repository.
   ```shell
   $ git clone git@github.com:redhataccess/pantheon-cmd.git
   ```
2. Navigate to the `pantheon-cmd` directory:
    ```shell
    $ cd pantheon-cmd
    ```
3. Run the `linux-cmd-intallation.sh` packaging and installation script:
   ```shell
   $ sh linux-cmd-intallation.sh
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
