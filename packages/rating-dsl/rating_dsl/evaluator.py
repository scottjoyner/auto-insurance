"""
Rating DSL expression evaluator.

Provides a safe, deterministic engine for evaluating boolean expressions
and numeric formulas found in the rating DSL. Uses Python's `ast` module
to parse and evaluate expressions, with a restricted namespace containing
only the quote context variables and a small set of allowed functions.

Supported expression types:
- Comparison: age >= 16, claims_3yr <= 3, credit_tier == 'a'
- Arithmetic: vehicle_value * 0.008, base + surcharge - discount
- Logical: age >= 16 and claims_3yr == 0
- Built-in functions: abs(), min(), max(), round(), int(), float()
- Ternary: 100 if age >= 25 else 200
"""

from __future__ import annotations

import ast
import math
import operator as op
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_FLOOR, ROUND_CEILING
from typing import Any, Callable, Optional

# Allowed arithmetic/unary operators
_ARITH_OPS: dict[type, op._FunctionType] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Not: op.not_,
}

# Allowed comparison operators
_CMP_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
    ast.Lt: op.lt,
    ast.LtE: op.le,
    ast.Gt: op.gt,
    ast.GtE: op.ge,
    ast.In: lambda a, b: op.contains(b, a),  # a in b
    ast.NotIn: lambda a, b: not op.contains(b, a),  # a not in b
}

# Allowed logical operators (binary only)
_LOGIC_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.And: lambda a, b: a and b,
    ast.Or: lambda a, b: a or b,
}

# Allowed built-in functions
_ALLOWED_BUILTINS: dict[str, Any] = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "int": int,
    "float": float,
    "pow": pow,
    "sum": sum,
    "any": any,
    "all": all,
    "math": math,
}


class ExpressionError(ValueError):
    """Raised when an expression cannot be evaluated."""
    pass


class Evaluator:
    """
    Safe expression evaluator for the rating DSL.

    Supports two evaluation modes:
    1. Boolean expressions (eligibility rules, discount/surcharge conditions)
    2. Numeric formulas (base amount calculations)

    All expressions are evaluated against a context dict of variable names
    and values.
    """

    def __init__(
        self,
        context: dict[str, Any],
        precision: int = 2,
        round_mode: str = "half_up",
    ):
        """
        Args:
            context: Variable name -> value mapping from the quote.
            precision: Decimal precision for numeric results.
            round_mode: One of 'half_up', 'half_down', 'ceiling', 'floor'.
        """
        self.context = context
        self.precision = precision
        self.round_mode = round_mode

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_boolean(self, expression: str) -> bool:
        """
        Evaluate a boolean expression against the quote context.

        Args:
            expression: A string like 'age >= 16 and claims_3yr <= 3'

        Returns:
            True if the expression evaluates to a truthy value.

        Raises:
            ExpressionError: If the expression is invalid or uses disallowed
                             operators/functions.
        """
        result = self._eval_ast(self._parse(expression))
        return bool(result)

    def evaluate_numeric(self, expression: str) -> Decimal:
        """
        Evaluate a numeric expression against the quote context.

        Args:
            expression: A string like 'vehicle_value * 0.008 + 50'

        Returns:
            A Decimal result, rounded to the configured precision.
        """
        result = self._eval_ast(self._parse(expression))
        return self._to_decimal(result)

    def evaluate_formula(self, formula: str) -> Decimal:
        """Alias for evaluate_numeric (same semantics)."""
        return self.evaluate_numeric(formula)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse(self, expression: str) -> ast.AST:
        """Parse an expression string into an AST, with safety checks."""
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise ExpressionError(f"Syntax error in expression '{expression}': {e}") from e

        self._check_safety(tree)
        return tree

    def _check_safety(self, tree: ast.AST) -> None:
        """Walk the AST and reject disallowed node types."""
        # All operator types that are safe to allow
        _ALLOWED_OPS = (
            # Comparison operators
            ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq,
            ast.Is, ast.IsNot, ast.In, ast.NotIn,
            # Arithmetic operators
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Pow, ast.Mod,
            # Unary operators
            ast.Invert, ast.Not, ast.UAdd, ast.USub,
            # Logical operators
            ast.And, ast.Or,
            # Bitwise operators
            ast.BitOr, ast.BitAnd, ast.BitXor, ast.LShift, ast.RShift,
            # Context nodes (used by Name, Store, Load, etc.)
            ast.Load, ast.Store, ast.Del,
        )
        for node in ast.walk(tree):
            # Only allow specific node types
            allowed = (
                ast.Expression, ast.Constant, ast.Name, ast.BinOp,
                ast.UnaryOp, ast.Compare, ast.BoolOp, ast.Call,
                ast.Attribute, ast.Subscript,
                ast.Tuple, ast.List, ast.Dict,
            ) + _ALLOWED_OPS
            if not isinstance(node, allowed):
                raise ExpressionError(
                    f"Disallowed AST node type '{type(node).__name__}' "
                    f"in expression: {ast.dump(node)}"
                )

            # Reject attribute access except for 'math.xxx'
            if isinstance(node, ast.Attribute):
                if not isinstance(node.value, ast.Name):
                    raise ExpressionError(
                        f"Attribute access only allowed on 'math' module"
                    )
                if node.value.id != "math":
                    raise ExpressionError(
                        f"Attribute access only allowed on 'math' module, "
                        f"got '{node.value.id}.{node.attr}'"
                    )

            # Reject function calls except allowed builtins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in _ALLOWED_BUILTINS:
                        raise ExpressionError(
                            f"Function '{node.func.id}' is not allowed. "
                            f"Allowed: {list(_ALLOWED_BUILTINS.keys())}"
                        )

    def _eval_ast(self, node: ast.AST) -> Any:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Expression):
            return self._eval_ast(node.body)

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in self.context:
                return self.context[node.id]
            if node.id in _ALLOWED_BUILTINS:
                return _ALLOWED_BUILTINS[node.id]
            raise ExpressionError(f"Unknown variable: '{node.id}'")

        if isinstance(node, ast.BinOp):
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            op_type = type(node.op)
            if op_type not in _ARITH_OPS:
                raise ExpressionError(f"Unsupported operator: {op_type.__name__}")
            return _ARITH_OPS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_ast(node.operand)
            op_type = type(node.op)
            if op_type not in _ARITH_OPS:
                raise ExpressionError(f"Unsupported unary operator: {op_type.__name__}")
            return _ARITH_OPS[op_type](operand)

        if isinstance(node, ast.Compare):
            left = self._eval_ast(node.left)
            comparators = [self._eval_ast(c) for c in node.comparators]
            results = []
            for cmp_op, comp in zip(node.ops, comparators):
                op_type = type(cmp_op)
                if op_type not in _CMP_OPS:
                    raise ExpressionError(f"Unsupported comparison: {op_type.__name__}")
                results.append(_CMP_OPS[op_type](left, comp))
                left = comp
            # Chain: a < b < c means (a < b) and (b < c)
            return all(results)

        if isinstance(node, ast.BoolOp):
            # True short-circuit: evaluate values lazily
            op_type = type(node.op)
            if op_type not in _LOGIC_OPS:
                raise ExpressionError(f"Unsupported logical operator: {op_type.__name__}")
            fn = _LOGIC_OPS[op_type]
            # Evaluate first value
            result = self._eval_ast(node.values[0])
            if op_type is ast.And:
                # Short-circuit on falsy
                if not result:
                    return False
                for v in node.values[1:]:
                    result = fn(result, self._eval_ast(v))
                    if not result:
                        return False
                return result
            else:  # Or
                # Short-circuit on truthy
                if result:
                    return True
                for v in node.values[1:]:
                    result = fn(result, self._eval_ast(v))
                    if result:
                        return True
                return result

        if isinstance(node, ast.Call):
            func = self._eval_ast(node.func)
            args = [self._eval_ast(a) for a in node.args]
            if not callable(func):
                raise ExpressionError(f"Cannot call non-callable")
            return func(*args)

        if isinstance(node, ast.Attribute):
            obj = self._eval_ast(node.value)
            # Only support math module attributes
            if isinstance(obj, type(math)):
                return getattr(obj, node.attr)
            raise ExpressionError(f"Attribute access only supported on 'math' module")

        if isinstance(node, ast.Subscript):
            obj = self._eval_ast(node.value)
            idx = self._eval_ast(node.slice)
            return obj[idx]

        if isinstance(node, (ast.Tuple, ast.List)):
            return (tuple if isinstance(node, ast.Tuple) else list)([self._eval_ast(e) for e in node.elts])

        raise ExpressionError(f"Unsupported expression node: {type(node).__name__}")

    def _to_decimal(self, value: Any) -> Decimal:
        """Convert a numeric result to a Decimal with configured precision."""
        if isinstance(value, Decimal):
            return value
        if isinstance(value, bool):
            return Decimal(int(value))
        d = Decimal(str(value))
        quantize_str = "0." + "0" * self.precision
        round_map = {
            "half_up": ROUND_HALF_UP,
            "half_down": ROUND_HALF_DOWN,
            "ceiling": ROUND_CEILING,
            "floor": ROUND_FLOOR,
        }
        return d.quantize(Decimal(quantize_str), rounding=round_map.get(self.round_mode, ROUND_HALF_UP))
