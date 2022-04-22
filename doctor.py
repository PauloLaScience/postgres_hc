#!/usr/bin/env python
import psycopg2 #pip install psycopg2-binary
import argparse
import datetime
import webbrowser
import os
import time

connection = ""
def main():
    args = loadArgs()
    conn = loadConn(args)
    html = createHtmlBody(args)
    html = addHeadersAndStyle(html)
    filename = os.path.join("output","hc_"+ args.ip + "_" +args.db + "_" + datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S"))
    writeFile(html,filename)
    if args.openbrowser == True:
        webbrowser.open('file://' + os.path.realpath(filename + ".html")) #Opening browser with root rights returns error.
    if args.outputpdf == True:
        print( "Writing pdf file...")
        try:
            import pdfkit #pip install pdfkit
        except:
            print( "Failed making a pdf report. pdfkit probably missing. \'pip install pdfkit\'")
        try:
            pdfkit.from_string(html, filename + ".pdf")
        except:
            print( "Failed making a pdf report. wkhtmltopdf probably missing on your system. \'sudo apt-get install wkhtmltopdf\'")

def createHtmlBody(args): #To add table: create sql file in doctor/sql/ --> html += htmltable( title of the table, filename of sql )
    html = "<h2>General Info</h2>\n"
    html += "<p>Date of Health Check: " + datetime.datetime.now().strftime("%a %d-%m-%Y") + "</p>"
    html += "<p>Time of Health Check: "+datetime.datetime.now().strftime("%H:%M:%S")+"</p>"
    html += "<p>"+select("select version()").fetchall()[0][0]+"</p>"
    html += "<div class='floatfix'><div id='lefttable'>"
    html += "<h3>Connection</h3>\n"
    html +="<table id='verticaltable1' class='tables'>\n"
    html += "<tr><th style='vertical-align: top' >Database</th><td>"+args.db+"</td></tr>"
    html += "<tr><th style='vertical-align: top' >User</th><td>"+args.dbusr+"</td></tr>"
    html += "<tr><th style='vertical-align: top' >Host</th><td>"+args.ip+"</td></tr>"
    html += "<tr><th style='vertical-align: top' >Port</th><td>"+args.port+"</td></tr>"
    html += verticalHtmlrows("Uptime",ReadSQL("uptime.sql"))
    html += verticalHtmlrows("Longest Trans","SELECT max(now() - xact_start) FROM pg_stat_activity WHERE state IN('idle in transaction', 'active')")
    html += verticalHtmlrows("Current Cons","select count(1) from pg_stat_activity")
    html += verticalHtmlrows("Max Cons", "select setting from pg_settings where name = 'max_connections'")
    html += "</table>"
    html += "</div><div id='righttable'>"
    html += "<h3>Memory</h3>\n"
    html +="<table id='verticaltable2' class='tables'>\n"
    html += verticalHtmlrows("","show work_mem")
    html += verticalHtmlrows("Maintenance","show maintenance_work_mem")
    html += verticalHtmlrows("Autovac_mem","show autovacuum_work_mem")
    html += verticalHtmlrows("","show shared_buffers")
    html += verticalHtmlrows("","show huge_pages")
    html += verticalHtmlrows("Db Size", "select pg_size_pretty(pg_database_size(datname)::bigint) FROM pg_database where datname='"+args.db+"'")
    html += verticalHtmlrows("XID Age","select age(datfrozenxid) FROM pg_database where datname='"+args.db+"';")
    html +="</table>"
    html += "</div></div>"
    html += htmltable("List of all Databases","listdatabases.sql")
    html += htmltable("List of 10 first users","listallusers.sql")
    html += htmltable("List of 10 largest tables","listtables.sql")
    html += "</div>" #div end of page (line break)
    print( "Attempting to query pg_stat_statements table...")
    tmp += "<div class='pages'><h2>Query Performance</h2>"
    tmp += htmltable('Query performance','pg_stat_statements_query_performance.sql')
    tmp += htmltable('report 1','pg_stat_statements_report_s1.sql')
    tmp += htmltable('Top total','pg_stat_statements_top_total_s1.sql')
    tmp += '</div>'
    html += tmp
    print( "\033[91mpg_stat_statements is not installed in database.\033[0m")

    html += "<div class='pages'><h2>WAL and Autovacuum</h2>\n"
    html += htmltable("Dead tuples","tuples_herokus_pg_extras.sql")
    html += "<div class='floatfix'><div id='lefttable'>"
    html += htmltable("Autovacuum settings","autovacuumsettings.sql")
    html += "</div><div id='righttable'>"
    html += htmltable("Write Ahead Log Settings","walsettings.sql")
    html += "</div></div>"
    html += "</div>"

    html += "<div class='pages'> <h2>Indexes</h2>"
    html += "<div class='floatfix'><div id='lefttable'>"
    html += htmltable("Fetched vs Returned","fetchedvsreturnedrows.sql")
    html += "</div><div id='righttable'>"
    html += htmltable("Sequential vs index","sequentialvsindex.sql")
    html += "</div></div>"
    html += htmltable("Unused/Rarely Used Indexes","rarelyusedkeys.sql")
    html += htmltable("Unused/Redundant Indexes Do & Undo Migration DDL","i2_redundant_indexes.sql")
    html += "</div>" #div end of page (line break)

    html += "<div class='pages'><h2>Performance</h2>\n"
    html += htmltable("Cache","cache.sql")
    html += htmltable("Load Profile","3_load_profiles.sql")
    html += htmltable("Current Activity: count of current connections","a1_activity.sql")
    html += htmltable("[EXPERIMENTAL] Alignment Padding. How many bytes can be saved if columns are ordered better?","p1_alignment_padding.sql")
    html += htmltable("Tables and Columns Without Stats (so bloat cannot be estimated)","b5_tables_no_stats.sql")
    html += htmltable("Foreign Keys with Missing/Bad Indexes","foreignkeys.sql")
    html += "</div>" #div end of page (line break)
    html += "src: <p>https://github.com/openPablo/postgres_doctor</p>"
    return html

def htmltable(title, string):
    table = ""
    try:
        cursor = select(ReadSQL(string))
        result = cursor.fetchall()
        if title:
            table += "<div class='tablecontainer'><h3>" + title + "</h3>\n"
        table += "\n<table id='" + string + "' class='tables'>\n"
        if result:
            for columnname in cursor.description:
                table += "\t<th>" + columnname[0] + "</th>\n"
            for row in result:
                table += "\t<tr>\n\t\t"
                for column in row:
                    table +=   "<td>" + str(column) + "</td>"
                table += "\n\t</tr>\n"
        else:
            table += "<p>Query returned empty."
        table += "</table></div>\n"
    except:
        print( "Failed to execute query: " + title + "\n")
    return table
def verticalHtmlrows(title,string):
    table = ""
    try:
        cursor = select(string)
        rows = cursor.fetchall()[0]
        for i,columnname in enumerate(cursor.description):
            table += "\n<tr><th style='vertical-align: top' >" + (title if title else columnname[0])  + "</th>"
            if rows:
                table += "<td>" + str(rows[i]) + "</td>"
            else:
                table += "<td>Empty</td>"
            table += "</tr>"
    except:
        print( "Failed to execute query: " + title  + ". Probable cause is older PostgreSQL version.")
    return table

def addHeadersAndStyle(htmltoadd):
    logo= "https://i.imgur.com/Pnlx3Aa.png"
    html = """<html><header><title>Report</title>
    <link href="https://fonts.googleapis.com/css?family=Cabin|Source+Sans+Pro" rel="stylesheet"></header><body><div class="container">
    <div class='pages'><div id='logowrapper'> <h1> openPablo / postgres_doctor</h1></div>"""
    html +=  htmltoadd
    csspath= os.path.join("css", "style.css")
    html +="</div><style>" + open(csspath,"r").read() + "</style></body></html>"
    return html

def loadArgs():
    parser = argparse.ArgumentParser(description='Automated health check on a postgresql database. Requires psycopg2: \'pip install psycopg2-binary\'')
    parser.add_argument('-P', '--pdf', dest='outputpdf', action='store_true', default='false', help='Converts the html output to a pdf file. Requires wkhtmltopdf installed and python module pdfkit: \'sudo apt install wkhtmltopdf && pip install pdfkit\'')
    parser.add_argument('-o', '--openbrowser', dest='openbrowser', action='store_true', default='false', help='Opens the browser to view the report after done running the script.')
    parser.add_argument('-ip', '--host', dest='ip', action='store', default="localhost", help='Host IP adres to connect. Default is localhost')
    parser.add_argument('-p', '--port', dest='port', action='store', default="5432", help='Port of the Postgres database. Default is 5432')
    parser.add_argument('-d', '--dbname', dest='db', action='store', default="postgres", help='Name of the database. Default is postgres')
    parser.add_argument('-U', '--username', dest='dbusr', action='store', default="postgres", help='Postgres Username. Superuser recommended. Default is postgres')
    parser.add_argument('-W', '--password', dest='dbpas', action='store', default="", help='Postgres Password. Can be left empty depending on database config')
    return parser.parse_args()

def loadConn(args):
    global connection
    connectionString = "host='"+ args.ip + "' dbname='"+args.db+"' port='"+args.port+"' user='"+args.dbusr+"' password='"+args.dbpas+"'"
    try:
        connection =  psycopg2.connect(connectionString)
    except:
        print("Couldn't connect to database!\n" + "Used connectionstring: " + "--host '"+ args.ip + "' --dbname '"+args.db+"' --port '"+args.port+"' --user '"+args.dbusr+"' --password '----'\n")
        os._exit(os.EX_NOHOST)

def ReadSQL(filename):
    result = ""
    file = os.path.join("sql",filename)
    sqlfile = open(file, "r")
    print( "Loading: " + filename)
    result = sqlfile.read()
    return result

def select(qry):
    try:
        cursor = connection.cursor()
        cursor.execute(qry)
        connection.commit()
        return cursor
    except psycopg2.Error as e:
        print( e.pgerror)
        print( e.diag.message_primary)
        connection.rollback()

def writeFile(report, name):
    file = open(name + ".html","w+")
    file.write(report)

main()
