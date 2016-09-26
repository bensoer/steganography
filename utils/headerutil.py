import logging
import math

logger = logging.getLogger("stego")


def calculateMaxStorageCapacity(carrierFileBytes):
    '''
    calculateMaxStorageCapacity Detemines the maximum amount of data that can be stored in the passed in carrier
    image. This calculation includes leaving enough space for the header data needed for the size of data image
    that could be stored within the image. All calculations use cautious metrics so as to allow extra room for
    the header
    :param carrierImg: DCImage - A wrapper of the Pillow Image object representing an image file
    :return: Tuple(int, int) - The tuple's first value contains the maxDataBytes that can be stored in the carrier
    image, leaving enough room for the required header. The tuple's second value is then how many bits will be
    needed in the header in order to store the max data bytes value. Note that cautious calculations means the bits
    needed may be equal to or greater the the space needed to represent the max data byte value. So

            maxDataBytes <= 2 ^ bitsNeededToRepresentMaxDataBytes

            where:
            Tuple(maxDataBytes, bitsNeededToRepresentMaxDataBytes)
    '''


    maxDataBytes = math.floor(carrierFileBytes / 8)  # as 8 bytes of carrier file is needed for 1 byte of data image

    # find how many bits are needed to represent this total
    bitsToRepresentMaxDataBytes = math.ceil(math.log2(maxDataBytes))

    # round this up to the highest number of pixels this will need
    pixelsNeedToRepresentMaxDataBytes = math.ceil(bitsToRepresentMaxDataBytes / 3)
    # recalculate bits as we may have rounded up
    bitsToRepresentMaxDataBytes = pixelsNeedToRepresentMaxDataBytes * 3

    # now from this max subtract header data space needed
    maxDataBytes = maxDataBytes - math.ceil(
        (bitsToRepresentMaxDataBytes / 8))  # round up so that more is taken for header

    return (maxDataBytes, bitsToRepresentMaxDataBytes)