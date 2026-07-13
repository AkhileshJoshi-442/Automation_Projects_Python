import psutil
import os
import sys
import time
import schedule
import smtplib
from email.message import EmailMessage

def ProcessScan():

    listprocess = []

    for proc in psutil.process_iter():
        try:
            info = proc.as_dict(attrs=['pid','name','username'])
            info['vms'] = proc.memory_info().vms / (1024 * 1024)
            listprocess.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return listprocess

def CreateLog(FolderName):

    timestamp = time.ctime()

    FileNameOnly = "ProcessLog%s.log" %(timestamp)
    FileNameOnly = FileNameOnly.replace(" ","_")
    FileNameOnly = FileNameOnly.replace(":","_")

    FileName = os.path.join(FolderName, FileNameOnly)

    fobj = open(FileName, "w")

    border = "-"*80

    fobj.write(border+"\n")
    fobj.write("\t\tSystem Process Logger - Process Log\n")
    fobj.write("\t\tLog file is created at : "+time.ctime()+"\n")
    fobj.write(border+"\n")

    Data = ProcessScan()

    pidcolumnwidth = 10
    namecolumnwidth = 30
    usercolumnwidth = 20
    memorycolumnwidth = 15

    fobj.write("PID".ljust(pidcolumnwidth))
    fobj.write("Name".ljust(namecolumnwidth))
    fobj.write("User".ljust(usercolumnwidth))
    fobj.write("Memory(MB)".ljust(memorycolumnwidth))
    fobj.write("\n")

    fobj.write(border+"\n")

    for value in Data:
        pid = str(value.get('pid',""))
        name = str(value.get('name',""))
        user = str(value.get('username',""))
        vms = value.get('vms',0)
        memory = "%.2f" %(vms)

        fobj.write(pid.ljust(pidcolumnwidth))
        fobj.write(name.ljust(namecolumnwidth))
        fobj.write(user.ljust(usercolumnwidth))
        fobj.write(memory.ljust(memorycolumnwidth))
        fobj.write("\n")

    fobj.write(border+"\n")
    fobj.write("Total processes : "+str(len(Data))+"\n")
    fobj.write(border+"\n")

    fobj.close()

    return FileName

def sendmail(fpath,emailpassword,senderemail,receiveremail):

    fobj=open(fpath,"rb")
    data=fobj.read()
    fobj.close()

    msg = EmailMessage()
    msg.add_attachment(data,maintype="file",subtype="log",filename=os.path.basename(fpath))

    msg['Subject'] = "log of running processes"
    msg['From'] = senderemail
    msg['To'] = receiveremail

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(senderemail, emailpassword)
    s.send_message(msg)
    s.quit()

    print("log file sent through mail: ",fpath)

def task(foldername,emailpassword,senderemail,receiveremail):

    logfilename = CreateLog(foldername)

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
    print("-------------------System Process Logger & Scheduler--------------")
    print(border)

    if(len(sys.argv)==2):
        if((sys.argv[1]=="--h") or (sys.argv[1]=="--H")):
            print("this application is used to log details of running processes")
            print("this is the system process logger script")
            print("it logs PID, name, user and memory usage of every running process")

        elif((sys.argv[1]=="--u") or (sys.argv[1]=="--U")):
            print("use the given script as")
            print("scriptname.py nameoffolder intervalinminutes emailpassword senderemail receiveremail")
            print("please provide valid absolute path")
            print("a new log file will be created in this folder on every interval")
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

        foldername=sys.argv[1]
        intervalminutes=sys.argv[2]
        emailpassword=sys.argv[3]
        senderemail=sys.argv[4]
        receiveremail=sys.argv[5]

        flag=os.path.isabs(foldername)

        if(flag==False):
            foldername=os.path.abspath(foldername)

        flag=os.path.exists(foldername)

        if(flag==False):
            os.makedirs(foldername)

        flag=os.path.isdir(foldername)

        if(flag==False):
            print("the path is valid but target is not a directory")
            exit()

        schedule.every(int(intervalminutes)).minutes.do(task,foldername,emailpassword,senderemail,receiveremail)

        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        print("invalid number of commandline arguments")
        print("use the given flags as ")
        print("--h : used to display the help")
        print("--u : used to display the usage")
        print("or run as: scriptname.py nameoffolder intervalinminutes emailpassword senderemail receiveremail")

    print(border)
    print("------------------Thank you for using this script -----------------")
    print("---------------------System Process Logger------------------------")
    print(border)

if __name__ == "__main__":
    main()
