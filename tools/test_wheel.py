"""Smoke test for wheel builds: imports cyipopt and solves HS071."""
import numpy as np
import cyipopt


class HS071:

    def objective(self, x):
        return x[0] * x[3] * np.sum(x[0:3]) + x[2]

    def gradient(self, x):
        return np.array([
            x[0] * x[3] + x[3] * np.sum(x[0:3]),
            x[0] * x[3],
            x[0] * x[3] + 1.0,
            x[0] * np.sum(x[0:3])
        ])

    def constraints(self, x):
        return np.array((np.prod(x), np.dot(x, x)))

    def jacobian(self, x):
        return np.concatenate((np.prod(x) / x, 2 * x))

    def hessianstructure(self):
        return np.nonzero(np.tril(np.ones((4, 4))))

    def hessian(self, x, lagrange, obj_factor):
        H = obj_factor * np.array((
            (2 * x[3], 0, 0, 0),
            (x[3], 0, 0, 0),
            (x[3], 0, 0, 0),
            (2 * x[0] + x[1] + x[2], x[0], x[0], 0)))
        H += lagrange[0] * np.array((
            (0, 0, 0, 0),
            (x[2] * x[3], 0, 0, 0),
            (x[1] * x[3], x[0] * x[3], 0, 0),
            (x[1] * x[2], x[0] * x[2], x[0] * x[1], 0)))
        H += lagrange[1] * 2 * np.eye(4)
        row, col = self.hessianstructure()
        return H[row, col]


def main():
    x0 = [1.0, 5.0, 5.0, 1.0]
    lb = [1.0, 1.0, 1.0, 1.0]
    ub = [5.0, 5.0, 5.0, 5.0]
    cl = [25.0, 40.0]
    cu = [2.0e19, 40.0]

    nlp = cyipopt.Problem(
        n=len(x0),
        m=len(cl),
        problem_obj=HS071(),
        lb=lb,
        ub=ub,
        cl=cl,
        cu=cu,
    )
    nlp.add_option('mu_strategy', 'adaptive')
    nlp.add_option('tol', 1e-7)
    nlp.add_option('print_level', 0)

    x, info = nlp.solve(x0)

    # Known optimal solution for HS071
    x_expected = np.array([1.0, 4.74299963, 3.82114998, 1.37940829])
    obj_expected = 17.014017145179164

    assert info['status'] == 0, f"Solver did not converge: status={info['status']}"
    assert np.allclose(x, x_expected, atol=1e-4), f"Unexpected solution: {x}"
    assert np.isclose(info['obj_val'], obj_expected, atol=1e-4), (
        f"Unexpected objective: {info['obj_val']}"
    )

    print(f"cyipopt {cyipopt.__version__} — wheel smoke test passed")


if __name__ == '__main__':
    main()
