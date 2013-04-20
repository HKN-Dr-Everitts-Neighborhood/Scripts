#! python

import csv, sys, os, codecs
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
                    
                    # 6 to 27 = questions about the different subfields of courses;
                    # omit questions with empty responses
                    if not answer:
                        if i in range(6,27):
                            continue
                        else:
                            answer = 'No response'
                    
                    # 2 = full time / intern, #3 = desired degree programs,
                    if i==2 or i == 3 or i in range(6,27):
                        # note rsplit of an empty string is a list of an empty string.
                        answer = ''.join(("* " + a + "\n") for a in answer.rsplit(', '))
                        
                    output_list.append("h4. %s\n%s\n" % (question, answer))

                output_file.write('\n'.join(output_list))

if __name__ == '__main__':
  main()
