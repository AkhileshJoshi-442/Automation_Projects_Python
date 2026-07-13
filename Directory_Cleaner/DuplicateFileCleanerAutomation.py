import os
import sys
import time
import hashlib
import schedule
import smtplib
from email.message import EmailMessage

def calculatechecksum(path,blocksize=1024):
    fobj=open(path,"rb")

    hobj=hashlib.md5()

    buffer= fobj.read(blocksize)
    while(len(buffer)>0):
        hobj.update(buffer)
        buffer= fobj.read(blocksize)

    fobj.close()

    return hobj.hexdigest()

def findduplicate(directoryname="."):

    flag=os.path.isabs(directoryname)

    if(flag==False):
        directoryname=os.path.abspath(directoryname)

    flag=os.path.exists(directoryname)

    if(flag==False):
        print("the path is invalid")
        exit()

    flag=os.path.isdir(directoryname)

    if(flag==False):
        print("the path is valid but target is not a directory")
        exit()

    duplicate={}

    for FolderName , SubFoldersNames , FileNames in os.walk(directoryname):
        for fname in FileNames:
            fname=os.path.join(FolderName,fname)
            checksum=calculatechecksum(fname)

            if(checksum in duplicate):
                duplicate[checksum].append(fname)
            else:
                duplicate[checksum]=[fname]

    return duplicate

def deleteduplicate(path="."):

    mydict=findduplicate(path)

    result=list(filter(lambda x : len(x)>1 , mydict.values()))

    count=0
    cnt=0

    deletedfiles=[]
    keptfiles=[]

    for value in result:
        for subvalue in value:
            count=count+1
            if (count>1):
                print("file deleted: ",subvalue)
                os.remove(subvalue)   
                cnt=cnt+1
                deletedfiles.append(subvalue)
            else:
                keptfiles.append(subvalue)
        count=0

    print("total deleted files: ",cnt)

    return deletedfiles , keptfiles

def generatelog(deletedfiles , keptfiles , directoryname):

    logsfolder = os.path.join(directoryname,"CleanerLogs")

    flag = os.path.exists(logsfolder)

    if(flag==False):
        os.makedirs(logsfolder)

    timestamp = time.ctime()

    filename = "CleanerLog%s.log" %(timestamp)
    filename = filename.replace(" ","_")
    filename = filename.replace(":","_")

    filename = os.path.join(logsfolder,filename)

    fobj=open(filename,"w")

    border="-"*54

    fobj.write(border+"\n")
    fobj.write("Duplicate File Cleaner - Automation Log\n")
    fobj.write("Directory Cleaner Script\n")
    fobj.write(border+"\n")

    fobj.write("This log is created at \n"+timestamp+"\n")
    fobj.write(border+"\n")

    fobj.write("Target directory : "+directoryname+"\n")
    fobj.write(border+"\n")

    fobj.write("Files kept as original :\n")
    if(len(keptfiles)==0):
        fobj.write("none\n")
    else:
        for fname in keptfiles:
            fobj.write(fname+"\n")

    fobj.write(border+"\n")

    fobj.write("Files deleted as duplicate :\n")
    if(len(deletedfiles)==0):
        fobj.write("none\n")
    else:
        for fname in deletedfiles:
            fobj.write(fname+"\n")

    fobj.write(border+"\n")
    fobj.write("Total deleted files : "+str(len(deletedfiles))+"\n")
    fobj.write(border+"\n")

    fobj.write("\n")
    fobj.write("Summary table :\n")
    fobj.write(border+"\n")

    statuscolumnwidth=10

    fobj.write("Status".ljust(statuscolumnwidth)+"File path\n")
    fobj.write(border+"\n")

    if(len(keptfiles)==0 and len(deletedfiles)==0):
        fobj.write("no files were found in this run\n")
    else:
        for fname in keptfiles:
            fobj.write("kept".ljust(statuscolumnwidth)+fname+"\n")

        for fname in deletedfiles:
            fobj.write("deleted".ljust(statuscolumnwidth)+fname+"\n")

    fobj.write(border+"\n")

    fobj.close()

    return filename

def sendmail(fpath,emailpassword,senderemail,receiveremail):

    fobj=open(fpath,"rb")
    data=fobj.read()
    fobj.close()

    msg = EmailMessage()
    msg.add_attachment(data,maintype="file",subtype="log",filename=os.path.basename(fpath))

    msg['Subject'] = "log of deleted files"
    msg['From'] = senderemail
    msg['To'] = receiveremail

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(senderemail, emailpassword)
    s.send_message(msg)
    s.quit()

    print("log file sent through mail: ",fpath)

def task(directoryname,emailpassword,senderemail,receiveremail):

    deletedfiles , keptfiles = deleteduplicate(directoryname)

    logfilename = generatelog(deletedfiles , keptfiles , directoryname)

    print("log file generated: ",logfilename)

    try:
        sendmail(logfilename,emailpassword,senderemail,receiveremail)
    except Exception as e:
        print("mail could not be sent")
        print("reason: ",e)
        print("the script will continue running and try again on the next interval")

def main():
 
    border="-"*66
    print(border)
    print("-------------------Duplicate File Cleaner & Logger----------------")
    print(border)

    if(len(sys.argv)==2):
        if((sys.argv[1]=="--h") or (sys.argv[1]=="--H")):
            print("this application is used to perform directory cleaning")
            print("this is the directory automation script")
            print("it also generates a log file and sends it through mail")

        elif((sys.argv[1]=="--u") or (sys.argv[1]=="--U")):
            print("use the given script as")
            print("scriptname.py nameofdirectory intervalinminutes emailpassword senderemail receiveremail")
            print("please provide valid absolute path")
            print("note: emailpassword is your gmail app password")
            print("senderemail is the gmail address used to send the log")
            print("receiveremail is the address that will receive the log")
            print("arguments must be given in this exact order")
            print("do not run this on a shared computer as it may remain visible")
            print("in the command history")

        else:
            print("invalid commandline argument")
            print("use --h for help or --u for usage")

    elif(len(sys.argv)==6):

        directoryname=sys.argv[1]
        intervalminutes=sys.argv[2]
        emailpassword=sys.argv[3]
        senderemail=sys.argv[4]
        receiveremail=sys.argv[5]

        schedule.every(int(intervalminutes)).minutes.do(task,directoryname,emailpassword,senderemail,receiveremail)

        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        print("invalid number of commandline arguments")
        print("use the given flags as ")
        print("--h : used to display the help")
        print("--u : used to display the usage")
        print("or run as: scriptname.py nameofdirectory intervalinminutes emailpassword senderemail receiveremail")

    print(border)
    print("------------------Thank you for using this script -----------------")
    print("------------------Duplicate File Cleaner Automation---------------")
    print(border)
    
if __name__=="__main__":
    main()