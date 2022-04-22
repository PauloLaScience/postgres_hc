# Postgres_Doctor
Executes a collection of SQL queries and compiles the results in a nicely formatted html page.
Perfect to use for monthly health checks, or to investigate a new postgres database. 

Example pictures: https://imgur.com/a/tdFh89G

### Requierements
You need python and the psycopg2 module for this script.
On linux simply use:
```bash
pip install psycopg2-binary
```

On windows:

follow this guide to install pip:

https://www.liquidweb.com/kb/install-pip-windows/

and then 
```bash
pip install psycopg2-binary
```


Requirements if you want to generate a pdf version of the report:
(for debian based system)
```bash
sudo apt install wkhtmltopdf && pip install pdfkit
```

### Example use:

```bash
python doctor.py -ip 192.168.56.1 -p 5432 -d dbname -u username -w "password" -o
```

To generate pdf version:
```bash
python doctor.py -P -o -ip 192.168.56.1 -p 5432 -d dbname -u username -w "password"
```

List of options and commands:
```bash
python doctor.py -h
./doctor.py --help
```

PS: if there are special characters, like $ or &, in the password use backslash! ('\\')

The report will be placed in the output directory, if you use the -o command it will open in the browser automatically.

### Adding your own queries
1) Save the new query in the 'sql' directory
2) in the script doctor.py, go to the "createHtmlBody" function
3) Add a new line using this format:
  html += htmltable("Title to display","filename_of_query.sql")
  
Would appreciate it if you share any cool queries with me so I can add them to this repo.

### Heads Up:

Some of the used SQL queries do not work with old postgres versions. 


### Sources:
I took several queries from these guys:

https://www.citusdata.com/blog/2019/03/29/health-checks-for-your-postgres-database/

https://github.com/NikolayS/postgres_dba
