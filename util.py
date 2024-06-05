import csv

#loader that reads in the tab delimited file. Returns
#an array with each element containing a dictionary. Dictionary Keys
#are column headers from the file.
def loadTabFile(tabFile):
    f = []
    with open(tabFile, "r") as sched:
        tab_reader = csv.DictReader(sched, delimiter="\t")
        for line in tab_reader:
            #convert integer values to int type.  ToDo convert floats too.
            for key in line.keys():
                if line[key].isdigit():
                    line[key] = int(line[key])
            f.append(dict(line))
    return f
