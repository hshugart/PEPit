from PEPit.function import Function


class StronglyConvexFunction(Function):
    """
    Smooth strongly convex function
    """

    def __init__(self,
                 param,
                 is_leaf=True,
                 decomposition_dict=None,
                 is_differentiable=False):
        """
        Class of smooth strongly convex functions.
        The differentiability is necessarily verified.

        :param param: (dict) contains the values of mu and L
        :param is_leaf: (bool) If True, it is a basis function. Otherwise it is a linear combination of such functions.
        :param decomposition_dict: (dict) Decomposition in the basis of functions.
        """
        super().__init__(is_leaf=is_leaf,
                         decomposition_dict=decomposition_dict,
                         is_differentiable=is_differentiable)

        # Store mu and L
        self.mu = param['mu']

    def add_class_constraints(self):
        """
        Add all the interpolation condition of the strongly convex smooth functions
        """

        for i, point_i in enumerate(self.list_of_points):

            xi, gi, fi = point_i

            for j, point_j in enumerate(self.list_of_points):

                xj, gj, fj = point_j

                if i != j:

                    # Interpolation conditions of smooth strongly convex functions class
                    self.add_constraint(fi - fj >=
                                        gj * (xi - xj)
                                        + self.mu / 2 * (xi - xj) ** 2)