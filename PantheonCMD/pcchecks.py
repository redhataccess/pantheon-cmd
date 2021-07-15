#!/usr/bin/python3

import re
import os


class Colors:
    """Define colors to use in the command line output."""

    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Tags:

    """Define tags."""
    ABSTRACT = '[role="_abstract"]'
    ADD_RES = '[role="_additional-resources"]'
    EXPERIMENTAL = ':experimental:'
    LVLOFFSET = ':leveloffset:'


class FileType:
    """Define strings for finding out fily type."""

    ASSEMBLY = re.compile(r'assembly_.*\.adoc')
    CONCEPT = re.compile(r'con_.*\.adoc')
    PROCEDURE = re.compile(r'proc_.*\.adoc')
    REFERENCE = re.compile(r'ref_.*\.adoc')


class Regex:
    """Define regular expresiions for the checks."""

    VANILLA_XREF = re.compile(r'<<.*>>')
    PSEUDO_VANILLA_XREF = re.compile(r'<<((.*) (.*))*>>')
    MULTI_LINE_COMMENT = re.compile(r'(/{4,})(.*\n)*?(/{4,})')
    SINGLE_LINE_COMMENT = re.compile(r'(?<!//)(?<!/)//(?!//).*\n?')
    EMPTY_LINE_AFTER_ABSTRACT = re.compile(r'\[role="_abstract"]\n(?=\n)')
    FIRST_PARA = re.compile(r'(?<!\n\n)\[role="_abstract"]\n(?!\n)')
    NO_EMPTY_LINE_BEFORE_ABSTRACT = re.compile(r'(?<!\n\n)\[role="_abstract"]')
    COMMENT_AFTER_ABSTRACT = re.compile(r'\[role="_abstract"]\n(?=\//|(/{4,})(.*\n)*?(/{4,}))')
    VAR_IN_TITLE = re.compile(r'(?<!\=)=\s.*{.*}.*')
    INLINE_ANCHOR = re.compile(r'=.*\[\[.*\]\]')
    UI_MACROS = re.compile(r'btn:\[.*\]|menu:.*\]|kbd:.*\]')
    HTML_MARKUP = re.compile(r'<.*>.*<\/.*>|<.*>\n.*\n</.*>')
    CODE_BLOCK = re.compile(r'(?<=\.\.\.\.\n)((.*)\n)*(?=\.\.\.\.)|(?<=----\n)((.*)\n)*(?=----)')
    HUMAN_READABLE_LABEL_XREF = re.compile(r'xref:.*\[]')
    NESTED_ASSEMBLY = re.compile(r'include.*assembly_([a-z|0-9|A-Z|\-|_]+)\.adoc(\[.*\])')
    NESTED_MODULES = re.compile(r'include.*(proc|con|ref)_([a-z|0-9|A-Z|\-|_]+)\.adoc(\[.*\])')
    RELATED_INFO = re.compile(r'= Related information|.Related information', re.IGNORECASE)
    ADDITIONAL_RES = re.compile(r'= Additional resources|\.Additional resources', re.IGNORECASE)
    ADD_RES_ASSEMBLY = re.compile(r'== Additional resources', re.IGNORECASE)
    ADD_RES_MODULE = re.compile(r'\.Additional resources', re.IGNORECASE)
    EMPTY_LINE_AFTER_ADD_RES_TAG = re.compile(r'\[role="_additional-resources"]\n(?=\n)')
    COMMENT_AFTER_ADD_RES_TAG = re.compile(r'\[role="_additional-resources"]\n(?=\//|(/{4,})(.*\n)*?(/{4,}))')
    EMPTY_LINE_AFTER_ADD_RES_HEADER = re.compile(r'== Additional resources\s\n|\.Additional resources\s\n', re.IGNORECASE)
    COMMENT_AFTER_ADD_RES_HEADER = re.compile(r'\.Additional resources\s(?=\//|(/{4,})(.*\n)*?(/{4,}))|== Additional resources\s(?=\//|(/{4,})(.*\n)*?(/{4,}))', re.IGNORECASE)


def vanilla_xref_check(stripped_file):
    """Check if the file contains vanilla xrefs."""
    if re.findall(Regex.VANILLA_XREF, stripped_file):
        return True


def inline_anchor_check(stripped_file):
    """Check if the in-line anchor directly follows the level 1 heading."""
    if re.findall(Regex.INLINE_ANCHOR, stripped_file):
        return True


def var_in_title_check(stripped_file):
    """Check if the file contains a variable in the level 1 heading."""
    if re.findall(Regex.VAR_IN_TITLE, stripped_file):
        return True


def experimental_tag_check(stripped_file):
    """Check if the experimental tag is set."""
    if stripped_file.count(Tags.EXPERIMENTAL) > 0:
        return
    elif re.findall(Regex.UI_MACROS, stripped_file):
        return True


def human_readable_label_check(stripped_file):
    "Check if the human readable label is present."""
    if re.findall(Regex.HUMAN_READABLE_LABEL_XREF, stripped_file):
        return True


def html_markup_check(stripped_file):
    """Check if HTML markup is present in the file."""
    if re.findall(Regex.HTML_MARKUP, stripped_file):
        return True


def nesting_in_modules_check(stripped_file, file_path):
    """Check if modules contains nested content."""
    name_of_file = os.path.basename(file_path)
    if not FileType.ASSEMBLY.fullmatch(name_of_file):
        if re.findall(Regex.NESTED_ASSEMBLY, stripped_file):
            return True
            #print_fail("the following module contains nested assemblies", file)
        if re.findall(Regex.NESTED_MODULES, stripped_file):
            return True
            #print_fail("the following module contains nested modules", file)


def nesting_in_assemblies_check(stripped_file, file_path):
    """Check if file contains nested assemblies."""
    name_of_file = os.path.basename(file_path)
    if FileType.ASSEMBLY.fullmatch(name_of_file):
        if re.findall(Regex.NESTED_ASSEMBLY, stripped_file):
            return True


def lvloffset_check(stripped_file):
    """Check if file contains unsupported includes."""
    if re.findall(Tags.LVLOFFSET, stripped_file):
        return True


def abstarct_tag_none_or_multiple_check(stripped_file):
    """Checks if the abstract tag is not set or set more than once."""
    if stripped_file.count(Tags.ABSTRACT) != 1:
        return True


def abstract_tag_check(original_file):
    """Checks if the abstract tag is set once."""
    if original_file.count(Tags.ABSTRACT) == 1:
        return True


def checks(report, stripped_file, original_file, file_path):
    """Run the checks."""
    if vanilla_xref_check(stripped_file):
        report.create_report('vanilla xrefs', file_path)

    if inline_anchor_check(stripped_file):
        report.create_report('in-line anchors', file_path)

    if var_in_title_check(stripped_file):
        report.create_report('variable in the level 1 heading', file_path)

    if experimental_tag_check(stripped_file):
        report.create_report('experimental tag not', file_path)

    if html_markup_check(stripped_file):
        report.create_report('HTML markup', file_path)

    if human_readable_label_check(stripped_file):
        report.create_report('xrefs without a human readable label', file_path)

    if nesting_in_modules_check(stripped_file, file_path):
        report.create_report('nesting in modules. nesting', file_path)

    if nesting_in_assemblies_check(stripped_file, file_path):
        report.create_report('nesting in assemblies. nesting', file_path)

    if lvloffset_check(stripped_file):
        report.create_report('unsupported use of :leveloffset:. unsupported includes', file_path)

    if abstarct_tag_none_or_multiple_check(stripped_file):
        if stripped_file.count(Tags.ABSTRACT) == 0:
            report.create_report('abstract tag not', file_path)
        else:
            report.create_report('multiple abstract tags', file_path)

    if abstract_tag_check(original_file):
        if re.findall(Regex.FIRST_PARA, original_file):
            report.create_report('the first paragraph might render incorrectly. line between the level 1 heading and the abstract tag not', file_path)
        if re.findall(Regex.NO_EMPTY_LINE_BEFORE_ABSTRACT, original_file):
            report.create_report('empty line before the abstract tag not', file_path)
        if re.findall(Regex.EMPTY_LINE_AFTER_ABSTRACT, original_file):
            report.create_report('empty line after the abstract tag', file_path)
        if re.findall(Regex.COMMENT_AFTER_ABSTRACT, original_file):
            report.create_report('comment after the abstract tag', file_path)
