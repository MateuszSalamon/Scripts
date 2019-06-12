poi = 0
uyt = 0
ID = 3
#   0000x00x0
#   00000000
#   9 8 7 6 4 3 1
p = [2,4,8,16,32,64,128,256,512]
taskID = [27, 40, 50, 51]
tabi = [0,0,0,0]
tab2 = [0b1100101,
        0b10100000,
        0b11000100,
        0b11000101]
        #0000x00x0
        #000110011 //51
        #011000101  //51<<

base = taskID[ID]
mul = taskID[ID] * 4    #shift by 2b
poi = mul & 0xFF0       #cut 4 LSb

mul = taskID[ID] * 2    #shift by 1b
uyt = mul & 0x0F        #cut to 4 bits

mul = poi | uyt         #binary fusion

if(taskID[ID]%2 == 1):  #if odd
    mul |= (1<<0)       #assign 1 at LSb

mul &= ~(0x12<<0)       #clear for 0000x00x0

print(bin(mul))


tabi[ID] = mul

print(bin(tabi[ID]), " : ", bin(tab2[ID]))

print("orig: ",base)
print("tab:  ",bin(taskID[ID]))
print("base: ",bin(base))

def test():
    if(tabi[ID] == tab2[ID]):
        print("test pass")
    else:
        print("test fail")

test()