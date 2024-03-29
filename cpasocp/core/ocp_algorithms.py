import numpy as np
import cpasocp.core.proximal_online_part as core_online
from math import sqrt as sqrt


class Algorithms:
    """
    Algorithms for OCP
    """

    def __init__(self):
        self.__N = None  # prediction_horizon
        self.__A = None  # state_dynamics
        self.__B = None  # control_dynamics
        self.__R = None  # control_weight
        self.__x0 = None  # initial_state
        self.__z0 = None  # initial_guess_z
        self.__eta0 = None  # initial_guess_eta
        self.__epsilon = None
        self.__P_seq = None
        self.__R_tilde_seq = None
        self.__K_seq = None
        self.__A_bar_seq = None
        self.__Gamma_x = None  # stage_state
        self.__Gamma_u = None  # stage_input
        self.__Gamma_N = None  # terminal_state
        self.__C_t = None  # stage_sets
        self.__C_N = None  # terminal_set
        self.__L = None
        self.__L_adj = None
        self.__L_z = None
        self.__residuals_cache = None
        self.__alpha = None
        self.__status = None
        self.__scaling_factor = None
        self.__loop_time = None
        self.__z = None
        self.__s_cache = None
        self.__y_cache = None
        self.__r_safe = None
        self.__supermann_eta = None

    @property
    def prediction_horizon(self):
        """
        :return: prediction_horizon: prediction horizon (N) of dynamic system
        """
        return self.__N

    @prediction_horizon.setter
    def prediction_horizon(self, value):
        self.__N = value

    @property
    def state_dynamics(self):
        """
        :return: state_dynamics: matrix (A), describing the state dynamics
        """
        return self.__A

    @state_dynamics.setter
    def state_dynamics(self, value):
        self.__A = value

    @property
    def control_dynamics(self):
        """
        :return: control_dynamics: matrix (B), describing control dynamics
        """
        return self.__B

    @control_dynamics.setter
    def control_dynamics(self, value):
        self.__B = value

    @property
    def control_weight(self):
        """
        :return: control_weight: scalar or matrix (R), input cost matrix or scalar
        """
        return self.__R

    @control_weight.setter
    def control_weight(self, value):
        self.__R = value

    @property
    def initial_state(self):
        """
        :return: initial_state: initial state of dynamic system
        """
        return self.__x0

    @initial_state.setter
    def initial_state(self, value):
        self.__x0 = value

    @property
    def initial_guess_z(self):
        """
        :return: initial_guess_z: vector initial guess of (z0) of Chambolle-Pock algorithm
        """
        return self.__z0

    @initial_guess_z.setter
    def initial_guess_z(self, value):
        self.__z0 = value

    @property
    def initial_guess_eta(self):
        """
        :return: initial_guess_eta: vector initial guess of (eta0) of Chambolle-Pock algorithm
        """
        return self.__eta0

    @initial_guess_eta.setter
    def initial_guess_eta(self, value):
        self.__eta0 = value

    @property
    def epsilon(self):
        """
        :return: epsilon: scalar (epsilon) of Chambolle-Pock algorithm
        """
        return self.__epsilon

    @epsilon.setter
    def epsilon(self, value):
        self.__epsilon = value

    @property
    def P_seq(self):
        """
        :return: P_seq: tensor, matrix sequence of (P) from proximal of h offline part
        """
        return self.__P_seq

    @P_seq.setter
    def P_seq(self, value):
        self.__P_seq = value

    @property
    def R_tilde_seq(self):
        """
        :return: R_tilde_seq: tensor, matrix sequence of (R) from proximal of h offline part
        """
        return self.__R_tilde_seq

    @R_tilde_seq.setter
    def R_tilde_seq(self, value):
        self.__R_tilde_seq = value

    @property
    def K_seq(self):
        """
        :return: K_seq: tensor, matrix sequence of (K) from proximal of h offline part
        """
        return self.__K_seq

    @K_seq.setter
    def K_seq(self, value):
        self.__K_seq = value

    @property
    def A_bar_seq(self):
        """
        :return: A_bar_seq: tensor, matrix sequence of (A_bar) from proximal of h offline part
        """
        return self.__A_bar_seq

    @A_bar_seq.setter
    def A_bar_seq(self, value):
        self.__A_bar_seq = value

    @property
    def stage_constraints_state(self):
        """
        :return: stage_constraints_state: matrix (Gamma_x), describing the state constraints
        """
        return self.__Gamma_x

    @stage_constraints_state.setter
    def stage_constraints_state(self, value):
        self.__Gamma_x = value

    @property
    def stage_constraints_input(self):
        """
        :return: stage_constraints_input: matrix (Gamma_u), describing the input constraints
        """
        return self.__Gamma_u

    @stage_constraints_input.setter
    def stage_constraints_input(self, value):
        self.__Gamma_u = value

    @property
    def terminal_constraints_state(self):
        """
        :return: terminal_constraints_state: matrix (Gamma_N), describing terminal constraints
        """
        return self.__Gamma_N

    @terminal_constraints_state.setter
    def terminal_constraints_state(self, value):
        self.__Gamma_N = value

    @property
    def stage_constraints_sets(self):
        """
        :return: stage_constraints_sets: nonempty convex closed sets (C) which is the Cartesian product of sets (C_t),
        describing state-control constraints
        """
        return self.__C_t

    @stage_constraints_sets.setter
    def stage_constraints_sets(self, value):
        self.__C_t = value

    @property
    def terminal_constraints_set(self):
        """
        :return: terminal_constraints_set: nonempty convex closed set (C_N), describing terminal constraints
        """
        return self.__C_N

    @terminal_constraints_set.setter
    def terminal_constraints_set(self, value):
        self.__C_N = value

    @property
    def L(self):
        """
        :return: L: LinearOperator of (L) of Chambolle-Pock algorithm
        """
        return self.__L

    @L.setter
    def L(self, value):
        self.__L = value

    @property
    def L_adj(self):
        """
        :return: L_adj: LinearOperator adjoint of (L_adj) of Chambolle-Pock algorithm
        """
        return self.__L_adj

    @L_adj.setter
    def L_adj(self, value):
        self.__L_adj = value

    @property
    def L_z(self):
        """
        :return: L_z: vector of (L_z) of Chambolle-Pock algorithm
        """
        return self.__L_z

    @L_z.setter
    def L_z(self, value):
        self.__L_z = value

    @property
    def alpha(self):
        """
        :return: alpha: Choose α1, α2 > 0 such that α1α2∥L∥^2 < 1, here α1 = α2 = 0.99/∥L∥
        """
        return self.__alpha

    @alpha.setter
    def alpha(self, value):
        self.__alpha = value

    @property
    def z(self):
        return self.__z

    @property
    def residuals_cache(self):
        return self.__residuals_cache

    @property
    def status(self):
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

    def anderson_acceleration(self, memory_num, x_k, T_x_k):
        N = self.__N
        x0 = self.__x0
        A = self.__A
        B = self.__B
        R = self.__R
        m = memory_num
        i = self.__loop_time
        n_x = A.shape[1]
        n_u = B.shape[1]
        n_z = N * (n_x + n_u) + n_x
        alpha = self.__alpha
        L = self.__L
        L_adj = self.__L_adj
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
        m_i = min(m, i)
        oldest_flag = i % m
        T_x_k_z_prev = T_x_k[0: n_z]
        T_x_k_eta_prev = T_x_k[n_z: 2 * n_z]
        T_x_k_z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                             proximal_lambda=alpha,
                                                             initial_state=x0,
                                                             initial_guess_vector=T_x_k_z_prev
                                                                                  - alpha * L_adj @ T_x_k_eta_prev,
                                                             state_dynamics=A,
                                                             control_dynamics=B,
                                                             control_weight=R,
                                                             P_seq=P_seq,
                                                             R_tilde_seq=R_tilde_seq,
                                                             K_seq=K_seq,
                                                             A_bar_seq=A_bar_seq)
        T_x_k_eta_half_next = T_x_k_eta_prev + alpha * L @ (2 * T_x_k_z_next - T_x_k_z_prev)
        T_x_k_eta_next = T_x_k_eta_half_next - alpha * Algorithms.proj_to_c(self, T_x_k_eta_half_next / alpha)
        TT_x_k = np.vstack((T_x_k_z_next, T_x_k_eta_next))
        self.__s_cache[oldest_flag] = x_k - T_x_k
        self.__y_cache[oldest_flag] = (x_k - T_x_k) - (T_x_k - TT_x_k)
        r_k = x_k - T_x_k
        S_k = self.__s_cache[0]
        Y_k = self.__y_cache[0]
        for k in range(1, m_i + 1):
            if k < m:
                S_k = np.hstack((S_k, self.__s_cache[k]))
                Y_k = np.hstack((Y_k, self.__y_cache[k]))
        t_k = np.linalg.lstsq(Y_k, r_k, rcond=None)[0]
        d_k = -r_k - (S_k - Y_k) @ t_k
        return d_k

    def sgn(self, x):
        if x >= 0:
            return 1
        else:
            return 0

    def modified_restarted_broyden(self, memory_num, x_k, T_x_k):
        N = self.__N
        x0 = self.__x0
        A = self.__A
        B = self.__B
        R = self.__R
        m = memory_num
        i = self.__loop_time
        n_x = A.shape[1]
        n_u = B.shape[1]
        n_z = N * (n_x + n_u) + n_x
        alpha = self.__alpha
        L = self.__L
        L_adj = self.__L_adj
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
        oldest_flag = i % m

        theta_bar = 0.2
        d = - (x_k - T_x_k)
        w_k = x_k + d
        w_k_z_prev = w_k[0: n_z]
        w_k_eta_prev = w_k[n_z: 2 * n_z]
        w_k_z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                           proximal_lambda=alpha,
                                                           initial_state=x0,
                                                           initial_guess_vector=w_k_z_prev
                                                                                - alpha * L_adj @ w_k_eta_prev,
                                                           state_dynamics=A,
                                                           control_dynamics=B,
                                                           control_weight=R,
                                                           P_seq=P_seq,
                                                           R_tilde_seq=R_tilde_seq,
                                                           K_seq=K_seq,
                                                           A_bar_seq=A_bar_seq)
        w_k_eta_half_next = w_k_eta_prev + alpha * L @ (2 * w_k_z_next - w_k_z_prev)
        w_k_eta_next = w_k_eta_half_next - alpha * Algorithms.proj_to_c(self, w_k_eta_half_next / alpha)
        T_w_k = np.vstack((w_k_z_next, w_k_eta_next))

        s = w_k - x_k
        tilde_s = w_k - T_w_k - (x_k - T_x_k)
        if oldest_flag == 0:
            self.__s_cache = [s]
            self.__y_cache = [tilde_s]
            tilde_s = tilde_s + np.inner(self.__s_cache[0].T, tilde_s.T) * tilde_s
            d = d + np.inner(self.__s_cache[0].T, d.T) * tilde_s
        else:
            self.__s_cache.append(s)
            self.__y_cache.append(tilde_s)
            num_s = len(self.__s_cache)
            for k in range(num_s):
                tilde_s = tilde_s + np.inner(self.__s_cache[num_s - k - 1].T, tilde_s.T) * self.__y_cache[num_s - k - 1]
                d = d + np.inner(self.__s_cache[num_s - k - 1].T, d.T) * self.__y_cache[num_s - k - 1]
        gamma = np.inner(tilde_s.T, s.T) / (np.linalg.norm(s) ** 2)
        if abs(gamma) >= theta_bar:
            theta = 1
        else:
            theta = (1 - Algorithms.sgn(self, gamma) * theta_bar) / (1 - gamma)
        tilde_s = theta / (1 - theta + theta * gamma) / (np.linalg.norm(s) ** 2) * (s - tilde_s)
        d = d + np.inner(s.T, d.T) * tilde_s
        return d

    def SuperMann(self, z_prev, eta_prev, z_next, eta_next, op_A, memory_num, c0, c1, q, beta, sigma, lambda_,
                  direction):
        N = self.__N
        x0 = self.__x0
        A = self.__A
        B = self.__B
        R = self.__R
        m = memory_num
        i = self.__loop_time
        n_x = A.shape[1]
        n_u = B.shape[1]
        n_z = N * (n_x + n_u) + n_x
        alpha = self.__alpha
        L = self.__L
        L_adj = self.__L_adj
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
        n_max = 10000
        x_k = np.vstack((z_prev, eta_prev))
        T_x_k = np.vstack((z_next, eta_next))
        if i == 0:
            self.__r_safe = sqrt((x_k - T_x_k).T @ op_A @ (x_k - T_x_k))
            self.__supermann_eta = self.__r_safe
        if sqrt((x_k - T_x_k).T @ op_A @ (x_k - T_x_k)) <= self.__epsilon:
            return x_k

        # Choose an update direction
        if direction is None:
            direction = 'anderson'
        if direction == 'anderson':
            # print('choose update direction using anderson acceleration')
            d_k = Algorithms.anderson_acceleration(self, m, x_k, T_x_k)
        elif direction == 'broyden':
            # print('choose update direction using broyden method')
            d_k = Algorithms.modified_restarted_broyden(self, m, x_k, T_x_k)

        # K0
        if sqrt((x_k - T_x_k).T @ op_A @ (x_k - T_x_k)) <= c0 * self.__supermann_eta:
            self.__supermann_eta = sqrt((x_k - T_x_k).T @ op_A @ (x_k - T_x_k))
            w_k = x_k + d_k
            x_k = w_k
            return x_k
        tau_k = 1
        for k in range(n_max):
            w_k = x_k + tau_k * d_k
            w_z_prev = w_k[0:n_z]
            w_eta_prev = w_k[n_z:2 * n_z]
            w_z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                             proximal_lambda=alpha,
                                                             initial_state=x0,
                                                             initial_guess_vector=w_z_prev - alpha * L_adj @ w_eta_prev,
                                                             state_dynamics=A,
                                                             control_dynamics=B,
                                                             control_weight=R,
                                                             P_seq=P_seq,
                                                             R_tilde_seq=R_tilde_seq,
                                                             K_seq=K_seq,
                                                             A_bar_seq=A_bar_seq)
            w_eta_half_next = w_eta_prev + alpha * L @ (2 * w_z_next - w_z_prev)
            w_eta_next = w_eta_half_next - alpha * Algorithms.proj_to_c(self, w_eta_half_next / alpha)
            T_w_k = np.vstack((w_z_next, w_eta_next))
            # K1
            if sqrt((x_k - T_x_k).T @ op_A @ (x_k - T_x_k)) <= self.__r_safe \
                    and sqrt((w_k - T_w_k).T @ op_A @ (w_k - T_w_k)) <= c1 * sqrt(
                (x_k - T_x_k).T @ op_A @ (x_k - T_x_k)):
                x_k = w_k
                self.__r_safe = sqrt((w_k - T_w_k).T @ op_A @ (w_k - T_w_k)) + q ** i
                break
            # K2
            rho_k = sqrt((w_k - T_w_k).T @ op_A @ (w_k - T_w_k)) ** 2 - (w_k - T_w_k).T @ op_A @ (w_k - x_k)
            if rho_k[0, 0] >= sigma * sqrt((w_k - T_w_k).T @ op_A @ (w_k - T_w_k)) \
                    * sqrt((x_k - T_x_k).T @ op_A @ (x_k - T_x_k)):
                x_k = x_k - lambda_ * rho_k[0, 0] / (sqrt((w_k - T_w_k).T @ op_A @ (w_k - T_w_k)) ** 2) * (
                        w_k - T_w_k)
                break
            else:
                tau_k = beta * tau_k
        return x_k

    def chambolle_pock(self):
        N = self.__N
        A = self.__A
        B = self.__B
        R = self.__R
        L = self.__L
        L_adj = self.__L_adj
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
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

        z_next = z0
        eta_next = eta0
        n_max = 10000
        self.__residuals_cache = np.zeros((n_max, 3))

        for i in range(n_max):
            self.__loop_time = i
            z_prev = z_next
            eta_prev = eta_next
            z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                           proximal_lambda=alpha,
                                                           initial_state=x0,
                                                           initial_guess_vector=z_prev - alpha * L_adj @ eta_prev,
                                                           state_dynamics=A,
                                                           control_dynamics=B,
                                                           control_weight=R,
                                                           P_seq=P_seq,
                                                           R_tilde_seq=R_tilde_seq,
                                                           K_seq=K_seq,
                                                           A_bar_seq=A_bar_seq)
            eta_half_next = eta_prev + alpha * L @ (2 * z_next - z_prev)
            eta_next = eta_half_next - alpha * Algorithms.proj_to_c(self, eta_half_next / alpha)

            # Termination criteria
            xi_1 = (z_prev - z_next) / alpha - L_adj @ (eta_prev - eta_next)
            xi_2 = (eta_prev - eta_next) / alpha + L @ (z_next - z_prev)
            xi_gap = xi_1 + L_adj @ xi_2
            t_1 = np.linalg.norm(xi_1, np.inf)
            t_2 = np.linalg.norm(xi_2, np.inf)
            t_3 = np.linalg.norm(xi_gap, np.inf)
            self.__residuals_cache[i, 0] = t_1
            self.__residuals_cache[i, 1] = t_2
            self.__residuals_cache[i, 2] = t_3

            if t_1 <= epsilon and t_2 <= epsilon and t_3 <= epsilon:
                break
        self.__status = 0  # converge success
        if self.__loop_time >= 9000:
            self.__status = 1  # converge failed
        self.__residuals_cache = self.__residuals_cache[0:self.__loop_time, :]
        self.__z = z_next
        return self

    def chambolle_pock_scaling(self, scaling_factor):
        N = self.__N
        A = self.__A
        B = self.__B
        R = self.__R
        L = self.__L
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

        z_next = z0
        eta_next = eta0
        n_max = 10000
        self.__residuals_cache = np.zeros((n_max, 3))

        for i in range(n_max):
            z_prev = z_next
            eta_prev = eta_next
            z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                           proximal_lambda=alpha,
                                                           initial_state=x0,
                                                           initial_guess_vector=z_prev - alpha * L_adj @ eta_prev,
                                                           state_dynamics=A,
                                                           control_dynamics=B,
                                                           control_weight=R,
                                                           P_seq=P_seq,
                                                           R_tilde_seq=R_tilde_seq,
                                                           K_seq=K_seq,
                                                           A_bar_seq=A_bar_seq)
            eta_half_next = eta_prev + alpha * L @ (2 * z_next - z_prev)
            eta_next = eta_half_next - alpha * Algorithms.proj_to_c(self, eta_half_next / alpha)

            # Termination criteria
            # scaling back
            z_prev_scaling_back = z_prev * scaling_factor
            eta_prev_scaling_back = eta_prev * scaling_factor
            z_next_scaling_back = z_next * scaling_factor
            eta_next_scaling_back = eta_next * scaling_factor

            xi_1 = (z_prev_scaling_back - z_next_scaling_back) / alpha \
                   - L_adj @ (eta_prev_scaling_back - eta_next_scaling_back)
            xi_2 = (eta_prev_scaling_back - eta_next_scaling_back) / alpha \
                   + L @ (z_next_scaling_back - z_prev_scaling_back)
            xi_gap = xi_1 + L_adj @ xi_2
            t_1 = np.linalg.norm(xi_1, np.inf)
            t_2 = np.linalg.norm(xi_2, np.inf)
            t_3 = np.linalg.norm(xi_gap, np.inf)
            self.__residuals_cache[i, 0] = t_1
            self.__residuals_cache[i, 1] = t_2
            self.__residuals_cache[i, 2] = t_3
            if t_1 <= epsilon and t_2 <= epsilon and t_3 <= epsilon:
                break
        self.__status = 0  # converge success
        if i >= 9000:
            self.__status = 1  # converge failed
        self.__residuals_cache = self.__residuals_cache[0:i, :]
        self.__z = z_next_scaling_back
        return self

    def chambolle_pock_supermann(self, memory_num, c0, c1, q, beta, sigma, lambda_, direction):
        N = self.__N
        A = self.__A
        B = self.__B
        R = self.__R
        L = self.__L
        L_adj = self.__L_adj
        P_seq = self.__P_seq
        R_tilde_seq = self.__R_tilde_seq
        K_seq = self.__K_seq
        A_bar_seq = self.__A_bar_seq
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

        z_next = z0
        eta_next = eta0
        n_max = 10000
        self.__residuals_cache = np.zeros((n_max, 3))

        # SuperMann parameter
        m = memory_num
        self.__s_cache = [None] * m
        self.__y_cache = [None] * m

        op_A = np.hstack((np.eye(n_z), -alpha * L_adj @ np.identity(n_z)))
        op_A = np.vstack((op_A, np.hstack((-alpha * L @ np.identity(n_z), np.eye(n_z)))))

        for i in range(n_max):
            self.__loop_time = i
            z_prev = z_next
            eta_prev = eta_next
            z_next = core_online.proximal_of_h_online_part(prediction_horizon=N,
                                                           proximal_lambda=alpha,
                                                           initial_state=x0,
                                                           initial_guess_vector=z_prev - alpha * L_adj @ eta_prev,
                                                           state_dynamics=A,
                                                           control_dynamics=B,
                                                           control_weight=R,
                                                           P_seq=P_seq,
                                                           R_tilde_seq=R_tilde_seq,
                                                           K_seq=K_seq,
                                                           A_bar_seq=A_bar_seq)
            eta_half_next = eta_prev + alpha * L @ (2 * z_next - z_prev)
            eta_next = eta_half_next - alpha * Algorithms.proj_to_c(self, eta_half_next / alpha)

            # use SuperMann
            x_k = Algorithms.SuperMann(
                self, z_prev, eta_prev, z_next, eta_next, op_A, m, c0, c1, q, beta, sigma, lambda_, direction)
            # update z, eta to CP
            z_next = x_k[0:n_z]
            eta_next = x_k[n_z:2 * n_z]

            # Termination criteria
            xi_1 = (z_prev - z_next) / alpha - L_adj @ (eta_prev - eta_next)
            xi_2 = (eta_prev - eta_next) / alpha + L @ (z_next - z_prev)
            xi_gap = xi_1 + L_adj @ xi_2
            t_1 = np.linalg.norm(xi_1, np.inf)
            t_2 = np.linalg.norm(xi_2, np.inf)
            t_3 = np.linalg.norm(xi_gap, np.inf)
            self.__residuals_cache[i, 0] = t_1
            self.__residuals_cache[i, 1] = t_2
            self.__residuals_cache[i, 2] = t_3
            if t_1 <= epsilon and t_2 <= epsilon and t_3 <= epsilon:
                break
        self.__status = 0  # converge success
        if self.__loop_time >= 9000:
            self.__status = 1  # converge failed
        self.__residuals_cache = self.__residuals_cache[0:self.__loop_time, :]
        self.__z = z_next
        return self

    def admm(self):
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

        self.__residuals_cache = np.zeros((n_max, 2))
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
            eta_next = Algorithms.proj_to_c(self, z_next + u_prev)
            u_next = u_prev + z_next - L_adj @ eta_next

            s = rho * L_adj @ (eta_next - eta_prev)
            r = z_next - L_adj @ eta_next
            t_1 = np.linalg.norm(s)
            t_2 = np.linalg.norm(r)
            self.__residuals_cache[i, 0] = t_1
            self.__residuals_cache[i, 1] = t_2
            # epsilon_pri = epsilon * max(np.linalg.norm(z_next), np.linalg.norm(L_adj @ eta_next))
            # epsilon_dual = epsilon * np.linalg.norm(eta_next)
            if t_2 <= epsilon and t_1 <= epsilon:
                break
        self.__status = 0  # converge success
        if i >= 9000:
            self.__status = 1  # converge failed
        self.__z = z_next
        self.__residuals_cache = self.__residuals_cache[0:i, :]
        return self

    def admm_scaling(self, scaling_factor):
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
            eta_next = Algorithms.proj_to_c(self, z_next + u_prev)
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

