import logging
import sys
import os

from utils import headerutil

from utils.argparcer import ArgParcer

# Setup Logging
logger = logging.getLogger("stego")
logger.setLevel(logging.DEBUG)
#console logging channel
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s(%(levelname)s) - %(message)s', "%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Parse Command Arguments
mode = ArgParcer.getValue(sys.argv, "-m") # mode can be either 'stego' or 'unstego'
carrierFileDir = ArgParcer.getValue(sys.argv, "-c") # dir path to the carrier image
dataFileDir = ArgParcer.getValue(sys.argv, "-d") # dir path to the data image - this image will be hidden into the carrier
outputFileDir = ArgParcer.getValue(sys.argv, "-o")

if outputFileDir == "":
    logger.fata("Output File Location Required To Stego/UnStego File. Terminating")
    exit(1)

if ArgParcer.keyExists(sys.argv, "--DEBUG"):
    ch.setLevel(logging.DEBUG)

if mode == "stego":
    logger.info("Stego Mode Selected. Merging Data File Into Carrier")

    # get the data file size
    dataFileByteSize = None
    carrierFileByteSize = None
    try:
        dataFileByteSize = os.path.getsize(dataFileDir)
    except:
        logger.fatal("Could Not Find Or Open Data File. Aborting")
        exit(1)
    try:
        carrierFileByteSize = os.path.getsize(carrierFileDir)
    except:
        logger.fatal("Could Not Find Or Open Carrier File. Aborting")
        exit(1)

    logger.info("Confirmed Carrier And Data File. Now Calculating Size Limitations")
    # generate the header data relative to carrier
    maxDataBytes, bitsNeededToRepresent = headerutil.calculateMaxStorageCapacity(carrierFileByteSize)

    logger.info("Size Calculations Complete. Now Parsing...")
    with open(carrierFileDir, 'rb') as c:
        with open(dataFileDir, 'rb') as d:
            with open(outputFileDir, 'wb') as o:

                logger.info("Parsing Header Content From Carrier")
                # move to end point of the header
                c.seek(bitsNeededToRepresent)
                headerBytes = list()

                # pull out carrier bytes and adjust carrier LSB to equal to dataFileBytesSize LSB
                # print it in backwards so that padded 0's will do nothing and fill in the extra space
                while c.tell() > 0:
                    byte = c.read(-1)
                    intByte = int.from_bytes(byte, sys.byteorder)

                    lsb = (dataFileByteSize & 1)
                    if lsb == 1:
                        intByte |= 1
                    else:
                        intByte &= ~1

                    headerBytes.insert(0, intByte.to_bytes(1, sys.byteorder))

                    dataFileByteSize >>= 1

                # write the header bytes into the output file
                for byte in headerBytes:
                    o.write(byte)

                # load the rest of the data into the carrier
                c.seek(bitsNeededToRepresent) # move back to the end spot
                dByte = d.read(1)
                while dByte:
                    for dBit in dByte:
                        cByte = c.read(1)
                        if dBit == 1:
                            cByte |= 1
                        else:
                            cByte &= ~1

                        o.write(cByte)
                    dByte = d.read(1)

elif mode == "unstego":

    carrierFileByteSize = None
    try:
        carrierFileByteSize = os.path.getsize(carrierFileDir)
    except:
        logger.fatal("Could Not Find Or Open Carrier File. Aborting")
        exit(1)

    # generate the header data relative to carrier
    maxDataBytes, bitsNeededToRepresent = headerutil.calculateMaxStorageCapacity(carrierFileByteSize)

    with open(carrierFileDir, 'rb') as c:
        with open(outputFileDir, 'wb') as o:

            #read out the header to determine data file size
            dFileSize = 0
            while c.tell() < bitsNeededToRepresent:
                dFileSize <<= 1
                hByte = c.read(1)
                lsb = (hByte & 1)
                if lsb == 1:
                    dFileSize |= 1
                else:
                    dFileSize &= ~1

            # now read out the data file until we have read the dFileSize amount of data

            while (o.tell() * 8) < dFileSize:

                dByte = 0
                for i in range(0,8):
                    dByte <<= 1
                    cByte = c.read(1)
                    lsb = (cByte & 1)
                    if lsb == 1:
                        dByte |= 1
                    else:
                        dByte &= ~1

                o.write(dByte.to_bytes(1, sys.byteorder))

else:
    logger.error("Mode not Specified or Not Supported. Can't Execute Any Action. Terminating")
    exit(0)