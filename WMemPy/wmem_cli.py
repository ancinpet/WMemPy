# pylint: disable=unnecessary-lambda,broad-except,raise-missing-from,no-value-for-parameter,too-many-arguments,unexpected-keyword-arg
"""CLI interface for WMemPy"""
import sys
import configparser
import click
import numpy as np
from wmempy.wmem_process import WinProc
from wmempy.wmem_system import WinSys


def array_from_where(process, where):
    """Get array of scannables from provided parameter"""
    if where == 'all':
        return process.pages
    if where == 'pages':
        return process.pages
    if where == 'modules':
        return process.modules
    if not where is None:
        return [module for module in process.modules if module.get_name().lower() == where.lower()]
    return process.pages

def readable(line):
    """
    Convert byte array to readable string representation, that
    means filter out unreadable symbols and replace others with dot
    """
    condition = (line <= 32) | (line >= 127)
    line = np.where(condition, 46, line)
    return line.tobytes().decode('ASCII').replace('\x00', '')

def memory_view_print(memory, address):
    """
    Print raw memory to console in a nice and readable format
    16 bytes per line like any other memory viewer
    """
    # Reshape memory to 16 bytes long arrays
    reshaped = np.reshape(memory,(-1,16))
    # Make sure numpy prints the entire array and doesn't short it
    # Also convert the hex to nice format (remove 0x in front)
    np.set_printoptions(formatter={'int':lambda x:'{:02x}'.format(x)}, threshold=sys.maxsize)
    address = address // 16 * 16
    # Print and also keep up with the address
    for line in reshaped:
        print(hex(address), line, readable(line))
        address += 16

def memory_view(process, view):
    """
    Allows to print out memory of process based on parameters
    """
    # Convert hint (supports both hex and decimals) if it exists
    base = 16 if view[1] and view[1][:2] else 10
    try:
        hint = int(view[1], base)
    except Exception:
        hint = 0
    # Get scannables that will be printed
    scannable_array = array_from_where(process, view[0])
    # Each scannable gets printed and is separated by line of Vs
    # to mimic the empty address space in between
    for scannable in scannable_array:
        hint_relative = hint
        # Hint can be either relative to the memory page or absolute
        # Here is decided what the user meant
        if hint >= scannable.size and hint >= scannable.base_address:
            hint_relative -= scannable.base_address
        # Always round down to 16 bytes so the memory is alligned properly
        hint_relative = (hint_relative // 16) * 16
        # Read the memory starting from the hint or 0
        memory = scannable.read_from(hint_relative)
        # If we were able to read some memory, print it
        # We don't get memory if the range was wrong or the page is protected
        if (not memory is None) and len(memory) > 1:
            memory_view_print(memory, scannable.base_address + hint_relative)
            print('vvvvvvvvvvvvvvvvvvv')

def text_list(process, list_text):
    """
    List all strings of given process based on parameters
    """
    params = list_text[0]
    # Hint here is used to only show words that contain it
    hint = list_text[2]
    # Params are in format 'x<number>' where x specifies if symbols should be used
    # (s = use, anything else means don't use them), number sets the minimum length
    # of the string
    if len(params) == 0:
        symbols = True
        min_length = 5
    else:
        symbols = params[0] == 's'
        try:
            min_length = int(params[1:])
        except Exception:
            min_length = 5
    # Get scannables that will be checked for strings
    scannable_array = array_from_where(process, list_text[1])
    try:
        result = process.scanner.ASCII_list_arr(scannable_array, symbols, min_length)
    except Exception:
        raise click.BadParameter('Invalid text list parameters.')
    # Print all strings
    print(f'Listing ASCII strings {"with" if symbols else "without"} symbols, minimum '
          f'length is {min_length}, hint is {hint}:')
    print('-------------------')
    if not hint is None:
        result = [word for word in result if hint in word]
    for word in result:
        print(word)
    print('-------------------')

def text_scan(process, text):
    """
    Scan process for given text
    """
    # Get scannables that will be checked for the text
    scannable_array = array_from_where(process, text[1])
    try:
        result, scannable = process.scanner.ASCII_scan_arr(scannable_array, text[0])
    except Exception:
        raise click.BadParameter('Invalid ASCII scan parameters.')
    # If the text exists in the process, show it along with address for further inspection
    if result is None:
        print('Text does not exist.')
    else:
        print(f'Text found at: {hex(scannable.base_address)} + {hex(result)} = '
              f'{hex(scannable.base_address + result)}')

def aob_scan(process, aob):
    """
    Same as text scan except with bytes
    """
    scannable_array = array_from_where(process, aob[1])
    # Parameters can specify pattern and it's separator and base
    try:
        result, scannable = process.scanner.AOB_scan_arr(scannable_array, aob[0], aob[2], aob[3])
    except Exception:
        raise click.BadParameter('Invalid AOB scan parameters.')
    if result is None:
        print('Pattern does not exist.')
    else:
        print(f'Pattern found at: {hex(scannable.base_address)} + {hex(result)} = '
              f'{hex(scannable.base_address + result)}')

def dump_section(process, config):
    """
    Dumps the pattern in this section from provided scannable
    """
    scannable_array = array_from_where(process, config['scannable'])
    pattern = config['pattern']
    try:
        separator = config['separator']
    except Exception:
        separator = ' '
    try:
        base = int(config['base'])
    except Exception:
        base = 16
    result, _ = process.scanner.AOB_scan_arr(scannable_array, pattern, base, separator)
    if result is None:
        print(f'{config.name} = {-1}')
    else:
        print(f'{config.name} = {hex(result)}')

def dump_memory(process, dump):
    """
    Dumps memory patterns from given process using parameters from the config file
    """
    config_parser = configparser.ConfigParser(allow_no_value=True)
    with open(dump) as file:
        try:
            config_parser.read_file(file)
        except Exception:
            raise click.BadParameter(f'Config file {dump} does not exist or has invalid format.')
        print(f'Dumping memory of {process.proc_name} for patterns from {dump}')
        for section in config_parser.sections():
            try:
                dump_section(process, config_parser[section])
            except Exception:
                raise click.BadParameter(f'Config file {dump} does not exist or has invalid '
                                          'format.')

def process_app(process, modules, pages, aob, text, list_text, view, dump):
    """
    Processes all the parameters given, also makes sure to only do one task
    if multiple parameters are provided, also sets the order of actions
    """
    # Modules can be listed on top of other commands
    if modules:
        process.print_modules()
    # Pages can be listed on top of other commands
    if pages:
        process.print_pages()
    # Other commands cannot be processed if previous one was already done
    if not aob[0] is None:
        aob_scan(process, aob)
        return
    if not text[0] is None:
        text_scan(process, text)
        return
    if not list_text[0] is None:
        text_list(process, list_text)
        return
    if not view[0] is None:
        memory_view(process, view)
        return
    if not dump is None:
        try:
            dump_memory(process, dump)
        except Exception:
            raise click.BadParameter(f'Config file {dump} does not exist or has invalid format.')
        return


def get_proc(identifier):
    """
    Retrieves process from identifier (whether it is name or PID)
    """
    try:
        pid = int(identifier)
    except Exception:
        pid = -1
    return WinProc(identifier, pid)

def compare_procs(first, second):
    """
    Compares two processes given as string of pid or name
    """
    try:
        first_proc = get_proc(first)
        second_proc = get_proc(second)
    except Exception as err:
        raise click.BadParameter(err)
    first_proc.compare(second_proc)

def run_app(name, pid, p_list, modules, pages, aob, text, list_text, view, compare, dump):
    """
    Helper to run the app from parameters
    """
    # If we want to list processes, do it and stop
    if p_list:
        WinSys.process_list_print()
        return
    # If we want to compare processes, do it and stop
    if compare:
        compare_procs(compare[0], compare[1])
        return
    # Otherwise, name or pid of process has to be provided for the other commands to work
    if (name is None) and pid == -1:
        raise click.BadParameter('Please specify process to work with.')
    # Try creating the process
    try:
        process = WinProc(name, pid)
    except Exception as err:
        raise click.BadParameter(err)
    process_app(process, modules, pages, aob, text, list_text, view, dump)

@click.command()
@click.version_option(version='1.0')
@click.option('-n', '--name', help='Name of the process to work with.')
@click.option('-i', '--pid', default=-1, help='PID of the process to work with.')
@click.option('-l', '--p-list', is_flag=True, default=False, help='List all processes running.')
@click.option('-m', '--modules', is_flag=True, default=False, help='List all modules of given '
              'process.')
@click.option('-p', '--pages', is_flag=True, default=False, help='List all valid pages of given '
              'process.')
@click.option('-a', '--aob', help='Scan given process against a provided AOB pattern. Use -w to '
              'specify what to scan, -b to set base of the pattern and -s to set the separator '
              'of the pattern.')
@click.option('-w', '--where', help='Specifies what to scan (pages, modules, all, specific'
              ' module).')
@click.option('-b', '--base', default=16, show_default=True, help='Specifies the base of bytes '
              'of the AOB pattern (16 for hex, 10 for decimal).')
@click.option('-s', '--separator', default=',', show_default=True, help='Specifies the separator '
              'of bytes of the AOB pattern.')
@click.option('-t', '--text', help='Scans given process for a provided string. Use -w to specify '
              'what to scan.')
@click.option('-lt', '--list-text', help='Print all strings in a given process. Provide \' \' as '
              'parameter for reasonable strings (length 5 with symbols). If you want to specify '
              'length and symbol usage yourself, the format is s<number> where s means use symbols,'
              ' c don\'t and number is minimum length. Example: s6 or c4. Use -w to specify what to'
              ' scan, -h <word> to only show strings that contain <word>.')
@click.option('-h', '--hint', help='For -lt, specifies <word> that the strings must contain. '
              'For -v, speficies <number> address where to start printing the memory (can be '
              'decimal or hex).')
@click.option('-v', '--view', help='Print memory of provided scannable into console. Scannable '
              'can be pages, modules, all or specific module name. Use -h <number> to start memory'
              ' view at provided <number> as address.')
@click.option('-c', '--compare', nargs=2, help='Compare two processes against each other. Arguments'
              ' can be either name of the process or process id.')
@click.option('-d', '--dump', help='Dump offsets of process from a config file.')
def main_app(name, pid, p_list, modules, pages, aob, where, base, separator, text, list_text, hint,
             view, compare, dump):
    """
    CLI click wrapper for the application.
    Everything is forwarded into the main entry point.
    """
    run_app(name, pid, p_list, modules, pages, [aob, where, base, separator], [text, where],
            [list_text, where, hint], [view, hint], compare, dump)

def main():
    """
    Helper for package manager.
    """
    main_app(prog_name='wmempy')
