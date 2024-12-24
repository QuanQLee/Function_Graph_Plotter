# modules/function_parser.py

import sympy as sp


class FunctionParser:
    def __init__(self, func_str, variables=('x',)):
        """
        初始化函数解析器。

        :param func_str: 用户输入的函数表达式，例如 "sin(a * x) + b" 或 "sin(a * x) + b * y"
        :param variables: 函数的自变量列表，例如 ('x',) 或 ('x', 'y')
        """
        self.func_str = func_str
        self.variables = [sp.symbols(var) for var in variables]
        self.expr = None
        self.params = []
        self.lambdified_func = None
        self.lambdified_derivative = {}
        self.lambdified_integral = {}
        self.derivative_expr = {}
        self.integral_expr = {}

    def parse_expression(self):
        try:
            self.expr = sp.sympify(self.func_str)
            symbols = sorted(self.expr.free_symbols, key=lambda s: s.name)
            # 分离参数（非自变量）
            self.params = [str(s) for s in symbols if str(s) not in [str(var) for var in self.variables]]
            return True, ""
        except Exception as e:
            return False, str(e)

    def generate_functions(self):
        try:
            all_symbols = self.variables + [sp.symbols(p) for p in self.params]
            self.lambdified_func = sp.lambdify(all_symbols, self.expr, modules=['numpy'])

            # 生成导数和积分函数
            for var in self.variables:
                deriv_expr = sp.diff(self.expr, var)
                integral_expr = sp.integrate(self.expr, var)

                self.derivative_expr[str(var)] = deriv_expr
                self.lambdified_derivative[str(var)] = sp.lambdify(all_symbols, deriv_expr, modules=['numpy'])

                self.integral_expr[str(var)] = integral_expr
                self.lambdified_integral[str(var)] = sp.lambdify(all_symbols, integral_expr, modules=['numpy'])

            return True, ""
        except Exception as e:
            return False, str(e)
