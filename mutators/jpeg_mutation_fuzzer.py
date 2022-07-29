from copy import deepcopy
from .mutator_base import MutatorBase
import random
import pwnlib.util.fiddling as bits


class jpegMutator(MutatorBase):
    """
        A fuzzer randomly generates inputs based on mutation of the seeds
        It implements python's generator
        
        Attributes:
            _content: 2D array that represents the cells of a csv
            shape: the dimensions of the csv (rows x cols)

    """

    def __init__(self, seed: bytes):
        """
        Args:
            seed: the seed csv bytes to mutate from
        """
        super().__init__(seed)
        self._content = seed
        
    
    def _mutte_insert_comment(self):
        #print("poop")
        data = self._content
        
        comment = b''
        
        for i in range(64):
          comment += random.randint(0, 0xFF).to_bytes(1, 'little')
        
        #print(data[0:10])
        data = data[:2] + b'\xFF' + b'\xFE' + b'\x00' + b'\x42' + comment + data[2:]
        #print(data[0:10])
        self._content = data
        return data
        
    def _muate_insert_ff(self):
        data = self._content
        
        #print(data[0:10])
        data = data[:2] + b'\xFF' + b'\x00' + data[2:]
        #print(data[0:10])
        self._content = data
        return data
        
    def _mutae_insert_at_end(self):
        data = self._content
        
        comment = b''
        
        for i in range(64):
          comment += random.randint(0, 0xFF).to_bytes(1, 'little')
          
        data += comment
        self._content = data
        return data
    
    
    def _mutate_get_jpeg_size(self):
        data = self._content
        data_size=len(data)
        i = 0   # Keeps track of the position within the file
        i += 4
        if data[i+2] == ord('J') and data[i+3] == ord('F') and data[i+4] == ord('I') and data[i+5] == ord('F') and data[i+6] == 0x00:
          #Retrieve the block length of the first block since the first block will not contain the size of file
          block_length = data[i] * 256 + data[i+1]
          while (i < data_size):
            i += block_length               # Increase the file index to get to the next block
            if i >= data_size: return False;   # Check to protect against segmentation faults
            if data[i] != 0xFF: return False;   #Check that we are truly at the start of another block
            if data[i+1] == 0xC0:          # 0xFFC0 is the "Start of frame" marker which contains the file size
              
              num = b'\x01'
              pos = i+6
              data = data[:pos] + num + data[pos + 1:]
              data = data[:pos - 1] + num + data[pos:]
              
              height = data[i+5]*256 + data[i+6]
              width = data[i+7]*256 + data[i+8]
              #print(height, width)
              self._content = data
              return height, width
            else:
              i += 2;                              #Skip the block marker
              block_length = data[i] * 256 + data[i+1]   #Go to the next block
          return False                   #If this point is reached then no size was found
        else:
          return False                  #Not a valid JFIF string not a valid SOI header
      
  
    def format_output(self, raw):
        return self._content