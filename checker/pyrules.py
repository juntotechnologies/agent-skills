"""Rules a Python syntax tree can decide. Pure: source text in, faults out."""
import ast
import fnmatch
import io
import re
import tokenize

from model import Fault

ALLOWED_COMMENT = re.compile(r'#!|#\s*(why:|noqa|type:|pragma|fmt:|ruff:)')
SQL = re.compile(r'^\s*(SELECT\s.+\sFROM\s|INSERT\s+INTO\s|UPDATE\s.+\sSET\s|DELETE\s+FROM\s|CREATE\s+TABLE\s)', re.I | re.S)
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def single(path, node, rule, message):
    return Fault(path, node.lineno, node.lineno, rule, message)


def comment_faults(path, source):
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    comments = [token for token in tokens if token.type == tokenize.COMMENT]
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
    found += [*lambda_faults(path, tree), *sql_faults(path, tree)]
    return found if is_test(path, limits) else [*found, *length_faults(path, tree, source, limits['max_function_lines'])]
