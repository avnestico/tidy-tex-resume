import argparse
import configparser
import os
import re
import subprocess
import sys


def arg_parser(argv):
    """ Ensures that args passed in are valid.

    :param argv:
    :return: properly parsed args
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Turn plain text into a beautiful LaTeX resume.')
    parser.add_argument('ini_file',
                        help='The .ini file containing your resume text. See resume.ini.example if you\'re stuck.')
    parser.add_argument('-s', '--sty', dest='sty_file', default='tidy-tex-resume.sty',
                        help='The .sty file used to style your resume. You can use a built-in file or add your own.')
    parser.add_argument('-o', '--out', dest='out_file',
                        help='The file name of the pdf output of this script.')
    parser.add_argument('-f', '--font', dest='font_size', type=int, default=11,
                        help='The font size of the resulting document. 11 pt is the default; 10 and 12 are good.')
    parser.add_argument('--no-clean', dest='clean_clutter', action='store_false',
                        help='Set this flag if you want to retain the .aux and .log files created by pdflatex.')
    parser.set_defaults(clean_clutter=True)
    args = parser.parse_args(argv)

    if not args.out_file:
        args.out_file = change_ext(args.ini_file, 'ini', 'pdf')
    return args


def change_ext(file, old_ext, new_ext=""):
    """ Switch a string (as a file name) from one extension (if that extension is what the name ends with) to another
    If the current extension does not match old_ext, new_ext is appended without removing any part of the file name
    If no new extension is supplied and old_ext matches the current extension, that extension is dropped

    :param file:
    :param old_ext:
    :param new_ext:
    :return:
    """
    remove = "\." + old_ext + "$"
    add = ""
    if new_ext != "":
        add = "." + new_ext
    # Example: old_ext = "ini", new_ext = "pdf"
    # Performs "s/\.ini$//", then appends ".pdf" to the result.
    return re.sub(remove, "", file) + add


def start_document(sty_file, font_size):
    """ Begins the resume and imports its STY file.

    :param sty_file:
    :return:
    """
    # \usepackage{} syntax drops the file extension from STY files
    sty_file = change_ext(sty_file, "sty")

    opening_text = "\\documentclass[" + str(font_size) + "pt]{article}\n\n" \
                   "\\usepackage{" + sty_file + "}\n\n" \
                   "\\begin{document}\n\n"

    return opening_text


def section_to_tex(section, section_dict):
    """ Convert a section to TeX, depending on its type.

    :param section:
    :param section_dict:
    :return:
    """
    if section == "Head" or ("type" in section_dict and section_dict["type"].lower() == "head"):
        return print_section_head(section_dict)
    elif section == "Skills" or ("type" in section_dict and section_dict["type"].lower() == "skills"):
        return print_section_skills(section_dict)
    elif "Education" in section or ("type" in section_dict and section_dict["type"].lower() == "education"):
        return print_section_education(section, section_dict)
    else:
        return print_section_entry(section, section_dict)


def print_section_head(section_dict):
    """ Convert the head section to TeX

    :param section_dict:
    :return:
    """
    text = "\\resumehead\n"
    text += add_section_line(section_dict["name"])
    text += add_repeat_section_line("info", section_dict)
    text += "\\resumeheadend\n\n"
    return text


def print_section_entry(section, section_dict):
    """ Convert a body entry to TeX

    :param section:
    :param section_dict:
    :return:
    """
    ends_with_number = re.match("^(.*)(\d+)$", section)

    # Determine title of segment
    text = ""
    if not ends_with_number:
        text += "\\section*{" + section.strip() + "}\n\n"
    if ends_with_number and int(ends_with_number.group(2)) == 1:
        text += "\\section*{" + str(ends_with_number.group(1)).strip() + "}\n\n"
    # if the segment ends with a number that isn't "1",
        # print nothing and assume that it's a continuation of a previous segment under the same header

    # Add lines to body entry in the correct order
    text += "\\resumeentry\n"
    text += add_section_line(section_dict["location"])

    if "position" in section_dict:
        text += add_section_line(section_dict["position"])
    else:  # Add a blank entry so that the TeX \resumeentry function takes in the correct number of arguments
        text += add_section_line()

    if "date" in section_dict:
        text += add_section_line(section_dict["date"])
        # Add a blank entry so that the TeX \resumeentry function takes in the correct number of arguments
        text += add_section_line()
    else:  # The date is assumed to be in two separate parts, start and end
        text += add_section_line(section_dict["start date"])
        text += add_section_line(section_dict["end date"])

    text += add_repeat_section_line("description", section_dict)
    text += "\\resumeentryend\n\n"
    return text


def print_section_skills(section_dict):
    """ Convert the skills section to TeX

    :param section_dict:
    :return:
    """
    text = ""
    if "name" in section_dict:
        text += "\\section*{" + section_dict["name"] + "}\n\n"
    else:
        text += "\\section*{Skills}\n\n"
    text += "\\resumeskills\n"
    text += add_repeat_section_line("skill", section_dict)
    text += "\\resumeskillsend\n\n"
    return text

def print_section_education(section, section_dict):
    """ Convert the education section to TeX

    :param section_dict:
    :return:
    """
    ends_with_number = re.match("^(.*)(\d+)$", section)

    # Determine title of segment
    text = ""
    if not ends_with_number:
        text += "\\section*{" + section.strip() + "}\n\n"
    if ends_with_number and int(ends_with_number.group(2)) == 1:
        text += "\\section*{" + str(ends_with_number.group(1)).strip() + "}\n\n"
    # if the segment ends with a number that isn't "1",
        # print nothing and assume that it's a continuation of a previous segment under the same header

    text += "\\educationentry\n"
    text += add_section_line(section_dict["degree"])
    text += add_section_line(section_dict["location"])
    if "course" in section_dict:
        text += add_section_line(section_dict["course"])
    else:
        text += add_section_line()

    if "date" in section_dict:
        text += add_section_line(section_dict["date"])
        # Add a blank entry so that the TeX \resumeentry function takes in the correct number of arguments
        text += add_section_line()
    else:  # The date is assumed to be in two separate parts, start and end
        text += add_section_line(section_dict["start date"])
        text += add_section_line(section_dict["end date"])

    if "description" in section_dict:
        text += add_section_line(section_dict["description"])
    else:
        text += add_section_line()

    text += "\n"
    return text


def latex_parse(entry):
    """ Unwieldy function to properly handle all the LaTeX special characters.
    TODO: Find a markdown-to-LaTeX parser.

    :param entry:
    :return:
    """

    # Handles all of: \#$%&_{}~|^<>
    entry = re.sub("\\\\", "\\\\textbackslash", entry)
    entry = re.sub("#", "\\#", entry)
    entry = re.sub("\\$", "\\$", entry)
    entry = re.sub("%", "\\%", entry)
    entry = re.sub("&", "\\&", entry)
    entry = re.sub("_", "\\_", entry)
    entry = re.sub("{", "$\\left\\{\\\\right.$", entry)
    entry = re.sub("}", "$\\left.\\\\right\\}$", entry)
    entry = re.sub("~", "\\\\textasciitilde", entry)
    entry = re.sub("\|", "$|$", entry)
    entry = re.sub("\\^", "$\string^$", entry)
    entry = re.sub("<", "$<$", entry)
    entry = re.sub(">", "$>$", entry)

    # Converts the string 'latex' to a form that is typeset properly in LaTeX
    entry = re.sub(r"(?i)latex", "\LaTeX", entry)

    # Converts leading quotations to backticks, which are typeset as opening quotes in LaTeX
    entry = re.sub("(?:^|\s)'", "`", entry)

    # Takes strings surrounded by **double asterisks** and bolds them
    entry = re.sub(r'\*\*(?P<bolded>.*?)\*\*', r'\\textbf{\g<bolded>}', entry)
    return entry


def add_section_line(entry=""):
    """ Wrap TeX around a properly formatted string

    :param entry:
    :return:
    """
    entry = latex_parse(entry)
    return "    {" + entry + "}\n"


def add_repeat_section_line(item, section_dict):
    """ Format a list of 0 or more items for TeX

    :param item:
    :param section_dict:
    :return:
    """
    # If there is only one item in the list, its name does not need to be followed by a number
    if item in section_dict:
        return add_section_line(section_dict[item])

    # else items are of the form "item 1", "item 2", etc.
    text = ""
    i = 0
    while 1:
        i += 1
        info_key = item + " " + str(i)

        # Continue adding items and iterating until the list is done.
        if info_key in section_dict:
            text += add_section_line(section_dict[info_key])
        else:
            return text


def end_document():
    """ Add line to end LaTeX document.

    :return:
    """
    return "\\end{document}\n"


def silent_remove(file):
    """ Delete a file if it exists, and do nothing otherwise

    :param file:
    :return:
    """
    os.remove(file) if os.path.exists(file) else None


def ini_to_tex(ini_file, sty_file, out_file, font_size):
    """ Take in the names of an INI file, a STY file, a PDF file, and the document's font size
    Uses the INI and STY files to build a TEX file that can be processed into the PDF file

    :param font_size:
    :param ini_file:
    :param sty_file:
    :param out_file:
    :return:
    """
    config = configparser.RawConfigParser()
    config.read(ini_file)

    # If a TEX file matching the name given already exists, delete it just in case.
    tex_file_name = change_ext(out_file, 'pdf', 'tex')
    silent_remove(tex_file_name)

    # Write each segment into the TEX file in the order that they appear in the INI file
    with open(tex_file_name, "w") as tex_file:
        tex_file.write(start_document(sty_file, font_size))
        for section in config.sections():
            section_dict = config[section]
            section_tex = section_to_tex(section, section_dict)
            tex_file.write(section_tex)
        tex_file.write(end_document())
    return tex_file_name


def main(args):
    """ Call pdflatex on a formatted tex file, and delete unnecessary files

    :param args:
    :return:
    """
    ini_file = args.ini_file
    sty_file = args.sty_file
    out_file = args.out_file
    font_size = args.font_size
    clean_clutter = args.clean_clutter

    # If there exists a pdf with a name that matches out_file, delete it
    silent_remove(out_file)

    # Process INI file into PDF
    tex_output = ini_to_tex(ini_file, sty_file, out_file, font_size)
    subprocess.call(["pdflatex", tex_output])

    # Clean up clutter
    if clean_clutter:
        silent_remove(change_ext(tex_output, 'tex', 'aux'))
        silent_remove(change_ext(tex_output, 'tex', 'log'))

    return 0


if __name__ == '__main__':
    parsed_args = arg_parser(sys.argv[1:])
    sys.exit(main(parsed_args))
