import time
import cpasocp as cpa
import numpy as np
import cvxpy as cp
import cpasocp.core.sets as core_sets

f = open("Chambolle-Pock.txt", "w")
print("---\nalgname: Chambolle-Pock\nsuccess: converged\nfree_format: True\n---", file=f)
f.close()
f = open("Preconditioning.txt", "w")
print("---\nalgname: Preconditioning\nsuccess: converged\nfree_format: True\n---", file=f)
f.close()

solved_num = 0
while solved_num < 100:
    # dynamics
    prediction_horizon = 20

    n_x = 10  # state dimension
    n_u = 10  # input dimension

    # A = np.array([[1, 0.7], [-0.1, 1]])  # n x n matrices
    A = 0.1 * np.random.rand(n_x, n_x)  # n x n matrices
    # B = np.array([[1, 1], [0.5, 1]])  # n x u matrices
    B = 0.05 * np.random.rand(n_x, n_u)  # n x u matrices

    # costs
    cost_type = "Quadratic"
    Q = 100 * np.eye(n_x)  # n x n matrix
    # Q[n_x-1, n_x-1] = 0.1
    R = np.eye(n_u)  # u x u matrix OR scalar
    P = 5 * np.eye(n_x)  # n x n matrix

    # constraints
    constraints_type = 'Rectangle'
    rect_min = [-1] * (n_x + n_u)  # constraints for x^0, ..., x^n, u^0, ..., u^n
    rect_max = [1] * (n_x + n_u)  # constraints for x^0, ..., x^n, u^0, ..., u^n
    for i in range(n_x + n_u):
        # rect_min[i] = np.random.rand()
        # rect_max[i] = np.random.rand()
        if (i % 2) == 0:
            rect_min[i] = rect_min[i] * 5
            rect_max[i] = rect_max[i] * 5
        else:
            rect_min[i] = rect_min[i] * 2
            rect_max[i] = rect_max[i] * 2
    rectangle = core_sets.Rectangle(rect_min=rect_min, rect_max=rect_max)
    stage_sets_list = [rectangle] * prediction_horizon
    stage_sets = core_sets.Cartesian(stage_sets_list)
    terminal_set = core_sets.Rectangle(rect_min=rect_min, rect_max=rect_max)
    # initial_state = np.array([0.2, 0.5])
    initial_state = np.ones(n_x)
    for i in range(n_x):
        if (i % 2) == 0:
            initial_state[i] = initial_state[i] * 5
        else:
            initial_state[i] = initial_state[i] * 2

    n_z = (prediction_horizon + 1) * A.shape[1] + prediction_horizon * B.shape[1]
    z0 = np.random.rand(n_z, 1)
    eta0 = np.random.rand(n_z, 1)
    # z0 = 0.5 * np.random.rand(n_z, 1) + 0.1
    # eta0 = 0.5 * np.random.rand(n_z, 1) + 0.1
    # for j in range(prediction_horizon):
    #     for i in range(n_x + n_u):
    #         z0[j * (n_x + n_u) + i] = np.random.random()
    #         eta0[j * (n_x + n_u) + i] = np.random.random()
    #         if ((j * (n_x + n_u) + i) % 2) == 0:
    #             z0[j * (n_x + n_u) + i] *= 1000
    #             eta0[j * (n_x + n_u) + i] *= 1000
    #         else:
    #             z0[j * (n_x + n_u) + i] *= 100
    #             eta0[j * (n_x + n_u) + i] *= 100

    # algorithm parameters
    epsilon = 1e-4
    # solving OCP by cvxpy
    # -----------------------------
    N = prediction_horizon
    n_x = A.shape[1]
    n_u = B.shape[1]
    c_t_x_min = np.zeros(n_x)
    c_t_x_max = np.zeros(n_x)
    c_t_u_min = np.zeros(n_u)
    c_t_u_max = np.zeros(n_u)
    c_N_min = np.zeros(n_x)
    c_N_max = np.zeros(n_x)
    for i in range(n_x):
        c_t_x_min[i] = rect_min[i]
        c_t_x_max[i] = rect_max[i]
        c_N_min[i] = rect_min[i]
        c_N_max[i] = rect_max[i]
    for i in range(n_u):
        c_t_u_min[i] = rect_min[i + n_x]
        c_t_u_max[i] = rect_max[i + n_x]

    # Problem statement
    x0_cp = cp.Parameter(n_x)  # <--- x is a parameter of the optimisation problem P_N(x)
    u_seq = cp.Variable((n_u, N))  # <--- sequence of control actions
    x_seq = cp.Variable((n_x, N + 1))

    cost = 0
    constraints = [x_seq[:, 0] == x0_cp]  # Initial Condition x_0 = x

    for t in range(N):
        xt_var = x_seq[:, t]  # x_t
        ut_var = u_seq[:, t]  # u_t
        cost += 0.5 * (cp.quad_form(xt_var, Q) + cp.quad_form(ut_var, R))  # Stage cost
        constraints += [x_seq[:, t + 1] == A @ xt_var + B @ ut_var,  # Dynamics
                        c_t_x_min <= xt_var,
                        xt_var <= c_t_x_max,
                        c_t_u_min <= ut_var,
                        ut_var <= c_t_u_max]  # Input Constraints

    xN = x_seq[:, N]
    cost += 0.5 * cp.quad_form(xN, P)  # Terminal cost
    constraints += [c_N_min <= xN, xN <= c_N_max]

    # Solution
    x0_cp.value = initial_state
    problem = cp.Problem(cp.Minimize(cost), constraints)
    problem.solve()
    print(problem.status)
    if problem.status == 'optimal':
        solved_num += 1
        # Chambolle-Pock method
        # ------------------------------------------------------------------------------------------------------------------
        # start time for chambolle-pock method
        start_CP = time.time()

        solution = cpa.core.CPASOCP(prediction_horizon) \
            .with_dynamics(A, B) \
            .with_cost(cost_type, Q, R, P) \
            .with_constraints(constraints_type, stage_sets, terminal_set) \
            .chambolle_pock(epsilon, initial_state, z0, eta0)

        CP_time = time.time() - start_CP

        z_CP = solution.z

        if solution.status == 0:
            f = open("Chambolle-Pock.txt", "a")
            print(f"problem{solved_num} converged {CP_time}", file=f)
            f.close()
        else:
            f = open("Chambolle-Pock.txt", "a")
            print(f"problem{solved_num} failed {CP_time}", file=f)
            f.close()

        # CP_scaling
        # ------------------------------------------------------------------------------------------------------------------
        start_CP_scaling = time.time()
        solution_CP_scaling = cpa.core.CPASOCP(prediction_horizon) \
            .with_dynamics(A, B) \
            .with_cost(cost_type, Q, R, P) \
            .with_constraints_scaling(constraints_type, stage_sets, terminal_set) \
            .cp_scaling(epsilon, initial_state, z0, eta0)

        CP_scaling_time = time.time() - start_CP_scaling

        z_CP_scaling = solution_CP_scaling.z

        if solution_CP_scaling.status == 0:
            f = open("Preconditioning.txt", "a")
            print(f"problem{solved_num} converged {CP_scaling_time}", file=f)
            f.close()
        else:
            f = open("Preconditioning.txt", "a")
            print(f"problem{solved_num} failed {CP_scaling_time}", file=f)
            f.close()

        print('problem_loop:', solved_num)
