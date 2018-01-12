# tidy-tex-resume

## Turn plain text into a beautiful LaTeX resume.

tidy-tex-resume takes a properly written INI file, wraps it in a thin layer of LaTeX, and turns it into a stylish PDF. By separating content from formatting, tidy-tex-resume lets anyone harness the typesetting power of LaTeX without needing to delve into code.

### Dependencies

* pdflatex (most likely through texlive on Linux, [MikTeX](http://miktex.org/download) on Windows, or [MacTeX](https://tug.org/mactex/downloading.html) on OS X)
* that's it!

### Out-of-the-box functionality
    python tidy-tex-resume.py resume.ini.example
    python tidy-tex-resume.py -h

### Usage

To format your own resume with tidy-tex-resume, copy the contents of `resume.ini.example` to a file with a name like `resume.ini`. This file will have three main sections:

#### 1. [Head]

The head should always be the first section of your INI, in much the same way that your name is what you want to see at the top of your resume. The head contains your name and a few pieces of contact info, such as an email address, a phone number, or a personal website. If you're using the default file tidy-tex-resume.sty, you can put up to three of contact information in the head. If you want to add more info, place more than one piece of information in a single line.

    [Head]
    Name: John Doe
    Info 1: john.doe@example.com
    Info 2: 555-867-5309 | 555-999-1234
    Info 3: example.com/john.doe

#### 2. [Body]

You may have multiple Body entries. Rather than being named "Body", these entries will be named with the header you want them to be placed under. For instance, you can write down the places you worked in a series of entries named `[Experience 1]`, `[Experience 2]`, and so on:

    [Experience 1]
    Location: Company, Inc.
    Position: Associate Person
    Start Date: Sept 2010
    End Date: May 2014
    Description 1: Did a few things
    Description 2: Learned the thing

As you can see, body entries contain a location, (optional) position, and date; they can also have any number of description lines, which will be formatted as a list in the PDF output.

If you only have one particular entry for a given header, or for a list like `Info` or `Description`, you can drop the trailing 1:

    [Extracurriculars]
    Location: Company, Inc.
    Position: Volunteer Person
    Date: Summer 2012 and 2013
    Description: Did a few things

Also note that instead of a `Start Date` and `End Date` entry, you can use a simple `Date` entry.

#### 3. [Education]

You may have multiple Education entries.

    [Education 1]
    Degree: BSc
    Location: University of Wherever
    Position: Something
    Start Date: Sept 2010
    End Date: May 2014
    Description 1: Learned the thing
    Description 2: Did the thing

As you can see, educationn entries contain a degree, location, (optional) course, and date; they can also have zero or one description lines, which will be formatted as a list in the PDF output if present.

TODO: Determine whether multiple description lines are useful to include.

As with Body sections, instead of a `Start Date` and `End Date` entry, you can use a simple `Date` entry.

#### 3. [Skills]

You can also place a section containing your technical skills into the INI file. This will usually be either before or after the body section, depending on your preference. The skills section usually contains nothing but a numbered list of skills as you'd like them to appear on your resume. There's also an optional `Name` entry if you'd like the name of this section to be something other than the default, "Skills". For instance:

    Name: Technical Skills
    Skill 1: Doing some things
    Skill 2: Doing other things

### Formatting

Surrounding a word or phrase in `**double asterisks**` will format that part of the PDF in bold.

### When You're Ready

Once your INI file is ready, simply run

    python tidy-tex-resume.py resume.ini

Your resume will be formatted and output as `resume.pdf`.

### Other Arguments

    -s STY_FILE:  Change the .sty file used to format your document
                  Uses tidy-tex-resume.sty by default
    -o OUT_FILE:  Rename the .pdf output file
                  Has the same name as the input file by default
    -f FONT_SIZE: Change the font size in the resulting pdf
                  11 is the default, and you probably want to stay between 10 and 12
    --no-clean:   Setting this flag retains the auxiliary files created by pdflatex
                  These files are deleted by default
    
    $ python tidy-tex-resume.py resume.ini -s custom.sty -o "John Doe Resume.pdf" -f 12 --no-clean
