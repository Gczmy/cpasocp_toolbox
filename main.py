import cpasocp as cpa
import numpy as np
import matplotlib.pyplot as plt
import cpasocp.core.sets as core_sets
import time

# CPASOCP generation
# -----------------------------------------------------------------------------------------------------

# dynamics
# prediction_horizon = np.random.randint(15, 20)
prediction_horizon = 10
# n_x = np.random.randint(10, 20)  # state dimension
# n_u = np.random.randint(9, n_x)  # input dimension
n_x = 20
n_u = 10
# A = np.array([[1, 0.7], [-0.1, 1]])  # n x n matrices
A = 2 * np.random.rand(n_x, n_x)  # n x n matrices
# B = np.array([[1, 1], [0.5, 1]])  # n x u matrices
B = np.random.rand(n_x, n_u)  # n x u matrices

# costs
cost_type = "Quadratic"
Q = 10 * np.eye(n_x)  # n x n matrix
R = np.eye(n_u)  # u x u matrix OR scalar
P = 5 * np.eye(n_x)  # n x n matrix

# constraints
constraints_type = 'Rectangle'
rect_min = [-5] * (n_x + n_u)  # constraints for x^0, ..., x^n, u^0, ..., u^n
rect_max = [5] * (n_x + n_u)  # constraints for x^0, ..., x^n, u^0, ..., u^n
# for i in range(n_x + n_u):
#     rect_min[i] = -np.random.rand()
#     rect_max[i] = np.random.rand()
#     if (i % 2) == 0:
#         rect_min[i] = rect_min[i] * -100000 - 100000
#         rect_max[i] = rect_max[i] * 100000 + 100000
#     else:
#         rect_min[i] = rect_min[i] * -1000 - 1000
#         rect_max[i] = rect_max[i] * 1000 + 1000
rectangle = core_sets.Rectangle(rect_min=rect_min, rect_max=rect_max)
stage_sets_list = [rectangle] * prediction_horizon
stage_sets = core_sets.Cartesian(stage_sets_list)
terminal_set = core_sets.Rectangle(rect_min=rect_min, rect_max=rect_max)
# x0 = np.array([0.2, 0.5])
x0 = 0.5 * np.random.rand(n_x)
# for i in range(n_x):
#     x0[i] = np.random.rand() - 0.5
#     if (i % 2) == 0:
#         x0[i] *= 1000
#     else:
#         x0[i] *= 100

# algorithm parameters
epsilon = 1e-3
n_z = (prediction_horizon + 1) * A.shape[1] + prediction_horizon * B.shape[1]
z0 = 0.5 * np.random.rand(n_z, 1)
eta0 = 0.5 * np.random.rand(n_z, 1)
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
start_CP = time.time()
solution = cpa.core.CPASOCP(prediction_horizon) \
    .with_dynamics(A, B) \
    .with_cost(cost_type, Q, R, P) \
    .with_constraints(constraints_type, stage_sets, terminal_set) \
    .chambolle_pock(epsilon, x0, z0, eta0)
CP_time = time.time() - start_CP
print(solution)
print(CP_time)
plt.title('semilogy')
plt.xlabel('Iterations')
plt.ylabel('Residuals')
plt.semilogy(solution.get_residuals_cache, label=['Primal Residual', 'Dual Residual', 'Duality Gap'])
plt.legend()
plt.show()



