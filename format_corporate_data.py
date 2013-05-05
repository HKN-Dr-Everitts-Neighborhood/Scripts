#! python

import csv, sys, os, codecs, re
from unidecode import unidecode

# this code is copied from the csv module documentation; it gives me a version that includes unicode support
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

# also from the csv module docs
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


# My code

# these constants tell us where the courses section of the survey begins
# and where the next section begins (starting with extracurriculars)
BEGIN_COURSES = 6
BEGIN_MISC = 27

def main():
 
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], '<csv filename>'
        return -1

    # make sure output directory exists
    if os.path.exists('output'):
        if not os.path.isdir('output'):
            print 'Error: \'output\' exists, but isn\'t a directory'
            return -2
    else:
        # if output folder doesn't exist, make it
        os.makedirs('output')

    # filename is the command line parameter
    csv_filename = sys.argv[1]

    # so it turns out that the google docs csv actually contains some ugly characters
    # like em dashes that need to be interpreted as utf-8.
    with codecs.open(csv_filename, 'r', 'utf-8') as csv_file:

        # read / parse the file.  lines is a list of the rows in the file
        lines = [line for line in unicode_csv_reader(csv_file)]

        questions = lines[0]
        data = lines[1:]

        for (i, response) in enumerate(data):
      
            # generate 1 file per response.
            output_filename = 'output/response%d.txt' % (i)
            
            # note we're using an ASCII output file; this works because we're forcing
            # everything written to it to be translated to ascii via unidecode; otherwise
            # we would use codecs.open with utf-8 as the codec - but we really don't want
            # the unicode on the wiki anyway, and copy-pasting it properly is difficult.
            with open(output_filename, 'w') as output_file:
        
                # output_list is a list, not a string, because string concatenation
                # is O(n) whereas list append is O(1) (and join is O(n))
                output_list = []
        
                for (i, (question, answer)) in enumerate(zip(questions, response)):
                    
                    # force everything written to ascii
                    question = unidecode(question)
                    answer = unidecode(answer)

                    # The portion of the code from here on is pretty ugly, as we're special
                    # casing based on the different ranges of questions, and the organization
                    # of the questions isn't clear until you look at either the survey or the
                    # survey data.
                    
                    # for questions about the different subfields of courses,
                    # omit questions with empty responses
                    if not answer:
                        if i in range(BEGIN_COURSES, BEGIN_MISC):
                            continue
                        else:
                            answer = 'No response'
                    
                    # insert the headers in the proper places
                    if i == 0:
                        output_list.append("h3. Basic Information:")
                    elif i == BEGIN_COURSES:
                        output_list.append("h3. Desired Courses:")
                    elif i == BEGIN_MISC:
                        output_list.append("h3. Miscellany:")
                    
                    # special treatment for the courses
                    if i in range(BEGIN_COURSES, BEGIN_MISC):
                        # note split of an empty string is a list of an empty string - this is
                        # part of the reason for looking for falsey answers above.
                        
                        # Turns out one of the classes was CS 429 - Software Engineering II, ACP.
                        # thus we look out for this case in the regex, since otherwise the comma throws
                        # things off.
                        processed_answers = []
                        for a in re.split(r', (?!ACP)', answer):
                            if a.count('-') >= 2:
                                # if there are two or more dashes, the last one separates the link.
                                # only one dash = no link.
                                if (a.count('-') > 2):
                                    print output_filename
                                
                                course, link = a.rsplit('-', 1)
                                processed_answers.append("* [" + course.strip() + "|" + link +"]\n")
                            else:
                                processed_answers.append("* " + a +"\n")
                        answer = ''.join(processed_answers)
                    
                    # beginning section drawn as a table; rest dumped as h5's & text
                    if question == "Timestamp":
                        output_list.append("{div:class=hidden}Timestamp: %s{div}\n" % answer)
                    elif i < BEGIN_COURSES:
                        output_list.append("|*%s*:| %s |" % (question, answer))
                    else:
                        output_list.append("h5. %s\n%s\n" % (question, answer))

                output_file.write('\n'.join(output_list))

if __name__ == '__main__':
  main()
