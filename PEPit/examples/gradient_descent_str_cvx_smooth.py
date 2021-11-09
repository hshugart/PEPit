from math import sqrt

from PEPit.pep import PEP
from PEPit.functions.smooth_strongly_convex_function import SmoothStronglyConvexFunction


def compute_rate_and_proof_n_steps_gd_on_str_cvx_smooth(mu, L, n, alternating_steps=False):
    """
    Compute the rate of n steps of GD methods over strongly convex and smooth functions class.
    Computed either for optimized constant step size or optimized alternating one.

    :param mu: (float) the strong convexity constant.
    :param L: (float) the smoothness constant.
    :param n: (int) number of iterations. Actually, 2.[n/2]is the real number of steps.
    :param alternating_steps: (bool) whether to use alternating step-sizes or not.
    :return:
    """

    # Instantiate PEP
    problem = PEP()

    # Define step sizes, alternating or not
    if alternating_steps:
        gamma0 = 1 / L * (sqrt(L ** 2 + (L - mu) ** 2) - mu) / (L - mu)
        gamma1 = 1 / L * (sqrt(L ** 2 + (L - mu) ** 2) + 2 * L + mu) / (L + 3 * mu)
    else:
        gamma = 2 / (L + mu)
        gamma0 = gamma
        gamma1 = gamma

    # Declare a strongly convex smooth function
    func = problem.declare_function(SmoothStronglyConvexFunction, param={'mu': mu, 'L': L})

    # Start by defining its unique optimal point
    xs = func.stationary_point()

    # Then Define the starting point of the algorithm
    x0 = problem.set_initial_point()

    # Set the initial constraint that is the distance between x0 and x^*
    problem.set_initial_condition((x0 - xs) ** 2 <= 1)

    # Run the GD method
    x = x0
    for i in range(n):
        if i % 2 == 0:
            x = x - gamma0 * func.gradient(x)
        else:
            x = x - gamma1 * func.gradient(x)

    # Set the performance metric to the final distance to optimum
    problem.set_performance_metric((x - xs) ** 2)

    # Solve the PEP
    rate = problem.solve()

    # Get the dual values, giving the proof
    dual_values = [constraint.dual_variable_value for constraint in func.list_of_constraints]

    # Return the rate of the evaluated method
    return rate, dual_values


if __name__ == "__main__":
    n = 4
    mu = .1
    L = 1

    rate, _ = compute_rate_and_proof_n_steps_gd_on_str_cvx_smooth(mu=mu, L=L, n=n, alternating_steps=False)
    accelerated_rate, _ = compute_rate_and_proof_n_steps_gd_on_str_cvx_smooth(mu=mu, L=L, n=n, alternating_steps=True)
    print('{} < {}'.format(accelerated_rate, rate))