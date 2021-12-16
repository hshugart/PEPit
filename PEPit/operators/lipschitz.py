from PEPit.function import Function


class LipschitzOperator(Function):
    """
    LipschitzOperator class

    Attributes:
        L (float) Lipschitz constant

    Example:
        >>> problem = PEP()
        >>> h = problem.declare_function(function_class=LipschitzOperator, param={'L': 1})

    Notes:
        By setting L=1, we define a non expansive operator.

        By setting L<1, we define a contracting operator.

    References:
        For details about interpolation conditions, we refer to the following :
        [1] E. K. Ryu, A. B. Taylor, C. Bergeling, and P. Giselsson,
        "Operator Splitting Performance Estimation: Tight contraction factors
        and optimal parameter selection," arXiv:1812.00146, 2018.

    """

    def __init__(self,
                 param,
                 is_leaf=True,
                 decomposition_dict=None,
                 reuse_gradient=True):
        """
        Lipschitz operators are characterized by their Lipschitz constant L.

        Args:
            is_leaf (bool): If True, it is a basis function. Otherwise it is a linear combination of such functions.
            decomposition_dict (dict): Decomposition in the basis of functions.
            reuse_gradient (bool): If true, the function can have only one subgradient per point.

        """
        super().__init__(is_leaf=is_leaf,
                         decomposition_dict=decomposition_dict,
                         reuse_gradient=reuse_gradient)
        # Store L
        self.L = param['L']

    def add_class_constraints(self):
        """
        Add all the interpolation condition of the strongly monotone operator
        """

        for i, point_i in enumerate(self.list_of_points):

            xi, gi, fi = point_i

            for j, point_j in enumerate(self.list_of_points):

                xj, gj, fj = point_j

                if (xi != xj) | (gi != gj):
                    # Interpolation conditions of Lipschitz operator class
                    self.add_constraint((gi - gj) ** 2 - self.L ** 2 * (xi - xj) ** 2 <= 0)
