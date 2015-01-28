import argparse
import configparser
import os
import re
import subprocess
import sys


def arg_parser(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Turn a plain text file into a beautiful LaTeX resume.')
    parser.add_argument('-i', '--ini', dest='ini_file', required='True',
                        help='The .ini file containing your resume text\nSee resume.ini.example if you\'re stuck')
    parser.add_argument('-s', '--sty', dest='sty_file', default='tidy-tex-resume.sty',
                        help='The .sty file used to style your resume\nYou can use a built-in file or add your own')
    parser.add_argument('-o', '--out', dest='out_file',
                        help='The file name of the pdf output of this script')
    args = parser.parse_args(argv)

    if not args.out_file:
        args.out_file = change_ext(args.ini_file, 'ini', 'pdf')
    return args


def start_document(sty_file):
    if sty_file.endswith(".sty"):
        sty_file = sty_file[:-len(".sty")]
    return "\\documentclass[11pt]{article}\n\n\\usepackage{" + sty_file + "}\n\n\\begin{document}\n\n"


def section_to_tex(section, section_dict):
    if section == "Head":
        return print_section_head(section_dict)
    elif section == "Skills":
        return print_section_skills(section_dict)
    else:
        return print_section_entry(section, section_dict)


def print_section_head(section_dict):
    text = "\\resumehead\n"
    text += add_section_line(section_dict["name"])
    text += add_repeat_section_line("info", section_dict)
    text += "\\resumeheadend\n\n"
    return text


def print_section_entry(section, section_dict):
    text = ""
    ends_with_number = re.match("^(.*)(\d+)$", section)
    if not ends_with_number:
        text += "\\section*{" + section.strip() + "}\n\n"
    if ends_with_number and int(ends_with_number.group(2)) == 1:
        text += "\\section*{" + str(ends_with_number.group(1)).strip() + "}\n\n"
    text += "\\resumeentry\n"
    text += add_section_line(section_dict["location"])
    if "position" in section_dict:
        text += add_section_line(section_dict["position"])
    else:
        text += add_section_line()
    if "date" in section_dict:
        text += add_section_line(section_dict["date"])
        text += add_section_line()
    else:
        text += add_section_line(section_dict["start date"])
        text += add_section_line(section_dict["end date"])
    text += add_repeat_section_line("description", section_dict)
    text += "\\resumeentryend\n\n"
    return text


def print_section_skills(section_dict):
    text = ""
    if "name" in section_dict:
        text += "\\section*{" + section_dict["name"] + "}\n\n"
    else:
        text += "\\section*{Skills}\n\n"
    text += "\\resumeskills\n"
    text += add_repeat_section_line("skill", section_dict)
    text += "\\resumeskillsend\n\n"
    return text


def add_section_line(entry=""):
    entry = latex_parse(entry)
    return "    {" + entry + "}\n"


def latex_parse(entry):
    print(entry)
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
    entry = re.sub(r"(?i)latex", "\LaTeX", entry)
    entry = re.sub("(?:^|\s)'", "`", entry)
    entry = re.sub(r'\*\*(?P<bolded>.*?)\*\*', r'\\textbf{\g<bolded>}', entry)
    print(entry)
    return entry


def silent_remove(file):
    os.remove(file) if os.path.exists(file) else None


def add_repeat_section_line(item, section_dict):
    if item in section_dict:
        return add_section_line(section_dict[item])
    # else items are of the form "item 1", "item 2", etc.
    text = ""
    i = 0
    while 1:
        i += 1
        info_key = item + " " + str(i)
        if info_key in section_dict:
            text += add_section_line(section_dict[info_key])
        else:
            return text


def end_document():
    return "\\end{document}\n"


def change_ext(file, old_ext, new_ext):
    remove = "\." + old_ext + "$"
    add = "." + new_ext
    return re.sub(remove, "", file) + add


def main(argv):
    parsed_args = arg_parser(argv)
    ini_file = parsed_args.ini_file
    sty_file = parsed_args.sty_file
    out_file = parsed_args.out_file

    config = configparser.RawConfigParser()
    config.read(ini_file)
    silent_remove(out_file)
    silent_remove(change_ext(out_file, 'pdf', 'tex'))
    tex_file_name = change_ext(out_file, 'pdf', 'tex')
    with open(tex_file_name, "w") as tex_file:
        tex_file.write(start_document(sty_file))
        for section in config.sections():
            section_dict = config[section]
            section_tex = section_to_tex(section, section_dict)
            tex_file.write(section_tex)
        tex_file.write(end_document())
    subprocess.call(["pdflatex", tex_file_name])
    silent_remove(change_ext(out_file, 'pdf', 'aux'))
    silent_remove(change_ext(out_file, 'pdf', 'log'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))