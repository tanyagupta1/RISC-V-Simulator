# byte addressable
# instruction_memory={0:'00000000011100110000001010110011'}#add x5,x6,x7
# instruction_memory={0:'11111100111000001000011110010011'} #addi x15,x1,-50
# instruction_memory={0:'00000000100000010010011100000011'} #lw x14, 8(x2)
# instruction_memory={0:'00000000111000010010010000100011'} #st x14, 8(x2)

# instruction_memory={0:'00000000101010011000100001100011'} #beq x19,x10,16 (bytes)

# instruction_memory={0:'00000000000000000000000001111011'} #STORENOC
# instruction_memory={0:'00000000001000001000010001111111'} #LOADNOC R1,R2,8


# instruction_memory={0:'00000000011100110000001010110011',
# 4:'11111100111000001000011110010011',
# 8:'00000000100000010010011100000011',
# 12:'00000000111000010010010000100011',
# 16:'00000000000000000000000001111011',
# 20:'00000000001000001000010001111111'} 

# instruction_memory={0:'00000000101010011000100001100011'} #beq x19,x10,16 (bytes)


#
# 1111011 -> STORENOC
# 1111111 -> LOADNOC
# LOADNOC is imm[11:5] rs2 rs1 000 imm[4:0] 1111111

import sys
data_memory=[0]*5000
GPR = [0]*32
registers={'pc':0,'ir':0,'I':0,'rd':0,'rs1':0,'rs2':0,'immx':0}
signals={'isImm':0,'isAdd':0,'isSub':0,'isAnd':0,'isOr':0,'isSLL':0,'isSRA':0,'isLW':0,'isST':0,'isBEQ':0,
'isSTORENOC':0, 'isLOADNOC':0}
mem_res=0
op1=0
op2=0
res=0
def fetch():
    PC = registers['pc']
    registers['ir'] = instruction_memory[PC]

def decode():
    global signals
    signals = dict.fromkeys(signals, 0)
    registers['rd'] = int(registers['ir'][20:25],2)
    registers['rs1'] = int(registers['ir'][12:17],2)
    registers['rs2'] = int(registers['ir'][7:12],2)
    #calculating immediate
    registers['immx']=0
    if(registers['ir'][0]=='1'):
        registers['immx']=-2048
    if((registers['ir'][25:32]=='0000011') or (registers['ir'][25:32]=='0010011')):
        registers['immx']+=int(registers['ir'][1:12],2)
    elif((registers['ir'][25:32]=='0100011') or (registers['ir'][25:32]=='1111111')):
        registers['immx']+=int(registers['ir'][1:7]+registers['ir'][20:25],2)
    elif(registers['ir'][25:32]=='1100011'):
        registers['immx']=int(registers['ir'][0]+registers['ir'][24]+registers['ir'][1:7]+registers['ir'][20:24],2)


    #sending signals
    if(registers['ir'][25:32]=='0110011'):
        if(registers['ir'][17:20]=='111'):
            signals['isAnd']=1
        if(registers['ir'][17:20]=='110'):
            signals['isOr']=1
        if((registers['ir'][17:20]=='000') and (registers['ir'][0:7]=='0000000')):
            signals['isAdd']=1
        if((registers['ir'][17:20]=='000') and (registers['ir'][0:7]=='0100000')):
            signals['isSub']=1
        if(registers['ir'][17:20]=='001'):
            signals['isSLL']=1
        if(registers['ir'][17:20]=='101'):
            signals['isSRA']=1
    elif (registers['ir'][25:32]=='1111011'):
        signals['isSTORENOC']=1
    else:
        signals['isImm']=1
        if(registers['ir'][25:32]=='0000011'):
            signals['isLW']=1
        if(registers['ir'][25:32]=='0100011'):
            signals['isST']=1
        if(registers['ir'][25:32]=='0010011'):
            signals['isAdd']=1
        if(registers['ir'][25:32]=='1100011'):
            registers['immx'] = registers['immx']*2
            if(GPR[registers['rs1']]==GPR[registers['rs2']]):
                signals['isBEQ']=1
        if(registers['ir'][25:32]=='1111111'):
            signals['isLOADNOC'] = 1
    
def execute():
    global op1,op2,res
    op1 = GPR[registers['rs1']]
    op2 = GPR[registers['rs2']]
    if(signals['isImm']):
        op2 = registers['immx']
    if(signals['isAdd'] or signals['isLW'] or signals['isST'] or signals['isLOADNOC']):
        res = op1+op2
    if(signals['isSub']):
        res = op1-op2
    if(signals['isAnd']):
        res = op1 & op2
    if(signals['isOr']):
        res = op1 | op2
    if(signals['isSLL']):
        res = op1 << op2
    if(signals['isSRA']):
        res = op1 >> op2
    print("op1: ",op1, " op2: ",op2, " res: ",res)

def memory():
    global mem_res
    if(signals['isLW']):
        mem_res = data_memory[res>>2]
    if(signals['isST'] or signals['isLOADNOC']):
        data_memory[res>>2] = GPR[registers['rs2']]
    if(signals['isSTORENOC']):
        data_memory[4100]=1 # 4010 hex byte = 16^3+4 decimal word (4bytes)
   
def writeback():
    global res, mem_res
    if(signals['isLW']):
        GPR[registers['rd']] = mem_res
    if(signals['isOr']or signals['isAnd'] or signals['isSLL'] or signals['isSRA'] or signals['isAdd'] or signals['isSub']):
        GPR[registers['rd']] = res
        #update PC
    if(signals['isBEQ']==1):
        registers['pc'] = registers['pc']+registers['immx']
    else:
        registers['pc'] = registers['pc']+4

        


def CPU():
    fetch()
    decode()
    execute()
    memory()
    writeback()
GPR[1] = 16384
GPR[2] = 4444

with open(sys.argv[1]) as file:
    lines = [line.rstrip() for line in file]
instruction_memory={}
for i in range(len(lines)):
    instruction_memory[4*i] = lines[i]
for i in range(len(lines)):
    CPU()
    print(signals)
    print(registers)
    print(GPR)
    for i in range(len(data_memory)):
        if(data_memory[i]!=0):
            print(i,' : ',data_memory[i])
