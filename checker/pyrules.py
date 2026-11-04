"""Rules a Python syntax tree can decide. Pure: source text in, faults out."""
import ast
import fnmatch
import io
import re
import tokenize

import textrules
from model import Fault

PEP_723_BLOCK = re.compile(r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$')
ALLOWED_COMMENT = re.compile(r'#!|#\s*(why:|noqa|type:|pragma|fmt:|ruff:)')
SQL = re.compile(r'^\s*(SELECT\s.+\sFROM\s|INSERT\s+INTO\s|UPDATE\s.+\sSET\s|DELETE\s+FROM\s|CREATE\s+TABLE\s)', re.I | re.S)
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
PROCESS_CALLS = {
    'subprocess': {'run', 'call', 'check_call', 'check_output', 'Popen', 'getoutput', 'getstatusoutput'},
    'os': {'system', 'popen', 'execv', 'execve', 'execvp', 'execvpe', 'execl', 'execle', 'execlp', 'execlpe',
           'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe',
           'posix_spawn', 'posix_spawnp'},
    'asyncio': {'create_subprocess_exec', 'create_subprocess_shell'}}


def single(path, node, rule, message):
    return Fault(path, node.lineno, node.lineno, rule, message)


def metadata_lines(source):
    """why: a PEP 723 script block is machine-read configuration, not commentary."""
    lines = set()
    for block in PEP_723_BLOCK.finditer(source):
        first = source.count('\n', 0, block.start()) + 1
        lines.update(range(first, first + block.group(0).count('\n') + 1))
    return lines


def comment_faults(path, source):
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    metadata = metadata_lines(source)
    comments = [token for token in tokens if token.type == tokenize.COMMENT and token.start[0] not in metadata]
    return [Fault(path, token.start[0], token.start[0], 'comment-why-only', 'comment must start `why:`')
            for token in comments if not ALLOWED_COMMENT.match(token.string)]


def docstring_faults(path, tree):
    nodes = [node for node in ast.walk(tree) if isinstance(node, (*FUNCTIONS, ast.ClassDef))]
    return [single(path, node, 'docstring-why-only', f'{node.name}: docstring must start `why:`')
            for node in nodes if not (ast.get_docstring(node) or 'why:').startswith('why:')]


def nested_in(path, node):
    inner = [child for child in ast.walk(node) if child is not node and isinstance(child, FUNCTIONS)]
    return [single(path, child, 'no-nested-function', f'{child.name}: move to top level') for child in inner]


def nested_faults(path, tree):
    return [fault for node in ast.walk(tree) if isinstance(node, FUNCTIONS) for fault in nested_in(path, node)]


def lambda_faults(path, tree):
    return [single(path, node, 'no-lambda', 'use a named function')
            for node in ast.walk(tree) if isinstance(node, ast.Lambda)]


def is_sql(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and bool(SQL.match(node.value))


def sql_faults(path, tree):
    return [single(path, node, 'inline-sql', 'move SQL to a .sql file') for node in ast.walk(tree) if is_sql(node)]


def length_faults(path, tree, source, limit):
    lines = source.splitlines()
    faults = []
    for node in (item for item in ast.walk(tree) if isinstance(item, FUNCTIONS)):
        size = sum(1 for text in lines[node.lineno - 1:node.end_lineno] if text.strip())
        if size > limit:
            faults.append(Fault(path, node.lineno, node.end_lineno, 'function-length', f'{node.name}: {size} lines; most {limit}'))
    return faults


def is_process_call(node):
    func = node.func if isinstance(node, ast.Call) else None
    if not (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)):
        return False
    return func.attr in PROCESS_CALLS.get(func.value.id, ())


def command_node(call):
    first = call.args[0] if call.args else None
    return first.elts[0] if isinstance(first, (ast.List, ast.Tuple)) and first.elts else first


def literal_text(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return ' '.join(part.value for part in node.values if isinstance(part, ast.Constant))
    return None


def is_sys_executable(node):
    return isinstance(node, ast.Attribute) and node.attr == 'executable' and ast.unparse(node.value) == 'sys'


def spawns_outside_uv(node):
    text = literal_text(node)
    return is_sys_executable(node) or (text is not None and textrules.line_breaks_uv(text))


def starts_with_interpreter(node):
    first = node.elts[0] if isinstance(node, ast.List) and len(node.elts) > 1 else None
    text = literal_text(first) if first is not None else None
    return text is not None and textrules.INTERPRETER_PATH.fullmatch(text) is not None


def uv_call_faults(path, tree):
    calls = [node for node in ast.walk(tree) if is_process_call(node)]
    covered = {id(call.args[0]) for call in calls if call.args}
    lists = [node for node in ast.walk(tree) if id(node) not in covered and starts_with_interpreter(node)]
    return [single(path, node, 'uv-only', 'run and install Python only through uv')
            for node in [*(call for call in calls if spawns_outside_uv(command_node(call))), *lists]]


def is_test(path, limits):
    return any(fnmatch.fnmatch(path, pattern) for pattern in limits['test_paths'])


def function_spans(source):
    tree = ast.parse(source)
    return {node.lineno: node.end_lineno for node in ast.walk(tree) if isinstance(node, FUNCTIONS)}


def faults_for(path, source, limits):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [Fault(path, error.lineno or 1, error.lineno or 1, 'syntax', str(error.msg))]
    found = [*comment_faults(path, source), *docstring_faults(path, tree), *nested_faults(path, tree)]
    found += [*lambda_faults(path, tree), *sql_faults(path, tree), *uv_call_faults(path, tree)]
    return found if is_test(path, limits) else [*found, *length_faults(path, tree, source, limits['max_function_lines'])]
