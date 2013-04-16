use strict;
use warnings;

use LWP::Simple; 
use File::Compare;

my $website = 'http://www.ece.illinois.edu/students/ugrad/curriculum/tech-electives-06.html';
my $website_content = get($website); 

open( FILE, '>', "test_filename" ) or die $!;


print FILE $website_content; 

close (FILE);

if (compare("test_filename","Current_File") == 0) 
{
  print "They're equal\n";
  system("rm test_filename");
}
else
{
    system("rm Current_File");
    system("mv test_filename Current_File");
}

    

