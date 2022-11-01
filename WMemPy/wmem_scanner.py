# pylint: disable=no-self-use,invalid-name
"""Scanner provides algorithms that run on top of scannable modules"""
import numpy as np


class ProcScanner:
    """
    Allows to run scans on Scannables
    """
    def __init__(self, proc):
        self.process = proc

    def array_from_pattern(self, pattern, base, separator):
        """
        Creates a numpy array from string, wildcard can be either * or ?
        Supports any base and any separator for use across all pattern styles

        :param pattern: bytes of the pattern separated by separator, * or ? for any value
        :param base: base of the bytes
        :param separator: separator that is used to separate bytes
        :type pattern: string
        :type base: int
        :type separator: char
        :returns: the bytes in the string as numpy array, wild card is -1
        :rtype: numpy.array of ints
        """
        pattern = pattern.replace('?', '-1')
        pattern = pattern.replace('*', '-1')
        return np.array([int(x, base) for x in pattern.split(separator)])

    def array_from_ascii(self, ascii_string):
        """
        Creates a numpy array from ASCII string

        :param ascii_string: string to be converted into byte array
        :type ascii_string: string
        :returns: byte array where each character of original string is converted to int
        :rtype: numpy.array of ints
        """
        return np.array([ord(c) for c in ascii_string])

    def is_subsequence(self, memory, pattern):
        """
        Sequence contains subsequence problem, linear solution

        :param memory: byte array of memory to scan for pattern
        :param pattern: byte array to look for in the memory
        :type memory: numpy.array of ints
        :type pattern: numpy.array of ints
        :returns: index in memory where the sequence was found or None if it does not exist
        :rtype: int or None
        """
        i = 0
        j = 0
        mem_len = len(memory)
        pat_len = len(pattern)

        # While not at the end of memory and not at the end of pattern
        while (i < mem_len and j < pat_len):
            # If wildcard or chars match, move both iterators
            if (pattern[j] == -1 or memory[i] == pattern[j]):
                i += 1
                j += 1
                # If whole pattern was iterated over, success
                if j == pat_len:
                    return i - pat_len
            # If chars don't match, return back where match was first found
            else:
                i = i - j + 1
                j = 0

        # If we went through the whole thing without success, fail
        return None

    def byte_scan(self, scannable, byte_arr):
        """
        Checks if memory contains the byte array

        :param scannable: what you want to scan
        :param byte_arr: array of bytes that should be found in scannable
        :type scannable: Scannable
        :type byte_arr: numpy.array of ints
        :returns: index in Scannable where the sequence was found or None otherwise
        :rtype: int or None
        """
        # Read the scannable's memory
        memory = scannable.read()
        if memory is None:
            return None
        # Check if pattern is in memory
        return self.is_subsequence(memory, byte_arr)

    def AOB_scan_arr(self, scannable_array, pattern, base=16, separator=' '):
        """
        Looks for a pattern inside an array of Scannables of the current process

        :param scannable_array: array of what you want to scan
        :param pattern: bytes of the pattern separated by separator, * or ? for any value
        :param base: base of the bytes
        :param separator: separator that is used to separate bytes
        :type scannable_array: list of Scannable
        :type pattern: string
        :type base: int
        :type separator: char
        :returns: index in Scannable where the sequence was found and the Scannable
        :rtype: int, Scannable
        """
        for scannable in scannable_array:
            result = self.AOB_scan(scannable, pattern, base, separator)
            if not result is None:
                return result, scannable
        return None, None

    def AOB_scan(self, scannable, pattern, base=16, separator=' '):
        """
        Checks if memory range contains given pattern

        :param scannable: what you want to scan
        :param pattern: bytes of the pattern separated by separator, * or ? for any value
        :param base: base of the bytes
        :param separator: separator that is used to separate bytes
        :type scannable: Scannable
        :type pattern: string
        :type base: int
        :type separator: char
        :returns: index in Scannable where the sequence was found or None otherwise
        :rtype: int or None
        """
        # Generate numpy array from pattern string
        to_find = self.array_from_pattern(pattern, base, separator)
        return self.byte_scan(scannable, to_find)

    def ASCII_scan_arr(self, scannable_array, ascii_string):
        """
        Looks for an ASCII string inside an array of Scannables of the current process

        :param scannable_array: array of what you want to scan
        :param ascii_string: string to be searched for in the Scannable
        :type scannable_array: list of Scannable
        :type ascii_string: string
        :returns: index in Scannable where the sequence was found and the Scannable
        :rtype: int, Scannable
        """
        for scannable in scannable_array:
            result = self.ASCII_scan(scannable, ascii_string)
            if not result is None:
                return result, scannable
        return None, None

    def ASCII_scan(self, scannable, ascii_string):
        """
        Checks if memory range contains given ASCII string

        :param scannable:  what you want to scan
        :param ascii_string: string to be searched for in the Scannable
        :type scannable: Scannable
        :type ascii_string: string
        :returns: index in Scannable where the sequence was found
        :rtype: int
        """
        # Generate numpy array from ASCII string
        to_find = self.array_from_ascii(ascii_string)
        return self.byte_scan(scannable, to_find)

    def ASCII_list_arr(self, scannable_arr, symbols=False, min_length=3):
        """
        Creates a list of all ASCII strings in an array of scannables

        :param scannable_arr: array of what you want to scan
        :param symbols: whether to include symbols or not
        :param min_length: minimum length of the string to be included
        :type scannable_arr: list of Scannable
        :type symbols: boolean
        :type min_length: int
        :returns: strings matching the length and symbols in the Scannables
        :rtype: list of strings
        """
        result = []
        for scannable in scannable_arr:
            tmp = self.ASCII_list(scannable, symbols, min_length)
            if not (tmp is None) and len(tmp) > 0:
                result.append(tmp)
        return [item for sublist in result for item in sublist]

    def ASCII_list(self, scannable, symbols=False, min_length=3):
        """
        Creates a list of all ASCII strings in a scannable

        :param scannable: what you want to scan
        :param symbols: whether to include symbols or not
        :param min_length: minimum length of the string to be included
        :type scannable: Scannable
        :type symbols: boolean
        :type min_length: int
        :returns: strings matching the length and symbols in the Scannable
        :rtype: list of strings
        """
        result = []
        # Read the scannable's memory
        memory = scannable.read()
        if memory is None:
            return None
        # For symbols, only remove special symbols like line endings and reserved bytes
        if symbols:
            condition = (memory <= 32) | (memory >= 127)
        # Otherwise, only allow a-z A-Z 0-9
        else:
            condition = (memory <= 47) | ((memory >= 58) & (memory <= 64)) | \
                        ((memory >= 91) & (memory <= 96)) | (memory >= 123)
        # Apply condition
        memory = np.where(condition, 0, memory)
        # Get bitmap for zero elements
        iszero = np.concatenate(([0], np.greater(memory, 0).view(np.int8), [0]))
        # Diff gets us boundaries
        absdiff = np.abs(np.diff(iszero))
        # Split boundaries into separate array for each word
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        # Iterate over all potential words
        for word in ranges:
            # Filter by length
            if word[1] - word[0] >= min_length:
                # Get the ASCII byte array
                ascii_word = memory[word[0]:word[1]]
                # Convert it to string and append it to results
                result.append("".join([chr(item) for item in ascii_word]))

        return result
