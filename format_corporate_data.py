#! python

import csv, sys, os

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

  with open(csv_filename, 'r') as csv_file:

    # read / parse the file.  lines is a list of the rows in the file
    lines = [line for line in csv.reader(csv_file)]

    questions = lines[0]
    data = lines[1:]

    for (i, response) in enumerate(data):
      
      # generate 1 file per response.
      output_filename = 'output/response%d.txt' % (i)
      with open(output_filename, 'w') as output_file:
        
        # output_list is a list, not a string, because string concatenation
        # is O(n) whereas list append is O(1) (and join is O(n))
        output_list = []
        for (question, answer) in zip(questions, response):

          # TODO: this processing scheme is retarded.
          output_list.append("h3. %s\n%s" % (question, answer))

        output_file.write('\n'.join(output_list))

if __name__ == '__main__':
  main()
