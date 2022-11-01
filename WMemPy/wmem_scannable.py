# pylint: disable=c-extension-no-member
"""Scannable classes are used to represent live memory of a process that can be scanned"""
import os
import ctypes
import win32process
import numpy as np
from wmempy.wmem_structs import MODULEINFO

class ProcScannable:
    """
    Scannable interface has to be implemented if you want to execute scans on the class.
    """
    def get_bounds(self):
        """
        Get base address and size of the scannable (valid memory region)

        :returns: starting index in memory and size of the Scannable
        :rtype: [int, int]
        """
        raise NotImplementedError('Interface ProcScannable not implemented.')

    def read(self):
        """
        Reads valid memory region of the scannable

        :returns: the entire memory of the Scannable
        :rtype: numpy.array of uint8
        """
        raise NotImplementedError('Interface ProcScannable not implemented.')

    def read_from(self, address):
        """
        Reads valid memory region of the scannable from given offset

        :param address: index from which to start the read operation
        :type address: int
        :returns: the entire memory of the Scannable
        :rtype: numpy.array of uint8
        """
        raise NotImplementedError('Interface ProcScannable not implemented.')

    def read_dtype(self, address, dtype):
        """
        Reads memory from address and interprets it as data type

        :param address: index at which the value should be read
        :param dtype: the data type into which the memory should be reinterpreted
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type that was read
        :rtype: ctypes data type
        """
        raise NotImplementedError('Interface ProcScannable not implemented.')

    def write_dtype(self, address, dtype):
        """
        Writes data type to memory at given address

        :param address: index at which the value should be read
        :param dtype: the data type into which the memory should be reinterpreted
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type to be written into memory
        :rtype: ctypes data type
        """
        raise NotImplementedError('Interface ProcScannable not implemented.')

class ProcPage(ProcScannable):
    """
    Represents a single virtual memory page of a process.
    """
    def __init__(self, proc, base, size):
        self.process = proc
        self.base_address = base
        self.size = size

    def get_bounds(self):
        """
        Page is represnted by base address and size only, this should never
        represent physical memory page

        :returns: starting index in memory and size of the Page
        :rtype: [int, int]
        """
        return [self.base_address, self.size]

    def read(self):
        """
        Read the entire page

        :returns: the entire memory of the Page
        :rtype: numpy.array of uint8
        """
        return self.process.reader.byte_arr(self.base_address, self.size)

    def read_from(self, address):
        """
        Read the entire page

        :param address: index from which to start the read operation
        :type address: int
        :returns: the entire memory of the Page
        :rtype: numpy.array of uint8
        """
        size = self.size - address
        if size > 0:
            return self.process.reader.byte_arr(self.base_address + address, self.size - address)
        return np.empty(shape=(0, 0))

    def read_dtype(self, address, dtype):
        """
        Read any data type from the page

        :param address: index at which the value should be read
        :param dtype: the data type into which the memory should be reinterpreted
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type that was read
        :rtype: ctypes data type
        """
        return self.process.reader.dtype(self.base_address + address, dtype)

    def write_dtype(self, address, dtype):
        """
        Write any data type into the page

        :param address: index at which the value should be read
        :param dtype: the data type into which the memory should be reinterpreted
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type to be written into memory
        :rtype: ctypes data type
        """
        return self.process.writer.dtype(self.base_address + address, dtype)

    def print(self):
        """
        Prints it's memory region
        """
        print(f'{hex(self.base_address)} - {hex(self.base_address + self.size)}')


class ProcModule(ProcScannable):
    """
    Represents a single module loaded by process.
    """
    def __init__(self, proc, handle):
        self.process = proc
        self.handle = handle
        self.path = win32process.GetModuleFileNameEx(self.process.handle, self.handle)
        minfo = MODULEINFO()
        ctypes.windll.psapi.GetModuleInformation(self.process.get_handle(), self.handle,
                                                 ctypes.byref(minfo), ctypes.sizeof(minfo))
        self.base_address = minfo.lpBaseOfDll
        self.size = minfo.SizeOfImage
        self.entry = minfo.EntryPoint

    def get_bounds(self):
        """
        Module has path (name), base address, size and entrypoint
        Entrypoint is what is called when the dll/so is loaded, but it can be obfuscated

        :returns: starting index in memory and size of the Module
        :rtype: [int, int]
        """
        return [self.base_address, self.size]

    def read(self):
        """
        Read the entire module

        :returns: the entire memory of the Module
        :rtype: numpy.array of uint8
        """
        return self.process.reader.byte_arr(self.base_address, self.size)

    def read_from(self, address):
        """
        Read the entire page

        :param address: index from which to start the read operation
        :type address: int
        :returns: the entire memory of the Module
        :rtype: numpy.array of uint8
        """
        size = self.size - address
        if size > 0:
            return self.process.reader.byte_arr(self.base_address + address, self.size - address)
        return np.empty(shape=(0, 0))

    def read_dtype(self, address, dtype):
        """
        Read any data type from the page

        :param address: index at which the value should be read
        :param dtype: the data type into which the memory should be reinterpreted
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type that was read
        :rtype: ctypes data type
        """
        return self.process.reader.dtype(self.base_address + address, dtype)

    def write_dtype(self, address, dtype):
        """
        Write any data type into the page

        :param address: index at which the value should be read
        :param dtype: the data type that should be interpreted into memory
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type to be written into memory
        :rtype: ctypes data type
        """
        return self.process.writer.dtype(self.base_address + address, dtype)

    def get_name(self):
        """
        Separate name from module path

        :returns: name of the Module without the path
        :rtype: string
        """
        return os.path.basename(self.path)

    def print(self):
        """
        Prints it's name and memory region
        """
        print(self.path)
        print(f'{hex(self.base_address)} - {hex(self.base_address + self.size)}')
