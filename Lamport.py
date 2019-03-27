raw_input = input

p = dict()
event = dict()
def clock():
    """local clock update"""
    procsno = int(raw_input("enter the no. of processes.\n"))
    for i in range(procsno):
        print ("enter the events in process"),
        eventno = int(raw_input(i))
        event[i] = eventno
        for j in range(event[i]):
            p[i,j] = j+1
            print (i,j,p[i,j])
    mes = int(raw_input("please enter the no. of messages sent"))
    for i in range(mes):
        psen = int(raw_input("sender process"))
        esen = int(raw_input("sender event"))
        prec = int(raw_input("receiver process"))
        erec = int(raw_input("receiver event"))
        p[prec,erec] = lamportclock(psen,esen,prec,erec)
    for i in range(procsno):
        for j in range(event[i]):
            print (i,j,p[i,j])

def lamportclock(si,sj,ri,rj):
    """global clock update by message passing"""
    q = p[si,sj]+1
    if q>p[ri,rj]:
        return q
    else:
        return p[ri,rj]