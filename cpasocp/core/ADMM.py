import numpy as np
import scipy as sp
import cpasocp.core.linear_operators as core_lin_op
import cpasocp.core.proximal_online_part as core_online


def make_alpha(prediction_horizon, state_dynamics, control_dynamics, stage_state, control_state, terminal_state,
               initial_guess_z):
    """
    :param initial_guess_z: vector initial guess of (z0) of Chambolle-Pock algorithm
    :param prediction_horizon: prediction horizon (N) of dynamic system
    :param state_dynamics: matrix (A), describing the state dynamics
    :param control_dynamics: matrix (B), describing control dynamics
    :param stage_state: matrix (Gamma_x), describing the state constraints
    :param control_state: matrix (Gamma_u), describing the control constraints
    :param terminal_state: matrix (Gamma_N), describing terminal constraints
    """
    n_z = initial_guess_z.shape[0]
    L = core_lin_op.LinearOperator(prediction_horizon, state_dynamics, control_dynamics, stage_state, control_state,
                                   terminal_state).make_L_op()
    L_z = L @ np.eye(n_z)
    L_adj = core_lin_op.LinearOperator(prediction_horizon, state_dynamics, control_dynamics, stage_state,
                                       control_state, terminal_state).make_L_adj()
    # Choose α1, α2 > 0 such that α1α2∥L∥^2 < 1
    eigs = np.real(sp.sparse.linalg.eigs(L_adj @ L, k=n_z - 2, return_eigenvectors=False))
    L_norm = np.sqrt(max(eigs))
    alpha = 0.99 / L_norm
    return L, L_z, L_adj, alpha


def proj_to_c(vector, prediction_horizon, stage_state, terminal_state, stage_sets, terminal_set):
    """
    :param vector: the vector to be projected to sets (C_t) and C_N
    :param prediction_horizon: prediction horizon (N) of dynamic system
    :param stage_state: matrix (Gamma_x), describing the state constraints
    :param terminal_state: matrix (Gamma_N), describing terminal constraints
    :param stage_sets: nonempty convex closed sets (C) which is the Cartesian product of sets (C_t), describing
    state-control constraints
    :param terminal_set: nonempty convex closed set (C_N), describing terminal constraints
    """
    N = prediction_horizon
    n_c = stage_state.shape[0]
    n_f = terminal_state.shape[0]
    if type(stage_sets).__name__ == 'Cartesian':
        vector_list = [None] * N
        for i in range(N):
            vector_list[i] = vector[i * n_c: (i + 1) * n_c]
        vector_stage = stage_sets.project(vector_list)
    else:
        vector_stage = stage_sets.project(vector[0: N * n_c])
    vector_terminal = terminal_set.project(vector[N * n_c: N * n_c + n_f])
    vector = np.vstack((vector_stage, vector_terminal))
    return vector


class ADMM:
    def __init__(self, epsilon, initial_guess_z, initial_guess_eta,
                 prediction_horizon, initial_state, L, L_z, L_adj, alpha, state_dynamics, control_dynamics,
                 control_weight, P_seq, R_tilde_seq, K_seq, A_bar_seq, stage_state,
                 terminal_state, stage_sets, terminal_set):
        """
        :param epsilon: scalar (epsilon) of Chambolle-Pock algorithm
        :param initial_guess_z: vector initial guess of (z0) of Chambolle-Pock algorithm
        :param initial_guess_eta: vector initial guess of (eta0) of Chambolle-Pock algorithm
        :param alpha: Choose α1, α2 > 0 such that α1α2∥L∥^2 < 1, here α1 = α2 = 0.99/∥L∥
        :param L: LinearOperator of (L) of Chambolle-Pock algorithm
        :param L_z: vector of (L_z) of Chambolle-Pock algorithm
        :param L_adj: LinearOperator adjoint of (L_adj) of Chambolle-Pock algorithm
        :param prediction_horizon: prediction horizon (N) of dynamic system
        :param initial_state: initial state of dynamic system
        :param state_dynamics: matrix (A), describing the state dynamics
        :param control_dynamics: matrix (B), describing control dynamics
        :param control_weight: scalar or matrix (R), input cost matrix or scalar
        :param P_seq: tensor, matrix sequence of (P) from proximal of h offline part
        :param R_tilde_seq: tensor, matrix sequence of (R) from proximal of h offline part
        :param K_seq: tensor, matrix sequence of (K) from proximal of h offline part
        :param A_bar_seq: tensor, matrix sequence of (A_bar) from proximal of h offline part
        :param stage_state: matrix (Gamma_x), describing the state constraints
        :param terminal_state: matrix (Gamma_N), describing terminal constraints
        :param stage_sets: nonempty convex closed sets (C) which is the Cartesian product of sets (C_t), describing
        state-control constraints
        :param terminal_set: nonempty convex closed set (C_N), describing terminal constraints
        """
        self.__N = prediction_horizon
        self.__A = state_dynamics
        self.__B = control_dynamics
        self.__R = control_weight
        self.__x0 = initial_state
        self.__z0 = initial_guess_z
        self.__eta0 = initial_guess_eta
        self.__epsilon = epsilon
        self.__P_seq = P_seq
        self.__R_tilde_seq = R_tilde_seq
        self.__K_seq = K_seq
        self.__A_bar_seq = A_bar_seq
        self.__Gamma_x = stage_state
        self.__Gamma_N = terminal_state
        self.__C_t = stage_sets
        self.__C_N = terminal_set
        self.__L = L
        self.__L_adj = L_adj
        self.__L_z = L_z
        self.__alpha = alpha
        self.__status = None
        self.__scaling_factor = None
        self.__z = None

    @property
    def get_z(self):
        return self.__z

    @property
    def get_status(self):
        return self.__status

    def proj_to_c(self, vector):
        """
        :param vector: the vector to be projected to sets (C_t) and C_N
        """
        n_c = self.__Gamma_x.shape[0]
        n_f = self.__Gamma_N.shape[0]
        if type(self.__C_t).__name__ == 'Cartesian':
            vector_list = [None] * self.__N
            for i in range(self.__N):
                vector_list[i] = vector[i * n_c: (i + 1) * n_c]
            vector_stage = self.__C_t.project(vector_list)
        else:
            vector_stage = self.__C_t.project(vector[0: self.__N * n_c])
        vector_terminal = self.__C_N.project(vector[self.__N * n_c: self.__N * n_c + n_f])
        vector = np.vstack((vector_stage, vector_terminal))
        return vector

    def ADMM_for_ocp(self):
        N = self.__N
        A = self.__A
        B = self.__B
        R = self.__R
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
        L_adj = self.__L_adj
        alpha = self.__alpha
        epsilon = self.__epsilon
        n_x = A.shape[1]
        n_u = B.shape[1]
        n_z = N * (n_x + n_u) + n_x
        n_L = self.__L_z.shape[0]
        x0 = self.__x0.copy()
        z0 = self.__z0.copy()
        eta0 = self.__eta0.copy()

        if z0.shape[0] != n_z:
            raise ValueError("Initial guess vector z row is not correct")
        if eta0.shape[0] != n_L:
            raise ValueError("Initial guess vector eta row is not correct")

        proximal_lambda = alpha
        rho = 1 / proximal_lambda
        z_next = z0
        eta_next = eta0
        u0 = 1 / rho * eta0
        u0 = z0 - L_adj @ eta0
        u_next = u0
        n_max = 10000

        for i in range(n_max):
            z_prev = z_next
            eta_prev = eta_next
            u_prev = u_next
            z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                           proximal_lambda=proximal_lambda,
                                                           initial_state=x0,
                                                           initial_guess_vector=L_adj @ eta_prev - u_prev,
                                                           state_dynamics=A,
                                                           control_dynamics=B,
                                                           control_weight=R,
                                                           P_seq=P_seq,
                                                           R_tilde_seq=R_tilde_seq,
                                                           K_seq=K_seq,
                                                           A_bar_seq=A_bar_seq)
            eta_next = ADMM.proj_to_c(self, z_next + u_prev)
            u_next = u_prev + z_next - L_adj @ eta_next

            s = rho * L_adj @ (eta_next - eta_prev)
            r = z_next - L_adj @ eta_next
            t_1 = np.linalg.norm(s)
            t_2 = np.linalg.norm(r)
            # epsilon_pri = epsilon * max(np.linalg.norm(z_next), np.linalg.norm(L_adj @ eta_next))
            # epsilon_dual = epsilon * np.linalg.norm(eta_next)
            if t_2 <= epsilon and t_1 <= epsilon:
                break
        self.__status = 0  # converge success
        if i >= 9000:
            self.__status = 1  # converge failed
        self.__z = z_next
        return self

    def ADMM_scaling_for_ocp(self, scaling_factor):
        N = self.__N
        A = self.__A
        B = self.__B
        R = self.__R
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
        L_adj = self.__L_adj
        alpha = self.__alpha
        epsilon = self.__epsilon
        n_x = A.shape[1]
        n_u = B.shape[1]
        n_z = N * (n_x + n_u) + n_x
        n_L = self.__L_z.shape[0]

        # scaling
        x0 = self.__x0.copy()
        for i in range(n_x):
            x0[i] = x0[i] / scaling_factor[i]
        z0 = self.__z0.copy() / scaling_factor
        eta0 = self.__eta0.copy() / scaling_factor

        if z0.shape[0] != n_z:
            raise ValueError("Initial guess vector z row is not correct")
        if eta0.shape[0] != n_L:
            raise ValueError("Initial guess vector eta row is not correct")

        proximal_lambda = alpha
        rho = 1 / proximal_lambda
        z_next = z0
        eta_next = eta0
        u0 = 1 / rho * eta0
        u_next = u0
        n_max = 10000

        for i in range(n_max):
            z_prev = z_next
            eta_prev = eta_next
            u_prev = u_next
            z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                           proximal_lambda=proximal_lambda,
                                                           initial_state=x0,
                                                           initial_guess_vector=L_adj @ eta_prev - u_prev,
                                                           state_dynamics=A,
                                                           control_dynamics=B,
                                                           control_weight=R,
                                                           P_seq=P_seq,
                                                           R_tilde_seq=R_tilde_seq,
                                                           K_seq=K_seq,
                                                           A_bar_seq=A_bar_seq)
            eta_next = ADMM.proj_to_c(self, z_next + u_prev)
            u_next = u_prev + z_next - L_adj @ eta_next

            # Termination criteria
            # scaling back
            z_prev_scaling_back = z_prev * scaling_factor
            eta_prev_scaling_back = L_adj @ eta_prev * scaling_factor
            z_next_scaling_back = z_next * scaling_factor
            eta_next_scaling_back = L_adj @ eta_next * scaling_factor

            s = rho * (eta_next_scaling_back - eta_prev_scaling_back)
            r = z_next_scaling_back - eta_next_scaling_back
            t_1 = np.linalg.norm(s)
            t_2 = np.linalg.norm(r)
            # epsilon_pri = epsilon * max(np.linalg.norm(z_next_scaling_back), np.linalg.norm(eta_next_scaling_back))
            # epsilon_dual = epsilon * np.linalg.norm(eta_next_scaling_back)
            if t_1 <= epsilon and t_2 <= epsilon:
                break
        self.__status = 0  # converge success
        if i >= 9000:
            self.__status = 1  # converge failed
        self.__z = z_next_scaling_back
        return self
