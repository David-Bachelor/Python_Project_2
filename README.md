# README
This project was for transferring expenses data between different accounting software. Some code is not included here for reasons of commercial sensitivity/security.
This was an initial version built to run locally.
The project downloaded data from one API then processed it to change expenses categorization and flag any that did not succesfully match for human review. When approved a file of the expenses are uploaded by another piece of code from a different project.
I was calling the program using VBA from an excel spreadsheet that would also be used to review the data and check any exceptions.
This project uses python, predominantly with the pandas library though a number of other libraries are used. 
