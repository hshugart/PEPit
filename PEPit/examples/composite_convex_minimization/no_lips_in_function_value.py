import numpy as np

from PEPit.pep import PEP
from PEPit.functions.convex_function import ConvexFunction
from PEPit.functions.convex_indicator import ConvexIndicatorFunction
from PEPit.primitive_steps.bregman_gradient_step import bregman_gradient_step


def wc_no_lips_in_function_value(L, gamma, n, verbose=True):
    """
    Consider the constrainted composite convex minimization problem

    .. math:: F_\\star \\triangleq \\min_x \\{F(x) \\equiv f_1(x) + f_2(x)\\},

    where :math:`f_1` is convex and :math:`L`-smooth relatively to :math:`h`,
    :math:`h` being closed proper and convex,
    and where :math:`f_2` is a closed convex indicator function.

    This code computes a worst-case guarantee for the **NoLips** method.
    That is, it computes the smallest possible :math:`\\tau(n, L)` such that the guarantee

    .. math :: F(x_n) - F_\\star \\leqslant \\tau(n, L) D_h(x_\\star; x_0),

    is valid, where :math:`x_n` is the output of the **NoLips** method,
    where :math:`x_\\star` is a minimizer of :math:`F`,
    and where :math:`D_h` is the Bregman divergence generated by :math:`h`.
    In short, for given values of :math:`n` and :math:`L`,
    :math:`\\tau(n, L)` is computed as the worst-case value of
    :math:`F(x_n) - F_\\star` when :math:`D_h(x_\\star; x_0) \\leqslant 1`.

    **Algorithm**: This method (also known as Bregman Gradient, or Mirror descent) can be found in, e.g., [2, Algorithm 1]

        .. math:: x_{t+1} = \\arg\\min_{u} \\{f_2(u)+\\langle \\nabla f_1(x_t) \\mid u - x_t \\rangle + \\frac{1}{\\gamma} D_h(u; x_t)\\}.

    **Theoretical guarantee**:

    The **tight** guarantee obtained in [2, Theorem 1] is

        .. math :: F(x_n) - F_\\star \\leqslant \\frac{1}{\\gamma n} D_h(x_\\star; x_0),

    for any :math:`\\gamma \\leq \\frac{1}{L}`; tightness is provided in [2, page 23].

    **References**: NoLips was proposed [1] for convex problems involving relative smoothness.
    The worst-case analysis using a PEP, as well as the tightness are provided in [2].

    `[1] H.H. Bauschke, J. Bolte, M. Teboulle (2017). A Descent Lemma
    Beyond Lipschitz Gradient Continuity: First-Order Methods Revisited and Applications.
    Mathematics of Operations Research, 2017, vol. 42, no 2, p. 330-348.
    <https://cmps-people.ok.ubc.ca/bauschke/Research/103.pdf>`_

    `[2] R. Dragomir, A. Taylor, A. d’Aspremont, J. Bolte (2021). Optimal complexity and certification of Bregman
    first-order methods. Mathematical Programming, 1-43.
    <https://arxiv.org/pdf/1911.08510.pdf>`_

    Notes:
        Disclaimer: This example requires some experience with PEPit and PEPs ([2], section 4).

    Args:
        L (float): relative-smoothness parameter
        gamma (float): step-size.
        n (int): number of iterations.
        verbose (bool): if True, print conclusion

    Returns:
        pepit_tau (float): worst-case value
        theoretical_tau (float): theoretical value

    Example: **TOUPDATE**
        >>> L = 1
        >>> gamma = 1 / (2*L)
        >>> pepit_tau, theoretical_tau = wc_no_lips_in_function_value(L=L, gamma=gamma, n=3, verbose=True)
        (PEP-it) Setting up the problem: size of the main PSD matrix: 15x15
        (PEP-it) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEP-it) Setting up the problem: initial conditions (1 constraint(s) added)
        (PEP-it) Setting up the problem: interpolation conditions for 3 function(s)
                 function 1 : 20 constraint(s) added
                 function 2 : 20 constraint(s) added
                 function 3 : 16 constraint(s) added
        (PEP-it) Compiling SDP
        (PEP-it) Calling SDP solver
        (PEP-it) Solver status: optimal (solver: SCS); optimal value: 0.6666714558260607
        *** Example file: worst-case performance of the NoLips in function values ***
            PEP-it guarantee:		 F(x_n) - F_* <= 0.666671 Dh(x_*, x_0)
            Theoretical guarantee :	 F(x_n) - F_* <= 0.666667 Dh(x_*, x_0)

    """

    # Instantiate PEP
    problem = PEP()

    # Declare two convex functions and a convex indicator function
    d = problem.declare_function(ConvexFunction, param={}, reuse_gradient=True)
    func1 = problem.declare_function(ConvexFunction, param={}, reuse_gradient=True)
    h = (d + func1) / L
    func2 = problem.declare_function(ConvexIndicatorFunction, param={'D': np.inf})
    # Define the function to optimize as the sum of func1 and func2
    func = func1 + func2

    # Start by defining its unique optimal point xs = x_* and its function value fs = F(x_*)
    xs = func.stationary_point()
    ghs, hs = h.oracle(xs)
    gfs, fs = func1.oracle(xs)

    # Then define the starting point x0 of the algorithm and its function value f0
    x0 = problem.set_initial_point()
    gh0, h0 = h.oracle(x0)
    gf0, f0 = func1.oracle(x0)

    # Set the initial constraint that is the Bregman distance between x0 and x^*
    problem.set_initial_condition(hs - h0 - gh0 * (xs - x0) <= 1)

    # Compute n steps of the NoLips starting from x0
    gfx = gf0
    ffx = f0
    ghx = gh0
    for i in range(n):
        x, _, _ = bregman_gradient_step(gfx, ghx, func2 + h, gamma)
        gfx, ffx = func1.oracle(x)
        gdx = d.gradient(x)
        ghx = (gdx + gfx) / L

    # Set the performance metric to the final distance in function values to optimum
    problem.set_performance_metric(ffx - fs)

    # Solve the PEP
    pepit_tau = problem.solve(verbose=verbose)

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = 1 / (gamma * n)

    # Print conclusion if required
    if verbose:
        print('*** Example file: worst-case performance of the NoLips in function values ***')
        print('\tPEP-it guarantee:\t\t F(x_n) - F_* <= {:.6} Dh(x_*, x_0)'.format(pepit_tau))
        print('\tTheoretical guarantee :\t F(x_n) - F_* <= {:.6} Dh(x_*, x_0) '.format(
            theoretical_tau))
    # Return the worst-case guarantee of the evaluated method (and the upper theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":

    L = 1
    gamma = 1 / (2*L)
    pepit_tau, theoretical_tau = wc_no_lips_in_function_value(L=L, gamma=gamma, n=3, verbose=True)
