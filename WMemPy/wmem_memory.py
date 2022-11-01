# pylint: disable=broad-except,too-few-public-methods
"""Classes for working with process memory"""
import ctypes
import numpy as np

class ProcReader:
    """
    Allows to read the memory of a process
    """
    def __init__(self, proc):
        self.process = proc

    def byte_arr(self, address, size):
        """
        Read a byte array of the process

        :param address: index in the process virtual memory to read from
        :param size: amount of bytes to read
        :type address: int
        :type size: int
        :returns: array of bytes that were read from the memory
        :rtype: numpy.array of uint8
        """
        # Allocate buffer for single ReadProcessMemory operation
        buffer = ctypes.create_string_buffer(size)
        # How many bytes were read by the syscall
        bytes_read = ctypes.c_size_t()
        # RPM has to be called in a single call because it is extremely inefficient syscall
        # In regular WinApi if the call fails it returns 0 (you use GetLastError to get the problem)
        # In ctypes version, it can throw exception as well as fail with 0 and also partially fail
        try:
            if not ctypes.windll.kernel32.ReadProcessMemory(self.process.get_handle(), address,
                                                           buffer, size, ctypes.byref(bytes_read)):
                # Regular fail (for example called on null handle)
                return None
        except Exception:
            # Exception fail I haven't been able to produce
            return None
        if bytes_read.value != size:
            # Partial RMP fail, only some data are read, this should not happen normally, only
            # in the kernel call versions (Zw)
            return None
        # Convert the char buffer to numpy array
        return np.ctypeslib.as_array(buffer).view(np.uint8)

    def dtype(self, address, dtype):
        """
        Read any ctypes data type of the process

        :param address: index at which the value should be read
        :param dtype: the data type into which the memory should be reinterpreted
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type that was read
        :rtype: ctypes data type
        """
        # Get reference for ReadProcessMemory operation
        buffer = ctypes.byref(dtype)
        # Get the amount of bytes to be read
        size = ctypes.sizeof(dtype)
        # How many bytes were read by the syscall
        bytes_read = ctypes.c_size_t()
        # RPM has to be called in a single call because it is extremely inefficient syscall
        # In regular WinApi if the call fails it returns 0 (you use GetLastError to get the problem)
        # In ctypes version, it can throw exception as well as fail with 0 and also partially fail
        try:
            if not ctypes.windll.kernel32.ReadProcessMemory(self.process.get_handle(), address,
                                                           buffer, size, ctypes.byref(bytes_read)):
                # Regular fail (for example called on null handle)
                return None
        except Exception:
            # Exception fail I haven't been able to produce
            return None
        if bytes_read.value != size:
            # Partial RMP fail, only some data are read, this should not happen normally
            # only in the kernel call versions (Zw)
            return None
        # Return the value
        return dtype.value


class ProcWriter:
    """
    Allows to write the memory of a process
    """
    def __init__(self, proc):
        self.process = proc

    def dtype(self, address, dtype):
        """
        Write any ctypes data type into the process

        :param address: index at which the value should be read
        :param dtype: the data type that should be interpreted into memory
        :type address: int
        :type dtype: ctypes data type class
        :returns: the data type to be written into memory
        :rtype: ctypes data type
        """
        # Get reference for WriteProcessMemory operation
        buffer = ctypes.byref(dtype)
        # Get the amount of bytes to be written
        size = ctypes.sizeof(dtype)
        # How many bytes were written by the syscall
        bytes_read = ctypes.c_size_t()
        # WPM has to be called in a single call because it is extremely inefficient syscall
        # In regular WinApi if the call fails it returns 0 (you use GetLastError to get the problem)
        # In ctypes version, it can throw exception as well as fail with 0 and also partially fail
        try:
            if not ctypes.windll.kernel32.WriteProcessMemory(self.process.get_handle(), address,
                                                            buffer, size, ctypes.byref(bytes_read)):
                # Regular fail (for example called on null handle)
                return None
        except Exception:
            # Exception fail I haven't been able to produce
            return None
        if bytes_read.value != size:
            # Partial WPM fail, only some data are written, this should not happen normally
            # only in the kernel call versions (Zw)
            return None
        # On successful write, return the value written
        return dtype.value
    