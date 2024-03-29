import unittest
import numpy as np
import cvxpy as cp
import cpasocp.core.linear_operators as core_lin_op
import cpasocp.core.proximal_offline_part as core_offline


class TestSets(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_offline_part(self):
        prediction_horizon = 60
        proximal_lambda = 1
        n_x = 10
        n_u = 5
        n_c = 7
        n_f = 8
        # A = np.array([[1, 0.7], [-0.1, 1]])  # n x n matrices
        A = np.array(np.random.rand(n_x, n_x))  # n x n matrices
        # B = np.array([[1, 1], [0.5, 1]])  # n x u matrices
        B = np.array(np.random.rand(n_x, n_u))  # n x u matrices

        Q = 10 * np.eye(n_x)  # n x n matrix
        R = np.eye(n_u)  # u x u matrix OR scalar
        P = 5 * np.eye(n_x)  # n x n matrix

        Gamma_x = np.ones((n_c, n_x))  # n_c x n_x matrix
        Gamma_u = np.ones((n_c, n_u))  # n_c x n_u matrix
        Gamma_N = np.ones((n_f, n_x))  # n_f x n_x matrix

        initial_state = np.array(np.random.rand(n_x))
        n_z = (prediction_horizon + 1) * A.shape[1] + prediction_horizon * B.shape[1]
        z0 = np.zeros((n_z, 1))
        # z0 = np.array(np.random.rand(n_z, 1))
        for i in range(initial_state.shape[0]):
            z0[i] = initial_state[i]

        offline = core_offline.ProximalOfflinePart()
        offline.prediction_horizon = prediction_horizon
        offline.state_dynamics = A
        offline.control_dynamics = B
        offline.stage_state_weight = Q
        offline.control_weight = R
        offline.terminal_state_weight = P
        offline.proximal_lambda = proximal_lambda
        offline.algorithm()

        L = core_lin_op.LinearOperator(prediction_horizon, A, B, Gamma_x, Gamma_u, Gamma_N).make_L_op()
        L_z = L * z0
        L_adj = core_lin_op.LinearOperator(prediction_horizon, A, B, Gamma_x, Gamma_u, Gamma_N).make_L_adj()



        # solving OCP by cvxpy
        # -----------------------------
        N = prediction_horizon
        n_x = A.shape[1]
        n_u = B.shape[1]
        c_t_min = - 2 * np.ones(n_c)
        c_t_max = 2 * np.ones(n_c)
        c_N_min = - 2 * np.ones(n_f)
        c_N_max = 2 * np.ones(n_f)
        # Problem statement
        x0_cp = cp.Parameter(n_x)  # <--- x is a parameter of the optimisation problem P_N(x)
        u_seq = cp.Variable((n_u, N))  # <--- sequence of control actions
        x_seq = cp.Variable((n_x, N + 1))

        cost = 0
        constraints = [x_seq[:, 0] == x0_cp]  # Initial Condition x_0 = x

        for t in range(N - 1):
            xt_var = x_seq[:, t]  # x_t
            ut_var = u_seq[:, t]  # u_t
            cost += 0.5 * (cp.quad_form(xt_var, Q) + cp.quad_form(ut_var, R))  # Stage cost

            constraints += [x_seq[:, t + 1] == A @ xt_var + B @ ut_var,  # Dynamics
                            c_t_min <= Gamma_x @ xt_var + Gamma_u @ ut_var,  # State Constraints
                            Gamma_x @ xt_var + Gamma_u @ ut_var <= c_t_max]  # Input Constraints

        xN = x_seq[:, N - 1]
        cost += 0.5 * cp.quad_form(xN, P)  # Terminal cost
        constraints += [c_N_min <= Gamma_N @ xN, Gamma_N @ xN <= c_N_max]  # Terminal constraints

        # Solution
        x0_cp.value = initial_state
        problem = cp.Problem(cp.Minimize(cost), constraints)
        problem.solve()

        # Construct z, z are all the states and inputs in a big vector
        z_cp = np.reshape(x_seq.value[:, 0], (n_x, 1))  # x_0
        z_cp = np.vstack((z_cp, np.reshape(u_seq.value[:, 0], (n_u, 1))))  # u_0

        for i in range(1, N):
            z_cp = np.vstack((z_cp, np.reshape(x_seq.value[:, i], (n_x, 1))))
            z_cp = np.vstack((z_cp, np.reshape(u_seq.value[:, i], (n_u, 1))))

        z_cp = np.vstack((z_cp, np.reshape(x_seq.value[:, N], (n_x, 1))))  # xN

        offline = core_offline.ProximalOfflinePart()
        offline.prediction_horizon = prediction_horizon
        offline.state_dynamics = A
        offline.control_dynamics = B
        offline.stage_state_weight = Q
        offline.control_weight = R
        offline.terminal_state_weight = P
        offline.proximal_lambda = proximal_lambda
        offline.algorithm()
        P_seq = offline.P_seq
        print(P_seq[:, :, 0])


if __name__ == '__main__':
    unittest.main()
