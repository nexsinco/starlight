
"""
╔══════════════════════════════════════════════════════════════════════╗
║                    STELLIGHT AI - BRAIN v2.0                         ║
║             Hyper-Intelligent Decision & Response Engine             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import random
from collections import defaultdict, Counter


# ══════════════════════════════════════════════════════════════════════
#  SECTION 1 — ADVANCED MATH ENGINE
# ══════════════════════════════════════════════════════════════════════

class AdvancedMathEngine:

    CONSTANTS = {
        'pi': math.pi, 'e': math.e, 'phi': (1 + math.sqrt(5)) / 2,
        'tau': math.tau, 'inf': math.inf, 'euler': 0.5772156649,
        'sqrt2': math.sqrt(2), 'sqrt3': math.sqrt(3),
    }

    UNITS = {
        'km': 1000, 'm': 1, 'cm': 0.01, 'mm': 0.001,
        'mile': 1609.344, 'miles': 1609.344, 'yard': 0.9144,
        'yards': 0.9144, 'foot': 0.3048, 'feet': 0.3048,
        'inch': 0.0254, 'inches': 0.0254,
        'kg': 1, 'g': 0.001, 'mg': 1e-6, 'lb': 0.453592,
        'lbs': 0.453592, 'oz': 0.028349, 'ton': 1000, 'tonne': 1000,
        's': 1, 'sec': 1, 'min': 60, 'hour': 3600, 'hours': 3600,
        'day': 86400, 'days': 86400, 'week': 604800, 'weeks': 604800,
    }

    @staticmethod
    def _implicit_mult(expr: str) -> str:
        expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
        expr = re.sub(r'(\))(\d|[a-zA-Z(])', r'\1*\2', expr)
        return expr

    @staticmethod
    def _tokenize(expr: str):
        spec = [
            ('FLOAT',  r'\d+\.\d+'),
            ('INT',    r'\d+'),
            ('CONST',  r'pi|tau|phi|euler|sqrt2|sqrt3|inf'),
            ('FUNC',   r'sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|'
                       r'sqrt|cbrt|log|ln|log2|log10|exp|abs|ceil|floor|'
                       r'round|sign|fact|gamma'),
            ('VAR',    r'[a-zA-Z_][a-zA-Z_0-9]*'),
            ('OP',     r'[+\-*/%^!]'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('COMMA',  r','),
            ('SKIP',   r'\s+'),
        ]
        regex = '|'.join('(?P<%s>%s)' % (n, p) for n, p in spec)
        tokens = []
        pos = 0
        for mo in re.finditer(regex, expr):
            if mo.start() != pos:
                raise SyntaxError("Invalid token near '%s'" % expr[pos:mo.start() + 1])
            pos = mo.end()
            kind, val = mo.lastgroup, mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'FLOAT':
                val = float(val)
            elif kind == 'INT':
                val = int(val)
            elif kind == 'CONST':
                val = AdvancedMathEngine.CONSTANTS[val]
                kind = 'FLOAT'
            tokens.append((kind, val))
        if pos != len(expr):
            raise SyntaxError("Invalid token near '%s'" % expr[pos:])
        return tokens

    @classmethod
    def _parse(cls, tokens):
        pos = [0]

        def peek():
            return tokens[pos[0]] if pos[0] < len(tokens) else None

        def consume(kind=None):
            t = tokens[pos[0]]
            if kind and t[0] != kind:
                raise SyntaxError("Expected %s, got %s" % (kind, t))
            pos[0] += 1
            return t

        def parse_expr():
            return parse_additive()

        def parse_additive():
            left = parse_multiplicative()
            while peek() and peek()[0] == 'OP' and peek()[1] in ('+', '-'):
                op = consume('OP')[1]
                right = parse_multiplicative()
                left = ('binop', op, left, right)
            return left

        def parse_multiplicative():
            left = parse_power()
            while peek() and peek()[0] == 'OP' and peek()[1] in ('*', '/', '%'):
                op = consume('OP')[1]
                right = parse_power()
                left = ('binop', op, left, right)
            return left

        def parse_power():
            base = parse_unary()
            if peek() and peek()[0] == 'OP' and peek()[1] == '^':
                consume('OP')
                exp = parse_power()
                return ('binop', '^', base, exp)
            return base

        def parse_unary():
            if peek() and peek()[0] == 'OP' and peek()[1] == '-':
                consume('OP')
                return ('unary', '-', parse_primary())
            if peek() and peek()[0] == 'OP' and peek()[1] == '+':
                consume('OP')
                return parse_primary()
            return parse_primary()

        def parse_primary():
            t = peek()
            if not t:
                raise SyntaxError("Unexpected end of expression")

            if t[0] == 'FUNC':
                fname = consume('FUNC')[1]
                consume('LPAREN')
                args = [parse_expr()]
                while peek() and peek()[0] == 'COMMA':
                    consume('COMMA')
                    args.append(parse_expr())
                consume('RPAREN')
                return ('func', fname, args)

            if t[0] in ('INT', 'FLOAT'):
                val = consume()[1]
                node = ('num', val)
                if peek() and peek()[0] == 'OP' and peek()[1] == '!':
                    consume('OP')
                    return ('func', 'fact', [node])
                return node

            if t[0] == 'VAR':
                name = consume('VAR')[1]
                return ('var', name)

            if t[0] == 'LPAREN':
                consume('LPAREN')
                node = parse_expr()
                consume('RPAREN')
                return node

            raise SyntaxError("Unexpected token: %s" % str(t))

        ast = parse_expr()
        if pos[0] != len(tokens):
            raise SyntaxError("Trailing tokens at position %d" % pos[0])
        return ast

    @classmethod
    def _eval(cls, node, variables: dict):
        if node[0] == 'num':
            return node[1]
        if node[0] == 'var':
            name = node[1]
            if name in variables:
                return variables[name]
            if name in cls.CONSTANTS:
                return cls.CONSTANTS[name]
            raise NameError("Unknown variable '%s'" % name)
        if node[0] == 'unary':
            return -cls._eval(node[2], variables)
        if node[0] == 'func':
            fname, args = node[1], [cls._eval(a, variables) for a in node[2]]
            v = args[0]
            funcs = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
                'sqrt': math.sqrt,
                'cbrt': lambda x: math.copysign(abs(x) ** (1.0/3.0), x),
                'log': math.log, 'ln': math.log, 'log2': math.log2,
                'log10': math.log10, 'exp': math.exp,
                'abs': abs, 'ceil': math.ceil, 'floor': math.floor,
                'round': round,
                'sign': lambda x: (1 if x > 0 else (-1 if x < 0 else 0)),
                'fact': lambda x: math.factorial(int(x)),
                'gamma': math.gamma,
            }
            if fname == 'log' and len(args) == 2:
                return math.log(args[0], args[1])
            if fname == 'round' and len(args) == 2:
                return round(args[0], int(args[1]))
            if fname not in funcs:
                raise NameError("Unknown function '%s'" % fname)
            return funcs[fname](v)
        if node[0] == 'binop':
            _, op, l, r = node
            lv, rv = cls._eval(l, variables), cls._eval(r, variables)
            if op == '+': return lv + rv
            if op == '-': return lv - rv
            if op == '*': return lv * rv
            if op == '/':
                if rv == 0:
                    raise ZeroDivisionError("Division by zero")
                return lv / rv
            if op == '%': return lv % rv
            if op == '^': return lv ** rv
        raise ValueError("Unknown AST node: %s" % str(node))

    @classmethod
    def evaluate(cls, expr: str, variables=None) -> float:
        scope = dict(cls.CONSTANTS)
        if variables is not None:
            scope.update(variables)
        expr = cls._implicit_mult(expr)
        tokens = cls._tokenize(expr)
        if not tokens:
            raise SyntaxError("Empty expression")
        ast = cls._parse(tokens)
        return cls._eval(ast, scope)

    @staticmethod
    def _fmt(val) -> str:
        if isinstance(val, float):
            if val == int(val) and abs(val) < 1e15:
                return str(int(val))
            return "%.10g" % val
        return str(val)

    @classmethod
    def derivative_numeric(cls, expr: str, var: str, point: float) -> float:
        h = 1e-7
        f = lambda x: cls.evaluate(expr, {var: x})
        return (f(point + h) - f(point - h)) / (2 * h)

    @classmethod
    def derivative_symbolic(cls, expr: str, var: str = 'x') -> str:
        expr = expr.replace('^', '**').replace(' ', '')
        expr = cls._implicit_mult(expr)
        terms = re.split(r'(?=[+-])', expr)
        result = []
        for term in terms:
            term = term.strip()
            if not term or var not in term:
                continue
            m = re.match(r'^([+-]?\d*\.?\d*)\*?' + var + r'(?:\*\*([+-]?\d*\.?\d*))?$', term)
            if not m:
                result.append("d/d%s(%s)" % (var, term))
                continue
            coeff_s, exp_s = m.group(1), m.group(2)
            coeff = float(coeff_s) if coeff_s not in ('', '+', '-') else (1.0 if coeff_s != '-' else -1.0)
            exp = float(exp_s) if exp_s else 1.0
            new_coeff = coeff * exp
            new_exp = exp - 1
            if new_exp == 0:
                val = int(new_coeff) if new_coeff == int(new_coeff) else new_coeff
                result.append(str(val))
            elif new_exp == 1:
                c = int(new_coeff) if new_coeff == int(new_coeff) else new_coeff
                if c == 1:
                    result.append(var)
                elif c == -1:
                    result.append("-" + var)
                else:
                    result.append("%s*%s" % (c, var))
            else:
                c = int(new_coeff) if new_coeff == int(new_coeff) else new_coeff
                e = int(new_exp) if new_exp == int(new_exp) else new_exp
                if c == 1:
                    result.append("%s^%s" % (var, e))
                elif c == -1:
                    result.append("-%s^%s" % (var, e))
                else:
                    result.append("%s*%s^%s" % (c, var, e))
        if not result:
            return '0'
        out = '+'.join(result).replace('+-', '-')
        return out

    @classmethod
    def integrate_numeric(cls, expr: str, var: str, a: float, b: float, n: int = 1000) -> float:
        if n % 2 != 0:
            n += 1
        h = (b - a) / n
        f = lambda x: cls.evaluate(expr, {var: x})
        total = f(a) + f(b)
        for i in range(1, n):
            total += (4 if i % 2 else 2) * f(a + i * h)
        return total * h / 3

    @staticmethod
    def stats(nums: list) -> dict:
        n = len(nums)
        if n == 0:
            return {}
        mean = sum(nums) / n
        sorted_n = sorted(nums)
        if n % 2 == 1:
            median = sorted_n[n // 2]
        else:
            median = (sorted_n[n // 2 - 1] + sorted_n[n // 2]) / 2
        variance = sum((x - mean) ** 2 for x in nums) / n
        freq = Counter(nums)
        max_freq = max(freq.values())
        mode = [k for k, v in freq.items() if v == max_freq]
        return {
            'mean': mean,
            'median': median,
            'mode': mode,
            'std_dev': math.sqrt(variance),
            'variance': variance,
            'min': min(nums),
            'max': max(nums),
            'range': max(nums) - min(nums),
            'sum': sum(nums),
            'count': n,
        }

    @staticmethod
    def mat_det(M):
        n = len(M)
        if n == 1:
            return M[0][0]
        if n == 2:
            return M[0][0] * M[1][1] - M[0][1] * M[1][0]
        det = 0
        for c in range(n):
            minor = [row[:c] + row[c+1:] for row in M[1:]]
            det += ((-1) ** c) * M[0][c] * AdvancedMathEngine.mat_det(minor)
        return det

    @staticmethod
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    @staticmethod
    def prime_factors(n: int) -> list:
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    @staticmethod
    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a: int, b: int) -> int:
        return abs(a * b) // AdvancedMathEngine.gcd(a, b)

    @staticmethod
    def fibonacci(n: int) -> list:
        if n <= 0:
            return []
        seq = [0, 1]
        while len(seq) < n:
            seq.append(seq[-1] + seq[-2])
        return seq[:n]

    @classmethod
    def convert_units(cls, value: float, from_u: str, to_u: str) -> float:
        fu, tu = from_u.lower(), to_u.lower()
        temp_map = {
            ('c', 'f'): lambda x: x * 9.0/5.0 + 32,
            ('f', 'c'): lambda x: (x - 32) * 5.0/9.0,
            ('c', 'k'): lambda x: x + 273.15,
            ('k', 'c'): lambda x: x - 273.15,
            ('f', 'k'): lambda x: (x - 32) * 5.0/9.0 + 273.15,
            ('k', 'f'): lambda x: (x - 273.15) * 9.0/5.0 + 32,
        }
        if (fu, tu) in temp_map:
            return temp_map[(fu, tu)](value)
        if fu in cls.UNITS and tu in cls.UNITS:
            return value * cls.UNITS[fu] / cls.UNITS[tu]
        raise ValueError("Cannot convert %s to %s" % (from_u, to_u))


    @staticmethod
    def _fmt_steps(title: str, steps: list, answer: str) -> str:
        rendered = [title, "Steps:"]
        rendered.extend("  %d) %s" % (i + 1, step) for i, step in enumerate(steps))
        rendered.append("Answer: %s" % answer)
        return "\n".join(rendered)

    @staticmethod
    def _extract_numbers(text: str) -> list:
        return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]

    @classmethod
    def _solve_linear_equation(cls, lhs: str, rhs: str, var: str):
        try:
            f0 = cls.evaluate('(%s)-(%s)' % (lhs, rhs), {var: 0})
            f1 = cls.evaluate('(%s)-(%s)' % (lhs, rhs), {var: 1})
            a = f1 - f0
            b = f0
            if abs(a) < 1e-12:
                return None
            root = -b / a
            if abs(cls.evaluate('(%s)-(%s)' % (lhs, rhs), {var: root})) > 1e-7:
                return None
            steps = [
                "Move everything to one side: f(%s) = (%s) - (%s)." % (var, lhs, rhs),
                "Evaluate f(0) = %s and f(1) = %s, so slope a = %s." % (cls._fmt(f0), cls._fmt(f1), cls._fmt(a)),
                "Solve a·%s + b = 0: %s = %s / %s." % (var, var, cls._fmt(-b), cls._fmt(a)),
            ]
            return cls._fmt_steps("Linear equation solver", steps, "%s = %s" % (var, cls._fmt(root)))
        except Exception:
            return None

    @classmethod
    def _solve_quadratic_coefficients(cls, eq: str, var: str):
        match = re.match(
            r'^\s*([+-]?\d*\.?\d*)\*?%s\^2\s*([+-]\s*\d*\.?\d*)\*?%s\s*([+-]\s*\d+\.?\d*)?\s*=\s*0\s*$' % (var, var),
            eq.replace(' ', ''),
            re.I,
        )
        if not match:
            return None
        def coeff(raw, default=1.0):
            if raw in (None, ''):
                return default
            raw = raw.replace(' ', '')
            if raw == '+':
                return 1.0
            if raw == '-':
                return -1.0
            return float(raw)
        a = coeff(match.group(1), 1.0)
        b = coeff(match.group(2), 1.0)
        c = coeff(match.group(3), 0.0)
        disc = b * b - 4 * a * c
        steps = [
            "Identify a = %s, b = %s, c = %s." % (cls._fmt(a), cls._fmt(b), cls._fmt(c)),
            "Compute discriminant Δ = b² - 4ac = %s." % cls._fmt(disc),
        ]
        if disc < 0:
            real = -b / (2 * a)
            imag = math.sqrt(-disc) / (2 * a)
            ans = "%s = %s ± %si" % (var, cls._fmt(real), cls._fmt(abs(imag)))
        else:
            r1 = (-b + math.sqrt(disc)) / (2 * a)
            r2 = (-b - math.sqrt(disc)) / (2 * a)
            ans = "%s = %s or %s = %s" % (var, cls._fmt(r1), var, cls._fmt(r2))
        steps.append("Apply the quadratic formula (-b ± √Δ) / 2a.")
        return cls._fmt_steps("Quadratic equation solver", steps, ans)

    @classmethod
    def solve_equation(cls, eq: str, var: str = None) -> str:
        sides = eq.split('=')
        if len(sides) != 2:
            return "Invalid equation (need exactly one '=')"
        lhs, rhs = sides
        if not var:
            known = set(cls.CONSTANTS.keys()) | {
                'sin','cos','tan','sqrt','log','ln','exp','abs','pi','e'
            }
            vars_found = set(re.findall(r'[a-zA-Z]+', eq)) - known
            var = next(iter(vars_found), None)
        if not var:
            return "No variable found in equation"
        quadratic = cls._solve_quadratic_coefficients(eq, var)
        if quadratic:
            return quadratic
        linear = cls._solve_linear_equation(lhs, rhs, var)
        if linear:
            return linear
        f = lambda x: cls.evaluate('(%s)-(%s)' % (lhs, rhs), {var: x})
        lo, hi = -1e6, 1e6
        for _ in range(100):
            try:
                if f(lo) * f(hi) <= 0:
                    break
            except Exception:
                pass
            lo *= 2
            hi *= 2
        root = None
        try:
            for _ in range(100):
                mid = (lo + hi) / 2.0
                fmid = f(mid)
                if abs(fmid) < 1e-12 or (hi - lo) < 1e-12:
                    root = mid
                    break
                if f(lo) * fmid <= 0:
                    hi = mid
                else:
                    lo = mid
            if root is None:
                root = mid
        except Exception:
            pass
        if root is None:
            return "No real solution found for %s" % var
        root = round(root, 8)
        if isinstance(root, float) and root == int(root):
            root = int(root)
        return "%s = %s" % (var, root)

    @staticmethod
    def _normalize_math_language(text: str) -> str:
        replacements = [
            (r"\bwhats\b", "what is"),
            (r"\bplus\b", "+"),
            (r"\bminus\b", "-"),
            (r"\btimes\b|\bmultiplied by\b", "*"),
            (r"\bdivided by\b|\bover\b", "/"),
            (r"\bto the power of\b|\bto the power\b|\bpower of\b", "^"),
            (r"\bsquared\b", "^2"),
            (r"\bcubed\b", "^3"),
        ]
        normalized = text
        for pattern, replacement in replacements:
            normalized = re.sub(pattern, replacement, normalized, flags=re.I)
        return normalized

    @classmethod
    def process(cls, text: str):
        t = cls._normalize_math_language(text.lower().strip())
        t = re.sub(
            r'^(calculate|compute|what is|what\'s|find|solve|evaluate|'
            r'value of|work out|figure out)\s+', '', t, flags=re.I
        )

        # Percentages
        m = re.search(r'(?:what\s+is\s+)?([\d.]+)\s*%\s+of\s+([\d.]+)', t)
        if m:
            pct, whole = float(m.group(1)), float(m.group(2))
            result = whole * pct / 100
            return cls._fmt_steps("Percentage solver", ["Convert %s%% to decimal: %s/100 = %s." % (cls._fmt(pct), cls._fmt(pct), cls._fmt(pct / 100)), "Multiply by the whole: %s × %s." % (cls._fmt(whole), cls._fmt(pct / 100))], cls._fmt(result)), 1.0

        # Fibonacci
        m = re.search(r'fibonacci(?:\s+sequence)?\s+(?:of\s+|for\s+)?(\d+)', t)
        if m:
            n = int(m.group(1))
            seq = cls.fibonacci(n)
            return "First %d Fibonacci numbers: %s" % (n, seq), 1.0

        # Statistics
        m = re.search(
            r'(mean|median|mode|std|standard deviation|variance|statistics|stats)'
            r'\s+(?:of\s+)?([\d\s,\.]+)', t
        )
        if m:
            nums_raw = re.findall(r'[\d.]+', m.group(2))
            nums = [float(x) for x in nums_raw]
            s = cls.stats(nums)
            stat_type = m.group(1).lower()
            if stat_type in ('mean', 'average'):
                return "Mean = %s" % cls._fmt(s['mean']), 1.0
            if stat_type == 'median':
                return "Median = %s" % cls._fmt(s['median']), 1.0
            if stat_type == 'mode':
                return "Mode = %s" % str(s['mode']), 1.0
            if stat_type in ('std', 'standard deviation'):
                return "Std Dev = %s" % cls._fmt(s['std_dev']), 1.0
            if stat_type == 'variance':
                return "Variance = %s" % cls._fmt(s['variance']), 1.0
            lines = ["  %s: %s" % (k, cls._fmt(v) if isinstance(v, float) else str(v))
                     for k, v in s.items()]
            return "Statistics:\n" + "\n".join(lines), 1.0

        # Unit conversion
        m = re.search(r'([\d.]+)\s*(\w+)\s+(?:to|in|into|as)\s+(\w+)', t)
        if m:
            val, fu, tu = float(m.group(1)), m.group(2), m.group(3)
            try:
                result = cls.convert_units(val, fu, tu)
                return "%s %s = %s %s" % (val, fu, cls._fmt(result), tu), 1.0
            except Exception:
                pass

        # Derivative
        m = re.search(
            r'(?:derivative|differentiate|d/dx|gradient)\s+(?:of\s+)?(.+?)'
            r'(?:\s+at\s+([\d.]+))?$', t
        )
        if m:
            expr, at_pt = m.group(1).strip(), m.group(2)
            if at_pt:
                point = float(at_pt)
                result = cls.derivative_numeric(expr, 'x', point)
                return "d/dx(%s) at x=%s = %s" % (expr, point, cls._fmt(result)), 1.0
            sym = cls.derivative_symbolic(expr)
            return "d/dx(%s) = %s" % (expr, sym), 1.0

        # Integral
        m = re.search(
            r'integrat(?:e|ion)\s+(?:of\s+)?(.+?)\s+from\s+([\d.\-]+)\s+to\s+([\d.\-]+)', t
        )
        if m:
            expr, a, b = m.group(1), float(m.group(2)), float(m.group(3))
            result = cls.integrate_numeric(expr, 'x', a, b)
            return "integral(%s)dx from %s to %s = %s" % (expr, a, b, cls._fmt(result)), 1.0

        # Is prime
        m = re.search(r'is\s+(\d+)\s+(?:a\s+)?prime', t)
        if m:
            n = int(m.group(1))
            answer = "%d is prime" % n if cls.is_prime(n) else "%d is NOT prime" % n
            return answer, 1.0

        # Prime factors
        m = re.search(r'(?:prime\s+factors?\s+of|factorise|factorize)\s+(\d+)', t)
        if m:
            n = int(m.group(1))
            factors = cls.prime_factors(n)
            return "Prime factors of %d: %s" % (n, ' x '.join(map(str, factors))), 1.0

        # GCD
        m = re.search(r'gcd\s+(?:of\s+)?(\d+)\s+(?:and\s+)?(\d+)', t)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            return "GCD(%d, %d) = %d" % (a, b, cls.gcd(a, b)), 1.0

        # LCM
        m = re.search(r'lcm\s+(?:of\s+)?(\d+)\s+(?:and\s+)?(\d+)', t)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            return "LCM(%d, %d) = %d" % (a, b, cls.lcm(a, b)), 1.0

        # Combinations
        m = re.search(r'(?:C|nCr|choose)\s*\(?(\d+)[,\s]+(\d+)\)?', t)
        if m:
            n, r = int(m.group(1)), int(m.group(2))
            return "C(%d,%d) = %d" % (n, r, math.comb(n, r)), 1.0

        # Permutations
        m = re.search(r'(?:P|nPr|permutation)\s*\(?(\d+)[,\s]+(\d+)\)?', t)
        if m:
            n, r = int(m.group(1)), int(m.group(2))
            return "P(%d,%d) = %d" % (n, r, math.perm(n, r)), 1.0

        # Equation with variable
        if '=' in t and re.search(r'[a-zA-Z]', t):
            result = cls.solve_equation(t)
            return result, 1.0

        # Plain expression
        try:
            val = cls.evaluate(t)
            return cls._fmt_steps("Arithmetic evaluator", ["Parse the expression with standard precedence: parentheses, powers, multiplication/division, addition/subtraction.", "Evaluate safely without Python eval."], cls._fmt(val)), 1.0
        except Exception:
            pass

        return None, 0.0


# ══════════════════════════════════════════════════════════════════════
#  SECTION 2 — SENTENCE GENERATOR
# ══════════════════════════════════════════════════════════════════════

class SentenceGenerator:

    FALLBACKS = [
        "I can chat about that, but I need a little more detail. What angle do you want to explore?",
        "I’m not fully sure yet, but I can help reason it out. Tell me one more detail and I’ll try a smarter answer.",
        "Got it. I can keep learning from this conversation — ask it another way or teach me with: learn question | answer.",
        "I’m still building knowledge there, but I can help brainstorm, simplify, or make a plan.",
        "Interesting — give me a bit more context and I’ll connect it to what I already know.",
    ]

    GREETING_RESPONSES = [
        "Hey! Great to see you. What's on your mind?",
        "Hello! Ready to help — what can I do for you?",
        "Hi there! Ask me anything.",
        "Hey! I'm all ears.",
        "What's up! How can I help?",
    ]

    CONFIRM_RESPONSES = [
        "Absolutely!", "Of course!", "Sure thing!", "You got it!",
        "100%!", "Definitely!", "Without a doubt!",
    ]

    def __init__(self):
        self.chain = defaultdict(list)
        self.trained = False
        self._order = 2

    def train(self, corpus: list):
        for text in corpus:
            words = text.split()
            if len(words) < self._order + 1:
                continue
            for i in range(len(words) - self._order):
                key = tuple(words[i:i + self._order])
                self.chain[key].append(words[i + self._order])
        self.trained = bool(self.chain)

    def generate(self, seed_words=None, max_words=30) -> str:
        if not self.trained or not self.chain:
            return random.choice(self.FALLBACKS)
        keys = list(self.chain.keys())
        if seed_words:
            matching = [k for k in keys if any(sw in k for sw in seed_words)]
            start = random.choice(matching) if matching else random.choice(keys)
        else:
            start = random.choice(keys)
        words = list(start)
        for _ in range(max_words - self._order):
            key = tuple(words[-self._order:])
            if key not in self.chain:
                break
            words.append(random.choice(self.chain[key]))
            if words[-1].endswith(('.', '!', '?')):
                break
        sentence = ' '.join(words)
        if sentence:
            return sentence[0].upper() + sentence[1:]
        return random.choice(self.FALLBACKS)

    def greeting(self) -> str:
        return random.choice(self.GREETING_RESPONSES)

    def confirm(self) -> str:
        return random.choice(self.CONFIRM_RESPONSES)

    def fallback(self) -> str:
        return random.choice(self.FALLBACKS)


# ══════════════════════════════════════════════════════════════════════
#  SECTION 3 — INTENT CLASSIFIER
# ══════════════════════════════════════════════════════════════════════

class IntentClassifier:

    PATTERNS = {
        'greeting':    r'^(hi|hello|hey|sup|yo|howdy|good\s*(morning|evening|afternoon|night))',
        'farewell':    r'^(bye|goodbye|see\s*ya|farewell|exit|quit|shutdown|cya|later)',
        'affirmation': r'^(yes|yeah|yep|yup|sure|ok|okay|correct|right|exactly|absolutely|'
                       r'definitely|indeed|true|confirmed)',
        'negation':    r'^(no|nah|nope|wrong|incorrect|false|not really|never)',
        'math':        r'(\d[\d\s\+\-\*\/\^\(\)\.]*[\d\)]|'
                       r'derivative|integral|integrate|differentiate|'
                       r'solve|equation|factorial|fibonacci|prime|gcd|lcm|'
                       r'sin|cos|tan|sqrt|log|mean|median|mode|std|variance|'
                       r'convert|permutation|combination)',
        'learn':       r'^learn\s+.+\|.+',
        'recall':      r"(what is|what's) my\s+\w+",
        'remember':    r'^remember my\s+.+\s+is\s+.+',
        'question':    r'\?$|^(what|who|where|when|why|how|which|whose|whom)',
        'small_talk':  r'^(how are you|how\'s it going|what\'s up|are you|do you|can you|i\'m doing|i am doing|doing fine|doing good|doing well)',
    }

    COMPILED = {intent: re.compile(pat, re.IGNORECASE)
                for intent, pat in PATTERNS.items()}

    SMALL_TALK_RESPONSES = {
        r"how are you|how's it going|how are you doing": [
            "I'm doing great, thanks for asking! What can I help you with?",
            "Running at peak performance! What's on your mind?",
            "Fantastic! Ready to tackle anything.",
        ],
        r"i'?m doing|i am doing|doing fine|doing good|doing well": [
            "Nice — glad to hear it! Want to chat, learn something, or solve a problem?",
            "Awesome. I'm here for chatting, quick learning, or math whenever you're ready.",
        ],
        r'are you (human|a robot|an ai|real)': [
            "I'm an AI — but a pretty smart one! Ask me anything.",
            "AI through and through. What do you need?",
        ],
        r'what can you do': [
            "I can solve complex math, answer questions, learn new things, "
            "remember facts about you, and hold a decent conversation. Try me!",
        ],
        r'who made you|who created you|who built you': [
            "I was built as part of the Stellight AI Prototype. My creator put a lot of love into my brain!",
        ],
    }

    @classmethod
    def classify(cls, text: str) -> str:
        t = text.lower().strip()
        # Conversational phrases like "how are you doing" should not be
        # swallowed by the broad question detector just because they start with how.
        if cls.COMPILED['small_talk'].search(t):
            return 'small_talk'
        for intent, pattern in cls.COMPILED.items():
            if intent == 'small_talk':
                continue
            if pattern.search(t):
                return intent
        return 'unknown'

    @classmethod
    def get_small_talk_response(cls, text: str):
        t = text.lower().strip()
        for pattern, responses in cls.SMALL_TALK_RESPONSES.items():
            if re.search(pattern, t, re.I):
                return random.choice(responses)
        return None


# ══════════════════════════════════════════════════════════════════════
#  SECTION 4 — CONTEXT MANAGER
# ══════════════════════════════════════════════════════════════════════

class ContextManager:

    def __init__(self, window: int = 6):
        self.window = window
        self.turns = []
        self.entities = {}
        self.topic = None

    def add_turn(self, user_msg: str, bot_msg: str):
        self.turns.append({'user': user_msg, 'bot': bot_msg})
        if len(self.turns) > self.window:
            self.turns.pop(0)
        self._extract_entities(user_msg)

    def _extract_entities(self, text: str):
        m = re.search(r"(?:my name is|i am|call me|i'm)\s+([A-Za-z]+)", text, re.I)
        if m:
            self.entities['name'] = m.group(1).strip()
        m = re.search(r"i(?:'m| am)\s+(\d+)\s+years?\s+old", text, re.I)
        if m:
            self.entities['age'] = m.group(1)

    def inject_name(self, response: str) -> str:
        name = self.entities.get('name')
        if name and random.random() < 0.3:
            starters = [
                "Great question, %s!" % name,
                "Sure thing, %s." % name,
                "%s," % name,
            ]
            response = random.choice(starters) + ' ' + response
        return response


# ══════════════════════════════════════════════════════════════════════
#  SECTION 5 — DECISION BRAIN v2
# ══════════════════════════════════════════════════════════════════════

class DecisionBrain:
    def __init__(self, memory_manager, knowledge_engine):
        self.memory    = memory_manager
        self.knowledge = knowledge_engine
        self.math      = AdvancedMathEngine()
        self.generator = SentenceGenerator()
        self.intent    = IntentClassifier()
        self.context   = ContextManager()
        self.HIGH_CONF = 0.85
        self.LOW_CONF  = 0.50
        self._sync_generator()

    def _sync_generator(self):
        answers = list(self.knowledge.answer_by_idx.values())
        if answers:
            self.generator.train(answers)

    def retrain_generator(self):
        self._sync_generator()

    @staticmethod
    def _split_multi(text: str) -> list:
        parts = re.split(r'\s+(?:then|and also|also|,\s*and)\s+', text, flags=re.I)
        return [p.strip() for p in parts if p.strip()]

    def process_pipeline(self, user: str, raw_message: str):
        msg = raw_message.strip()
        msg_lower = msg.lower()
        intent = self.intent.classify(msg)

        # Greeting
        if intent == 'greeting':
            resp = self.generator.greeting()
            name = self.context.entities.get('name')
            if name:
                resp = "Hey %s! " % name + resp.split('!', 1)[-1].strip()
            self.context.add_turn(msg, resp)
            return resp, 1.0

        # Farewell
        if intent == 'farewell':
            return '__EXIT__', 1.0

        # Affirmation
        if intent == 'affirmation':
            resp = self.generator.confirm()
            self.context.add_turn(msg, resp)
            return resp, 1.0

        # Small talk
        if intent == 'small_talk':
            resp = self.intent.get_small_talk_response(msg)
            if resp:
                self.context.add_turn(msg, resp)
                return resp, 1.0

        # Remember profile fact
        if intent == 'remember':
            m = re.match(r"remember my (.+?) is (.+)", msg, re.I)
            if m:
                key, val = m.group(1).strip(), m.group(2).strip()
                self.memory.remember_profile_fact(user, key, val)
                self.context.entities[key.lower()] = val
                resp = "Got it! I'll remember your %s is '%s'." % (key, val)
                self.context.add_turn(msg, resp)
                return resp, 1.0

        # Recall profile fact
        if intent == 'recall':
            m = re.match(r"(?:what is|what's) my (.+?)[\?]?$", msg_lower)
            if m:
                attr = m.group(1).strip()
                fact = self.memory.get_profile_fact(user, attr)
                if fact:
                    resp = "Your %s is '%s'." % (attr, fact)
                    self.context.add_turn(msg, resp)
                    return resp, 1.0
                resp = ("I don't have your %s stored yet. "
                        "Tell me with: remember my %s is [value]") % (attr, attr)
                self.context.add_turn(msg, resp)
                return resp, 0.9

        # Auto entity extraction
        self.context._extract_entities(msg)

        # Math — handle multi-part queries
        parts = self._split_multi(msg)
        math_results = []
        all_math = True
        for part in parts:
            result, conf = self.math.process(part)
            if result is not None:
                math_results.append(result)
            else:
                all_math = False

        if math_results and (all_math or intent == 'math'):
            resp = '\n'.join(math_results)
            resp = self.context.inject_name(resp)
            self.context.add_turn(msg, resp)
            return resp, 1.0

        # Knowledge base semantic lookup
        answer, confidence = self.knowledge.query_semantic_match(msg_lower)

        if answer is not None and confidence >= self.HIGH_CONF:
            resp = self.context.inject_name(answer)
            self.context.add_turn(msg, resp)
            return resp, confidence

        # Medium confidence — return KB answer
        if answer is not None and confidence >= self.LOW_CONF:
            self.context.add_turn(msg, answer)
            return answer, confidence

        # Low confidence — try Markov generation
        seed_words = [w for w in msg_lower.split()
                      if len(w) > 3 and w not in {'what', 'does', 'this', 'that', 'with'}]
        generated = self.generator.generate(seed_words=seed_words)
        if generated and "interesting question" not in generated:
            self.context.add_turn(msg, generated)
            return generated, 0.3

        # Full fallback: give a useful conversational answer instead of forcing teaching.
        fallback = self.generator.fallback()
        self.context.add_turn(msg, fallback)
        return fallback, 0.55
