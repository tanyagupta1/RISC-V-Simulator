
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
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0}
    # delay =1
    # current_left=1
    # def __init__(self, latency):
    #     self.delay=latency
    #     self.current_left=latency
    
    def run(self,instruction_memory,pc):
        # self.current_left = self.current_left-1
        PC = pc
        self.registers['ir'] = instruction_memory.read_memory(PC)
        file1.write("FETCH: "+str(self.registers['ir'])+'\n')
        print("FETCH")
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)

class Decode():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0}

    scoreboard=[]

    def run(self,GPR,scoreboard):
        stash = False
        print("DECODE: ",self.registers['ir'])
        file1.write("DECODE: "+str(self.registers['ir'])+'\n')
        if(self.registers['ir']==0):
            return (False,stash,None)
        if(self.registers['ir']=='00000000000000000000000000000000'):
            return (False,stash,None)
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
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
            if(self.registers['ir'][17:20]=='110'):
                self.signals['isOr']=1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
            if((self.registers['ir'][17:20]=='000') and (self.registers['ir'][0:7]=='0000000')):
                self.signals['isAdd']=1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
            if((self.registers['ir'][17:20]=='000') and (self.registers['ir'][0:7]=='0100000')):
                self.signals['isSub']=1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
            if(self.registers['ir'][17:20]=='001'):
                self.signals['isSLL']=1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
            if(self.registers['ir'][17:20]=='101'):
                self.signals['isSRA']=1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
        
        elif (self.registers['ir'][25:32]=='1111011'):
            self.signals['isSTORENOC']=1
        else:
            self.signals['isImm']=1
            if(self.registers['ir'][25:32]=='0000011'):
                self.signals['isLW']=1
                if(scoreboard.pending[self.registers['rs1']] ):
                    return (True,stash,None)
                scoreboard.pending[self.registers['rd']]=True
            if(self.registers['ir'][25:32]=='0100011'):
                self.signals['isST']=1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
            if(self.registers['ir'][25:32]=='0010011'):
                if(scoreboard.pending[self.registers['rs1']]):
                    return (True,stash,None)
                self.signals['isAdd']=1
                scoreboard.pending[self.registers['rd']]=True
            if(self.registers['ir'][25:32]=='1100011'):
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
                self.registers['immx'] = self.registers['immx']*2
                if(GPR.read_reg(self.registers['rs1'])==GPR.read_reg(self.registers['rs2'])):
                    self.signals['isBEQ']=1
                    stash = True
            if(self.registers['ir'][25:32]=='1111111'):
                self.signals['isLOADNOC'] = 1
                if(scoreboard.pending[self.registers['rs1']] or scoreboard.pending[self.registers['rs2']]):
                    return (True,stash,None)
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        return (False,stash,self.registers['immx'])
        
class Execute():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,'isSTORENOC':0, 'isLOADNOC':0}

    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}

    def run(self,GPR,scoreboard):
        print("EXECUTE")
        file1.write("EXECUTE: "+str(self.registers['ir'])+'\n')
        if(self.registers['ir']==0):
            return
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        # op1 = GPR.read_reg(self.registers['rs1'])
        # op2 = GPR.read_reg(self.registers['rs2'])
        op1 = scoreboard.value[self.registers['rs1']]
        op2 = scoreboard.value[self.registers['rs2']]
        if(self.signals['isImm']):
            op2 = self.registers['immx']
        if(self.signals['isAdd'] or self.signals['isLW'] or self.signals['isST'] or self.signals['isLOADNOC']):
            self.registers['res'] = op1+op2
            if(self.signals['isAdd']):
                scoreboard.pending[self.registers['rd']] = False
                scoreboard.value[self.registers['rd']] = self.registers['res']
        if(self.signals['isSub']):
            self.registers['res'] = op1-op2
            scoreboard.pending[self.registers['rd']] = False
            scoreboard.value[self.registers['rd']] = self.registers['res']
        if(self.signals['isAnd']):
            self.registers['res'] = op1 & op2
            scoreboard.pending[self.registers['rd']] = False
            scoreboard.value[self.registers['rd']] = self.registers['res']
        if(self.signals['isOr']):
            self.registers['res'] = op1 | op2
            scoreboard.pending[self.registers['rd']] = False
            scoreboard.value[self.registers['rd']] = self.registers['res']
        if(self.signals['isSLL']):
            self.registers['res'] = op1 << op2
            scoreboard.pending[self.registers['rd']] = False
            scoreboard.value[self.registers['rd']] = self.registers['res']
        if(self.signals['isSRA']):
            self.registers['res'] = op1 >> op2
            scoreboard.pending[self.registers['rd']] = False
            scoreboard.value[self.registers['rd']] = self.registers['res']

class Memory():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,'isSTORENOC':0, 'isLOADNOC':0}
    delay =1
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}
    current_left = 1
    def __init__(self, latency):
        self.delay=latency
        self.current_left=latency
    def run(self,data_memory,GPR,scoreboard):
        file1.write("MEMORY: "+str(self.registers['ir'])+'\n')
        if(self.registers['ir']==0):
            print("NOP in memory")
            self.current_left=0
            return
        if(not(self.signals['isST'] or self.signals['isLW'] or self.signals['isLOADNOC'] or self.signals['isSTORENOC'])):
            self.current_left=0
            print("signals")
            print(self.signals)
            print("registers")
            print(self.registers)
            print("cycles left: ",self.current_left)
            return
        self.current_left = self.current_left-1
        print("signals")
        print(self.signals)
        print("registers")
        print(self.registers)
        print("cycles left: ",self.current_left)
        if(self.signals['isLW'] and (self.current_left==0)):
            self.registers['mem_res'] = data_memory.read_memory(self.registers['res']>>2)
            file1.write("MA:"+str(self.registers['res']>>2)+'\n')
            scoreboard.pending[self.registers['rd']] = False
            scoreboard.value[self.registers['rd']] = self.registers['mem_res']
        if((self.signals['isST'] or self.signals['isLOADNOC']) and (self.current_left==0)):
            # self.data_memory[res>>2] = self.GPR[registers['rs2']]
            data_memory.write_memory(self.registers['res']>>2,GPR.read_reg(self.registers['rs2']))
            file1.write("MA:"+str(self.registers['res']>>2)+'\n')
        if(self.signals['isSTORENOC']and (self.current_left==0)):
            file1.write("MA:"+str(4100)+'\n')
            data_memory.write_memory(4100,1) # 4010 hex byte = 16^3+4 decimal word (4bytes)

class Writeback():
    signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,'isSTORENOC':0, 'isLOADNOC':0}
    clock =0
    registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}

    def run(self,GPR):
        print("WRITEBACK")
        file1.write("WRITEBACK: "+str(self.registers['ir'])+'\n')
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

class Scoreboard():
    pending = [False]*32
    value = [0]*32

    def __init__(self,GPR):
        for i in range(32):
            self.value[i]=GPR.read_reg(i)
    
    def __str__(self):
        for i in range(32):
            print("reg: ",i," value: ",self.value[i]," pending: ",self.pending[i])
        return ""


class CPU():
    clock=0
    instruction_memory ={}
    data_memory=[]
    GPR=[]
    scoreboard=0
    PC=0
    fetch_unit=0
    decode_unit=0
    execute_unit=0
    memory_unit=0
    writeback_unit=0
    stall = False
    stash = False
    branch_target=0

    def __init__(self, im, dm, reg):
        self.instruction_memory = im
        self.data_memory = dm
        self.GPR = reg
        self.scoreboard = Scoreboard(self.GPR)
        self.fetch_unit= Fetch()
        self.decode_unit= Decode()
        self.execute_unit= Execute()
        self.memory_unit = Memory(3)
        self.writeback_unit= Writeback()

    def fetch(self):
        self.fetch_unit.run(self.instruction_memory,self.PC)

    def decode(self):
        (self.stall,self.stash,self.branch_target)  = self.decode_unit.run(self.GPR,self.scoreboard)
        
    def execute(self):
        self.execute_unit.run(self.GPR,self.scoreboard)
        
    def memory(self):
        self.memory_unit.run(self.data_memory,self.GPR,self.scoreboard)
            
    def writeback(self):
        self.writeback_unit.run(self.GPR)
            
    def transfer_sig(self):

        if(self.memory_unit.current_left>0): # we need to stall memory in next cycle, give NOP to writeback 
            self.writeback_unit.signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0, 'isSTORENOC':0, 'isLOADNOC':0}
            self.writeback_unit.registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}
        else:  #propagate memory signals to writeback
            self.writeback_unit.signals = self.memory_unit.signals.copy()
            self.writeback_unit.registers = self.memory_unit.registers.copy()
            self.memory_unit.signals = self.execute_unit.signals.copy()
            self.memory_unit.registers = self.execute_unit.registers.copy()
            self.memory_unit.current_left = self.memory_unit.delay

            if(self.stall):
                self.execute_unit.signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0, 'isSTORENOC':0, 'isLOADNOC':0}
                self.execute_unit.registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}
            else:
                self.execute_unit.signals=self.decode_unit.signals.copy()
                self.execute_unit.registers=self.decode_unit.registers.copy() 
                if(not self.stash):
                    self.decode_unit.signals = self.fetch_unit.signals.copy()
                    self.decode_unit.registers = self.fetch_unit.registers.copy()
                else:
                    self.decode_unit.signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0, 'isSTORENOC':0, 'isLOADNOC':0}
                    self.decode_unit.registers={'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0,'mem_res':0,'res':0}

        
            
            




    def cpu_clock_edge(self):
        file1.write("Cycle no: "+str(self.clock)+'\n')
        print("Cycle no: ", self.clock)
        #if stalling in memory stage execute only memory and writeback
        if(self.memory_unit.current_left<self.memory_unit.delay):
            file1.write("StallM "+str(self.clock)+"\n")
            self.memory()
            self.writeback()
            self.transfer_sig()
        
        #elif stalling in decode, execute decode to writeback only (stash can't be issued if decode is stalling)
        elif(self.stall):
            file1.write("StallD "+str(self.clock)+"\n")
            self.decode()
            self.execute()
            self.memory()
            self.writeback()
            self.transfer_sig()
        
        #no stalls
        else:
            if(self.stash):
                print("reached stash")
                self.PC = self.PC+self.branch_target
            print("FETCHING from ",self.PC)
            self.fetch()
            self.PC = self.PC+4
            self.decode()
            self.execute()
            self.memory()
            self.writeback()
            self.transfer_sig()

        
        print("GPR")
        print(self.GPR.GPR)
        print("Scoreboard")
        print(self.scoreboard)
        print("data memory")
        for i in range(len(self.data_memory.data_memory)):
            if(self.data_memory.read_memory(i)!=0):
                print(i,' : ',self.data_memory.read_memory(i))
        
        file1.write("GPR\n")
        file1.write(json.dumps(self.GPR.GPR))
        file1.write('\n')
        self.clock +=1




file1 = open("myfile.txt", "w")
instruction_memory = InstructionMemory()
data_memory = DataMemory()
GPR = Registers()
for i in range(32):
    GPR.write_reg(i,i)
my_cpu = CPU(instruction_memory,data_memory,GPR)
with open(sys.argv[1]) as file:
    lines = [line.rstrip() for line in file]

for i in range(len(lines)):
    instruction_memory.write_memory(4*i,lines[i][0:32])
# for i in range(5):
while(my_cpu.PC<4*len(lines)):
    my_cpu.cpu_clock_edge()
file1.write("Ending memory state: \n")
for i in range(len(data_memory.data_memory)):
    file1.write(str(i)+' : '+str(data_memory.read_memory(i))+'\n')
file1.write('\n')
file1.close()




# file1.write("Cycle no: "+ str(self.clock)+'\n')
#         file1.write("signals"+'\n')
#         file1.write(json.dumps(self.writeback_unit.signals))
#         file1.write('\n')
#         file1.write("GPR\n")
#         file1.write(json.dumps(self.GPR.GPR))
#         file1.write('\n')
#         file1.write("registers\n")
#         file1.write(json.dumps(self.writeback_unit.registers))
#         file1.write('\n')
#         file1.write("data memory\n")
#         for i in range(len(self.data_memory.data_memory)):
#             if(self.data_memory.read_memory(i)!=0):
#                 file1.write(str(i)+' : '+str(self.data_memory.read_memory(i))+'\n')
#         file1.write('\n')
#         file1.write('\n')
#         file1.write('\n')
#         print()
#         print()
#         print()