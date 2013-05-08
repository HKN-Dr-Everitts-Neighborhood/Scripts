#! python

import csv, sys, os, codecs, re, collections
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
    
    # force everything written to ascii
    for i, question in enumerate(questions):
        questions[i] = unidecode(question)
    for line in data:
        for i,answer in enumerate(line):
            line[i] = unidecode(answer)

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
    
    build_index(questions, data)

def build_index(questions, answers):
    
    position_type_to_answers = collections.defaultdict(list)
    questions_to_index = dict()
    
    for i,q in enumerate(questions):
        questions_to_index[q] = i
    
    index_pos_type = questions_to_index['Position Type']
    index_company = questions_to_index['Company name']
    index_title = questions_to_index['Position Title']
    index_avail_pos = questions_to_index['Available Positions']
    index_degrees = questions_to_index['Desired Degrees Programs']
    
    # gather all responses in a particular position type into a list mapped to by position_type_to_answers
    for answer in answers:
        position_type_to_answers[answer[index_pos_type]].append(answer)
    
    # helper function to generate titles of pages for links.  Doesn't handle duplicates though.
    def title_func(answer):
        return ('%s - %s' % (answer[index_company].strip(),answer[index_title].strip())).replace('/', ', ')
    
    # set up dictionary used to look for pages with duplicate titles
    count_for_duplicates = collections.Counter([title_func(answer) for answer in answers])
    
    output_lines = []
    for pos_type in position_type_to_answers:
        output_lines.append("h3. %s\n" % pos_type);
        output_lines.append('|| Job || Intern || Co-op || Full-time || Bachelors || Masters || PhD ||\n')
        for answer in position_type_to_answers[pos_type]:
            
            avail_pos = set(answer[index_avail_pos].split(', '))
            degrees = set(answer[index_degrees].split(', '))
            
            # generate page title for linking, and then handle duplicates
            page_title = title_func(answer)
            if count_for_duplicates[page_title] > 1:
                # This fixes most of the problematic links.  Our convention isn't solid enough to make it work for all though.
                page_title += '(' + pos_type.replace(':','') + ')'
            
            output_lines.append(
                "|[{company} - {title}|{link}]|{intern}|{coop}|{fulltime}|{bachelors}|{masters}|{phd}|\n".format(
                    company=answer[index_company],
                    title=answer[index_title],
                    intern='x' if 'Intern' in avail_pos else ' ',
                    coop='x' if 'Co-op' in avail_pos else ' ',
                    fulltime='x' if 'Full Time' in avail_pos else ' ',
                    bachelors='x' if 'Bachelors' in degrees else ' ',
                    masters='x' if 'Masters' in degrees else ' ',
                    phd='x' if 'PhD' in degrees else ' ',
                    link=page_title
                )
            )
        output_lines.append("\n")
    
    with open('index.txt', 'w') as index:
        index.write(''.join(output_lines))

if __name__ == '__main__':
  main()
