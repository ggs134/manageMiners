
# -*- coinding: utf-8 -*-
from pysnmp.entity.rfc3413.oneliner import cmdgen


def get_status(address, port):
    cmdGen = cmdgen.CommandGenerator()

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.UsmUserData('goldrush', authKey="authkey1", privKey="privkey1", authProtocol=cmdgen.usmHMACMD5AuthProtocol, privProtocol=cmdgen.usmDESPrivProtocol),
        cmdgen.UdpTransportTarget((address, port)),
        cmdgen.MibVariable('SNMPv2-SMI', 'enterprises', 42, 1, 0).addAsn1MibSource('./'),
        cmdgen.MibVariable('SNMPv2-SMI', 'enterprises', 42, 2, 0).addAsn1MibSource('./')
    )

    # Check for errors and print out results
    if errorIndication:
        print(errorIndication)
        return errorIndication
    else:
        if errorStatus:
            # print('%s at %s' % (
            #     errorStatus.prettyPrint(),
            #     errorIndex and varBinds[int(errorIndex)-1] or '?'
            #     )
            # )
            print(errorStatus.prettyPrint())
            return errorStatus
        else:
            result=[]
            for name, val in varBinds:
                # print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
                # print(val)
                result.append(val.prettyPrint())
    	    # print(errorStatus)
            # print varBinds
            # print errorIndication
            # print errorStatus
            # print result
            return result

def main():
    # get_status("onther.iptime.org", 161)
    po = {1:39,3:36,4:35,5:38,6:37,7:31,8:33,14:40,15:3,16:7,17:8,
    18:9,19:11,20:12,21:34,22:10,23:21,24:14,25:15,26:19,27:18,28:17,
    29:16,30:20,31:26,32:29,33:25,34:23,35:24,36:28,37:22,38:27}
    for i in po:
        print "miner"+str(i),get_status("192.168.0."+str(po[i]), 161)

if __name__ == "__main__":
    main()
