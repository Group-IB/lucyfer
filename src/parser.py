from django.db.models import Q
from sympy import simplify, SympifyError, And, Symbol, Or

from src.utils import LuceneSearchError


PARSING_NECESSARY_OPERATORS = {"(", ")", "OR", "AND", "||", "&&"}
LUCENE_OPERATORS = {"(", ")", "|", "&"}


class BaseLuceneParserMixin:
    variable_template = "a_{}"

    @classmethod
    def _parse_tree(cls, tree, variable_name_to_query_term):
        raise NotImplementedError()

    @classmethod
    def parse(cls, raw_expression):
        simplified_expression, variable_name_to_raw_value = cls._replace_expressions_by_variables(raw_expression)
        variable_name_to_query_term = cls.validate_tokens(variable_name_to_raw_value=variable_name_to_raw_value)

        try:
            # todo remove sympy lib
            tree = simplify(simplified_expression)
        except (SyntaxError, SympifyError):
            raise LuceneSearchError()

        return cls._parse_tree(tree=tree, variable_name_to_query_term=variable_name_to_query_term)

    @classmethod
    def _replace_expressions_by_variables(cls, raw_expression: str):
        """
        raw_expression for ex. (x: 2) OR ((y: 3) AND z < 4)

        result contains:
        variable_to_expression (dict): {"a_1": "x: 2", "a_2": "y: 3", "a_3": "z < 4"}
        simplified_raw_expression (str): "a_1 || ((a_2) && a_3)"
        """

        raw_expression = raw_expression.strip()
        if not raw_expression:
            raise LuceneSearchError()

        if not any(op in raw_expression for op in PARSING_NECESSARY_OPERATORS):
            return "a_1", {"a_1": raw_expression}

        # prepare string, replace all lucene operators to sympy operators
        for sympy_operator, lucene_valid_operators in {"|": ["OR", "||"], "&": ["AND", "&&"]}.items():
            for lucene_operator in lucene_valid_operators:
                raw_expression = raw_expression.replace(lucene_operator, sympy_operator)

        # split prepared expression to tokens
        tokens = list()

        future_var_index_start = -1
        last_index = len(raw_expression) - 1

        variable_name_to_raw_expression = dict()

        current_quote = None
        dash_counter = 0

        for index, letter in enumerate(raw_expression):
            if letter in {"'", '"'}:
                if letter == current_quote:  # end of user string
                    current_quote = None
                else:
                    current_quote = letter

            if current_quote is not None:  # if current part is user string
                continue

            # check dashes validity
            if letter == "(":
                dash_counter += 1
            elif letter == ")":
                dash_counter -= 1

            if dash_counter < 0:
                raise LuceneSearchError()

            # ok token creating part
            if letter == " ":
                continue

            if letter in LUCENE_OPERATORS:
                if future_var_index_start >= 0:
                    token = raw_expression[future_var_index_start:index].strip()
                    if token:
                        variable_name = cls.variable_template.format(str(index))

                        variable_name_to_raw_expression[variable_name] = token
                        tokens.append(variable_name)

                    future_var_index_start = -1

                tokens.append(letter)
                continue
            elif future_var_index_start < 0:
                future_var_index_start = index

            if (index == last_index) and (future_var_index_start >= 0):
                if current_quote is not None and letter != current_quote:
                    raise LuceneSearchError()

                token = raw_expression[future_var_index_start:index + 1].strip()
                if token:
                    variable_name = cls.variable_template.format(str(index))

                    variable_name_to_raw_expression[variable_name] = token
                    tokens.append(variable_name)

        if dash_counter != 0:
            raise LuceneSearchError()

        return " ".join(tokens), variable_name_to_raw_expression


class LuceneToDjangoParserMixin(BaseLuceneParserMixin):
    @classmethod
    def _parse_tree(cls, tree, variable_name_to_query_term):
        if isinstance(tree, Symbol):
            return variable_name_to_query_term.get(tree.name, Q())

        if isinstance(tree, And):
            query = Q()
            for arg in tree.args:
                query = query & cls._parse_tree(tree=arg, variable_name_to_query_term=variable_name_to_query_term)
            return (query)

        if isinstance(tree, Or):
            query = Q()
            for arg in tree.args:
                query = query | cls._parse_tree(tree=arg, variable_name_to_query_term=variable_name_to_query_term)
            return (query)

        return Q()
