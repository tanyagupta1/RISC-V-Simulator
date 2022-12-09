
import sys
import json

class Registers():
    GPR = [0]*32
    def write_reg(self,location, value):
        self.GPR[location] = value
    def read_reg(self,location):
        return self.GPR[location]
    
    
class InstructionMemory(): #word addressable
    instruction_memory={}

    def write_memory(self,location, value):
        self.instruction_memory[location] = value
    def read_memory(self,location):
        return self.instruction_memory[location]

class DataMemory(): #word addressable (length=5000 words)
    data_memory=[0]*5000

    def write_memory(self,location, value):
        self.data_memory[location] = value
    def read_memory(self,location):
        return self.data_memory[location]

class Fetch():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0}

    def run(self,instruction_memory,pc):
        print("FETCH")
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        PC = pc
        self.registers['ir'] = instruction_memory.read_memory(PC)

class Decode():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0}

    def run(self,GPR):
        
        print("DECODE")
        if(self.registers['ir']==0):
            return False
        self.signals = dict.fromkeys(self.signals, 0)
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)

        if(False):
            return True
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
                if(GPR.read_reg(self.registers['rs1'])==GPR.read_reg(self.registers['rs2'])):
                    self.signals['isBEQ']=1
            if(self.registers['ir'][25:32]=='1111111'):
                self.signals['isLOADNOC'] = 1
        
        return False
        
class Execute():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}

    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}

    def run(self,GPR):
        print("EXECUTE")
        if(self.registers['ir']==0):
            return
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        op1 = GPR.read_reg(self.registers['rs1'])
        op2 = GPR.read_reg(self.registers['rs2'])
        if(self.signals['isImm']):
            op2 = self.registers['immx']
        if(self.signals['isAdd'] or self.signals['isLW'] or self.signals['isST'] or self.signals['isLOADNOC']):
            self.registers['res'] = op1+op2
        if(self.signals['isSub']):
            self.registers['res'] = op1-op2
        if(self.signals['isAnd']):
            self.registers['res'] = op1 & op2
        if(self.signals['isOr']):
            self.registers['res'] = op1 | op2
        if(self.signals['isSLL']):
            self.registers['res'] = op1 << op2
        if(self.signals['isSRA']):
            self.registers['res'] = op1 >> op2

class Memory():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}

    def run(self,data_memory,GPR):
        print("MEMORY")
        if(self.registers['ir']==0):
            return
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        if(self.signals['isLW']):
            self.registers['mem_res'] = data_memory.read_memory(self.registers['res']>>2)
        if(self.signals['isST'] or self.signals['isLOADNOC']):
            # self.data_memory[res>>2] = self.GPR[registers['rs2']]
            data_memory.write_memory(self.registers['res']>>2,GPR.read_reg(self.registers['rs2']))
        if(self.signals['isSTORENOC']):
            data_memory.write_memory(4100,1) # 4010 hex byte = 16^3+4 decimal word (4bytes)

class Writeback():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}

    def run(self,GPR):
        print("WRITEBACK")
        if(self.registers['ir']==0):
            return
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        if(self.signals['isLW']):
            GPR.write_reg(self.registers['rd'],self.registers['mem_res'])
        if(self.signals['isOr']or self.signals['isAnd'] or self.signals['isSLL'] or self.signals['isSRA'] or self.signals['isAdd'] or self.signals['isSub']):
            GPR.write_reg(self.registers['rd'],self.registers['res'])
        # if(self.signals['isBEQ']==1):
        #     self.registers['pc'] = self.registers['pc']+self.registers['immx']
        # else:
        #     self.registers['pc'] = self.registers['pc']+4

class CPU():
    clock=0
    instruction_memory ={}
    data_memory=[]
    GPR=[]
    PC=0
    fetch_unit=0
    decode_unit=0
    execute_unit=0
    memory_unit=0
    writeback_unit=0
    stall = False


    def __init__(self, im, dm, reg):
        self.instruction_memory = im
        self.data_memory = dm
        self.GPR = reg
        self.fetch_unit= Fetch()
        self.decode_unit= Decode()
        self.execute_unit= Execute()
        self.memory_unit = Memory()
        self.writeback_unit= Writeback()

    def fetch(self,instruction_memory,pc):
        self.fetch_unit.run(instruction_memory,pc)

    def decode(self,GPR):
        self.stall  = self.decode_unit.run(GPR)
        

    def execute(self,GPR):
        self.execute_unit.run(GPR)
        

    def memory(self,data_memory,GPR):
        self.memory_unit.run(data_memory,GPR)
        
    
    def writeback(self,GPR):
        self.writeback_unit.run(GPR)
        
    
    def transfer_sig(self):
        self.writeback_unit.signals = self.memory_unit.signals
        self.writeback_unit.registers = self.memory_unit.registers

        self.memory_unit.signals = self.execute_unit.signals
        self.memory_unit.registers = self.execute_unit.registers

        self.execute_unit.signals=self.decode_unit.signals 
        self.execute_unit.registers=self.decode_unit.registers 

        if(not self.stall):
            self.decode_unit.signals = self.fetch_unit.signals
            self.decode_unit.registers = self.fetch_unit.registers





    def cpu_clock_edge(self):
        print("Cycle no: ", self.clock)
        global file1
        if(not self.stall):
            self.fetch(self.instruction_memory,self.PC)
            self.PC = self.PC+4
            self.stall  = self.decode(self.GPR)
        else:
            print("Stalling on decode")
        self.execute(self.GPR)
        self.memory(self.data_memory,self.GPR)
        self.writeback(self.GPR)
        self.transfer_sig()

        
        # print("signals")
        # print(self.writeback_unit.signals)
        print("GPR")
        print(self.GPR.GPR)
        # print("registers")
        # print(self.writeback_unit.registers)
        print("data memory")
        for i in range(len(self.data_memory.data_memory)):
            if(self.data_memory.read_memory(i)!=0):
                print(i,' : ',self.data_memory.read_memory(i))
        
        file1.write("Cycle no: "+ str(self.clock)+'\n')
        file1.write("signals"+'\n')
        file1.write(json.dumps(self.writeback_unit.signals))
        file1.write('\n')
        file1.write("GPR\n")
        file1.write(json.dumps(self.GPR.GPR))
        file1.write('\n')
        file1.write("registers\n")
        file1.write(json.dumps(self.writeback_unit.registers))
        file1.write('\n')
        file1.write("data memory\n")
        for i in range(len(self.data_memory.data_memory)):
            if(self.data_memory.read_memory(i)!=0):
                file1.write(str(i)+' : '+str(self.data_memory.read_memory(i))+'\n')
        file1.write('\n')
        file1.write('\n')
        file1.write('\n')
        print()
        print()
        print()
        self.clock +=1




file1 = open("myfile.txt", "w")
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

while(my_cpu.PC<4*len(lines)):
    my_cpu.cpu_clock_edge()
file1.write("Ending memory state: \n")
for i in range(len(data_memory.data_memory)):
    file1.write(str(i)+' : '+str(data_memory.read_memory(i))+'\n')
file1.write('\n')
file1.close()
