
import sys


class Registers():
    GPR = [0]*32
    def write_reg(self,location, value):
        self.GPR[location] = value
    def read_reg(self,location):
        return self.GPR[location]
    
    
class InstructionMemory():
    instruction_memory={}

    def write_memory(self,location, value):
        self.instruction_memory[location] = value
    def read_memory(self,location):
        return self.instruction_memory[location]

class DataMemory():
    data_memory=[0]*5000

    def write_memory(self,location, value):
        self.data_memory[location] = value
    def read_memory(self,location):
        return self.data_memory[location]


class CPU():


    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}
    mem_res=0
    op1=0
    op2=0
    res=0
    clock =0
    registers={'pc':0,'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0}

    instruction_memory ={}
    data_memory=[]
    GPR=[]

    def __init__(self, im, dm, reg):
        self.instruction_memory = im
        self.data_memory = dm
        self.GPR = reg

    def fetch(self):
        PC = self.registers['pc']
        self.registers['ir'] = self.instruction_memory.read_memory(PC)

    def decode(self):

        self.signals = dict.fromkeys(self.signals, 0)
        self.registers['rd'] = int(self.registers['ir'][20:25],2)
        self.registers['rs1'] = int(self.registers['ir'][12:17],2)
        self.registers['rs2'] = int(self.registers['ir'][7:12],2)
        #calculating immediate
        self.registers['immx']=0
        if(self.registers['ir'][0]=='1'):
            self.registers['immx']=-2048
        if((self.registers['ir'][25:32]=='0000011') or (self.registers['ir'][25:32]=='0010011')):
            self.registers['immx']+=int(self.registers['ir'][1:12],2)
        elif((self.registers['ir'][25:32]=='0100011') or (self.registers['ir'][25:32]=='1111111')):
            self.registers['immx']+=int(self.registers['ir'][1:7]+self.registers['ir'][20:25],2)
        elif(self.registers['ir'][25:32]=='1100011'):
            self.registers['immx']=int(self.registers['ir'][0]+self.registers['ir'][24]+self.registers['ir'][1:7]+self.registers['ir'][20:24],2)


        #sending signals
        if(self.registers['ir'][25:32]=='0110011'):
            if(self.registers['ir'][17:20]=='111'):
                self.signals['isAnd']=1
            if(self.registers['ir'][17:20]=='110'):
                self.signals['isOr']=1
            if((self.registers['ir'][17:20]=='000') and (self.registers['ir'][0:7]=='0000000')):
                self.signals['isAdd']=1
            if((self.registers['ir'][17:20]=='000') and (self.registers['ir'][0:7]=='0100000')):
                self.signals['isSub']=1
            if(self.registers['ir'][17:20]=='001'):
                self.signals['isSLL']=1
            if(self.registers['ir'][17:20]=='101'):
                self.signals['isSRA']=1
        elif (self.registers['ir'][25:32]=='1111011'):
            self.signals['isSTORENOC']=1
        else:
            self.signals['isImm']=1
            if(self.registers['ir'][25:32]=='0000011'):
                self.signals['isLW']=1
            if(self.registers['ir'][25:32]=='0100011'):
                self.signals['isST']=1
            if(self.registers['ir'][25:32]=='0010011'):
                self.signals['isAdd']=1
            if(self.registers['ir'][25:32]=='1100011'):
                self.registers['immx'] = self.registers['immx']*2
                if(self.GPR.read_reg(self.registers['rs1'])==self.GPR.read_reg(self.registers['rs2'])):
                    self.signals['isBEQ']=1
            if(self.registers['ir'][25:32]=='1111111'):
                self.signals['isLOADNOC'] = 1
        
    def execute(self):
        
        self.op1 = self.GPR.read_reg(self.registers['rs1'])
        self.op2 = self.GPR.read_reg(self.registers['rs2'])
        if(self.signals['isImm']):
            self.op2 = self.registers['immx']
        if(self.signals['isAdd'] or self.signals['isLW'] or self.signals['isST'] or self.signals['isLOADNOC']):
            self.res = self.op1+self.op2
        if(self.signals['isSub']):
            self.res = self.op1-self.op2
        if(self.signals['isAnd']):
            self.res = self.op1 & self.op2
        if(self.signals['isOr']):
            self.res = self.op1 | self.op2
        if(self.signals['isSLL']):
            self.res = self.op1 << self.op2
        if(self.signals['isSRA']):
            self.res = self.op1 >> self.op2

    def memory(self):
        if(self.signals['isLW']):
            self.mem_res = self.data_memory.read_memory(self.res>>2)
        if(self.signals['isST'] or self.signals['isLOADNOC']):
            # self.data_memory[res>>2] = self.GPR[registers['rs2']]
            self.data_memory.write_memory(self.res>>2,self.GPR.read_reg(self.registers['rs2']))
        if(self.signals['isSTORENOC']):
            self.data_memory.write_memory(4100,1) # 4010 hex byte = 16^3+4 decimal word (4bytes)
    
    def writeback(self):
        if(self.signals['isLW']):
            # self.GPR[registers['rd']] = self.mem_res
            self.GPR.write_reg(self.registers['rd'],self.mem_res)
        if(self.signals['isOr']or self.signals['isAnd'] or self.signals['isSLL'] or self.signals['isSRA'] or self.signals['isAdd'] or self.signals['isSub']):
            # self.GPR[registers['rd']] = self.res
            self.GPR.write_reg(self.registers['rd'],self.res)
            #update PC
        if(self.signals['isBEQ']==1):
            self.registers['pc'] = self.registers['pc']+self.registers['immx']
        else:
            self.registers['pc'] = self.registers['pc']+4

    def cpu_clock_edge(self):
        self.fetch()
        self.decode()
        self.execute()
        self.memory()
        self.writeback()
        print("Cycle no: ", self.clock)
        print("signals")
        print(self.signals)
        print("GPR")
        print(self.GPR.GPR)
        print("registers")
        print(self.registers)
        print("data memory")
        for i in range(len(self.data_memory.data_memory)):
            if(self.data_memory.read_memory(i)!=0):
                print(i,' : ',self.data_memory.read_memory(i))
        print()
        print()
        print()
        self.clock +=1





instruction_memory = InstructionMemory()
data_memory = DataMemory()
GPR = Registers()
my_cpu = CPU(instruction_memory,data_memory,GPR)
for i in range(32):
    GPR.write_reg(i,i)
with open(sys.argv[1]) as file:
    lines = [line.rstrip() for line in file]

for i in range(len(lines)):
    instruction_memory.write_memory(4*i,lines[i][0:32])

while(my_cpu.registers['pc']<4*len(lines)):
    my_cpu.cpu_clock_edge()


