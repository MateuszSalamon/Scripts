

#random hex with spaces

#diag_input = input('input diagjob value:\n')
diag_input = "08 A5 E6 C3 34 94 65 97 84 51 32 65 A6 A1 B3 B8 C9 45 D6 7F 56 97 A2 45 D1 23 56 44 98 21 12 3A 6B C2 91 76 83 25 55 64 CF 12 54 87 EE CC AA"

print("diag input ", diag_input)
def make_into_hex(in_str):
    in_str = in_str.replace(' ', '')
    k = 0 #initialize counter
    h = 6 #first line has fewer elements
    m = 6 #reset newline every m elements
    for i in range(0, len(in_str), 2):
        out_str = '0x'+in_str[i:i+2]
        if(i <= h): #first 5 bytes then new line
            print("ld_p_arr["+str(int(i/2))+"] = "+'0x'+in_str[i:i+2]+';', end=' ')
        elif(i > h):#rest of the bytes grouped by 6
            if(k % m):
                print("ld_p_arr[" + str(int(i / 2)) + "] = " + '0x' + in_str[i:i + 2] + ';', end=' ')
                k += 1;
            else:#every 6th line has new line symbol
                print("ld_p_arr[" + str(int(i / 2)) + "] = " + '0x' + in_str[i:i + 2] + ';')
                k += 1;

if len(diag_input) > 6:
    #diag_input_length_str = str(hex(len(diag_input) + 2)).replace('0x','' )
    #payload_out = '56 10 ' + diag_input_length_str + ' 31 01 --->' + diag_input[3:len(diag_input)]
    #print("diag output ", payload_out)

    make_into_hex(diag_input)



