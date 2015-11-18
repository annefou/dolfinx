#!/usr/bin/env py.test

"Unit tests for nullspace test"

# Copyright (C) 2014 Garth N. Wells
#
# This file is part of DOLFIN.
#
# DOLFIN is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DOLFIN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DOLFIN. If not, see <http://www.gnu.org/licenses/>.

from dolfin import *
import pytest
from dolfin_utils.test import *

backends = ["PETSc", skip_in_parallel("Eigen")]

def build_elastic_nullspace(V, x):
    """Function to build nullspace for 2D elasticity"""

    # Create list of vectors for null space
    nullspace_basis = [x.copy() for i in range(3)]

    # Build translational null space basis
    V.sub(0).dofmap().set(nullspace_basis[0], 1.0);
    V.sub(1).dofmap().set(nullspace_basis[1], 1.0);

    # Build rotational null space basis
    V.sub(0).set_x(nullspace_basis[2], -1.0, 1);
    V.sub(1).set_x(nullspace_basis[2], 1.0, 0);
    for x in nullspace_basis:
        x.apply("insert")
    return VectorSpaceBasis(nullspace_basis)


def build_broken_elastic_nullspace(V, x):
    """Function to build incorrect null space for 2D elasticity"""

    # Create list of vectors for null space
    nullspace_basis = [x.copy() for i in range(4)]

    # Build translational null space basis
    V.sub(0).dofmap().set(nullspace_basis[0], 1.0);
    V.sub(1).dofmap().set(nullspace_basis[1], 1.0);

    # Build rotational null space basis
    V.sub(0).set_x(nullspace_basis[2], -1.0, 1);
    V.sub(1).set_x(nullspace_basis[2], 1.0, 0);

    # Add vector that is not in nullspace
    V.sub(1).set_x(nullspace_basis[3], 1.0, 1);

    for x in nullspace_basis:
        x.apply("insert")
    return VectorSpaceBasis(nullspace_basis)


@pytest.mark.parametrize('backend', backends)
def test_nullspace_check(backend):
    # Check whether backend is available
    if not has_linear_algebra_backend(backend):
        pytest.skip('Need %s as backend to run this test' % backend)

    # Set linear algebra backend
    prev_backend = parameters["linear_algebra_backend"]
    parameters["linear_algebra_backend"] = backend

    # Mesh
    mesh = UnitSquareMesh(12, 12)

    # Elasticity form
    V = VectorFunctionSpace(mesh, 'CG', 1)
    u, v = TrialFunction(V), TestFunction(V)
    a = inner(sym(grad(u)), grad(v))*dx

    # Assemble matrix and create compatible vector
    A = assemble(a)
    x = Vector()
    A.init_vector(x, 1)

    # Create null space basis and test
    null_space = build_elastic_nullspace(V, x)
    assert in_nullspace(A, null_space)
    assert in_nullspace(A, null_space, "right")
    assert in_nullspace(A, null_space, "left")

    # Create incorect null space basis and test
    null_space = build_broken_elastic_nullspace(V, x)
    assert not in_nullspace(A, null_space)
    assert not in_nullspace(A, null_space, "right")
    assert not in_nullspace(A, null_space, "left")

    # Reset backend
    parameters["linear_algebra_backend"] = prev_backend
