#!/usr/bin/env python
from __future__ import division, print_function

import sys

# OpenMM Imports
import openmm as mm
import openmm.app as app

# ParmEd Imports
from parmed import load_file
from parmed.openmm.reporters import NetCDFReporter
from parmed import unit as u

# Load the Gromacs files
print('Loading Gromacs files...')
top = load_file('dhfr_gas.top', xyz='dhfr_gas.gro')

# Create the OpenMM system
print('Creating OpenMM System')
system = top.createSystem(nonbondedMethod=app.NoCutoff,
                          constraints=app.HBonds, implicitSolvent=app.GBn2,
                          implicitSolventSaltConc=0.1*u.moles/u.liter,
)

# Create the integrator to do Langevin dynamics
integrator = mm.LangevinIntegrator(
                        300*u.kelvin,       # Temperature of heat bath
                        1.0/u.picoseconds,  # Friction coefficient
                        2.0*u.femtoseconds, # Time step
)

# Define the platform to use; CUDA, OpenCL, CPU, or Reference. Or do not specify
# the platform to use the default (fastest) platform
platform = mm.Platform.getPlatformByName('CUDA')
prop = dict(CudaPrecision='mixed') # Use mixed single/double precision

# Create the Simulation object
sim = app.Simulation(top.topology, system, integrator, platform, prop)

# Set the particle positions
sim.context.setPositions(top.positions)

# Minimize the energy
print('Minimizing energy')
sim.minimizeEnergy(maxIterations=500)

# Set up the reporters to report energies and coordinates every 100 steps
sim.reporters.append(
        app.StateDataReporter(sys.stdout, 100, step=True, potentialEnergy=True,
                              kineticEnergy=True, temperature=True)
)
sim.reporters.append(
        NetCDFReporter('dhfr_gb.nc', 100, crds=True)
)

# Run dynamics
print('Running dynamics')
sim.step(10000)
