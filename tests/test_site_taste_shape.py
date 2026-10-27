"""Code-shape checks that ruff does not have: no nested functions and no lambdas in the site-taste code."""
import ast
import unittest

import context_site_taste

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
CHECKED = (*sorted(context_site_taste.SCRIPTS.glob("*.py")), *sorted(context_site_taste.ROOT.glob("tests/*site_taste*.py")))


def nested_in(function: ast.AST) -> list[ast.AST]:
    return [node for node in ast.walk(function) if node is not function and isinstance(node, FUNCTIONS)]


def shape_problems(source: str, filename: str) -> list[str]:
    tree = ast.parse(source)
    functions = [node for node in ast.walk(tree) if isinstance(node, FUNCTIONS)]
    nested = [inner for function in functions for inner in nested_in(function)]
    lambdas = [node for node in ast.walk(tree) if isinstance(node, ast.Lambda)]
    return [f"{filename}:{node.lineno}: nested function {node.name}" for node in nested] + [
        f"{filename}:{node.lineno}: lambda" for node in lambdas
    ]


class TestShapeProblems(unittest.TestCase):
    def test_finds_a_nested_function(self):
        source = "def outer():\n    def inner():\n        pass\n"
        self.assertEqual(shape_problems(source, "x.py"), ["x.py:2: nested function inner"])

    def test_finds_a_lambda(self):
        self.assertEqual(shape_problems("key = sorted([], key=lambda v: v)\n", "x.py"), ["x.py:1: lambda"])

    def test_allows_methods_in_a_class(self):
        self.assertEqual(shape_problems("class A:\n    def method(self):\n        pass\n", "x.py"), [])


class TestSiteTasteCodeShape(unittest.TestCase):
    def test_skill_code_has_no_nested_functions_or_lambdas(self):
        problems = [p for path in CHECKED for p in shape_problems(path.read_text(), path.name)]
        self.assertEqual(problems, [])

    def test_the_check_covers_the_skill_scripts(self):
        self.assertGreaterEqual(len(CHECKED), 7)


if __name__ == "__main__":
    unittest.main()
