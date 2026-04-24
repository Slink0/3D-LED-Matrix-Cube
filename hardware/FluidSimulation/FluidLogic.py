import numpy as np
from config import (
    CUBE_SIZE, FLUID_FILL_RATIO, PARTICLE_MASS, DAMPING,
    VISCOSITY, PARTICLE_RADIUS, COLLISION_DAMPING,
    SPATIAL_HASH_CELL_SIZE, SIMULATION_SPEED
)


class Particle:
    __slots__ = ['position', 'velocity']

    def __init__(self, position: np.ndarray):
        self.position = position.astype(float)
        self.velocity = np.zeros(3, dtype=float)


class FluidSimulation:
    def __init__(self):
        """
        Particle based fluid simulation operating in continuous 3D space.
        The cube occupies [0, CUBE_SIZE-1] on all axes.
        Particles are initialized randomly filling the bottom of the cube
        based on FLUID_FILL_RATIO.
        """
        self.size = CUBE_SIZE
        self.dt = SIMULATION_SPEED
        self.bounds = float(self.size - 1)
        self.diameter = PARTICLE_RADIUS * 2

        total_voxels = self.size ** 3
        self.num_particles = int(total_voxels * FLUID_FILL_RATIO)

        self.particles = self._initialize_particles()

    # ─── Initialization ────────────────────────────────────────────────────────

    def _initialize_particles(self) -> list:
        """
        Place particles randomly within the lower portion of the cube
        based on the fill ratio, with a small random initial velocity.
        """
        particles = []
        fill_height = self.bounds * FLUID_FILL_RATIO * 3  # Scale fill height

        for _ in range(self.num_particles):
            pos = np.array([
                np.random.uniform(0, self.bounds),
                np.random.uniform(0, self.bounds),
                np.random.uniform(0, min(fill_height, self.bounds))
            ])
            p = Particle(pos)
            p.velocity = np.random.uniform(-0.1, 0.1, 3)
            particles.append(p)

        return particles

    # ─── Spatial Hashing ───────────────────────────────────────────────────────

    def _hash_position(self, pos: np.ndarray) -> tuple:
        """Convert a continuous position to a spatial hash cell key."""
        return (
            int(pos[0] / SPATIAL_HASH_CELL_SIZE),
            int(pos[1] / SPATIAL_HASH_CELL_SIZE),
            int(pos[2] / SPATIAL_HASH_CELL_SIZE)
        )

    def _build_spatial_hash(self) -> dict:
        """
        Build a spatial hash map of all particles for O(1) neighbor lookup.
        Each cell key maps to a list of particles within that cell.
        """
        table = {}
        for p in self.particles:
            key = self._hash_position(p.position)
            if key not in table:
                table[key] = []
            table[key].append(p)
        return table

    def _get_neighbors(self, p: Particle, table: dict) -> list:
        """
        Return all particles in the 27 neighboring cells around a particle.
        This is the core of the spatial hashing optimization —
        only nearby particles are checked for collision.
        """
        cx, cy, cz = self._hash_position(p.position)
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    key = (cx + dx, cy + dy, cz + dz)
                    if key in table:
                        neighbors.extend(table[key])
        return neighbors

    # ─── Physics ───────────────────────────────────────────────────────────────

    def _apply_gravity(self, p: Particle, gravity: np.ndarray):
        """Apply gravitational acceleration to a particle's velocity."""
        p.velocity += gravity * self.dt

    def _apply_viscosity(self, p: Particle):
        """Dampen velocity each frame to simulate fluid viscosity."""
        p.velocity *= VISCOSITY
        # Zero out velocity below resting threshold to prevent jitter
        if np.linalg.norm(p.velocity) < 0.01:
            p.velocity[:] = 0.0

    def _update_position(self, p: Particle):
        """Integrate velocity to update position."""
        p.position += p.velocity * self.dt

    def _resolve_wall_collisions(self, p: Particle):
        """
        Reflect velocity and clamp position when a particle hits a wall.
        DAMPING controls how much energy is lost on impact.
        """
        for axis in range(3):
            if p.position[axis] < 0:
                p.position[axis] = 0.0
                p.velocity[axis] = abs(p.velocity[axis]) * DAMPING
            elif p.position[axis] > self.bounds:
                p.position[axis] = self.bounds
                p.velocity[axis] = -abs(p.velocity[axis]) * DAMPING

    def _resolve_particle_collisions(self, p: Particle, neighbors: list):
        """
        Push overlapping particles apart with a gentle positional correction.
        Velocity exchange is kept minimal to avoid introducing jitter energy.
        """
        for other in neighbors:
            if other is p:
                continue

            delta = p.position - other.position
            dist = np.linalg.norm(delta)

            if dist < self.diameter and dist > 1e-6:
                axis = delta / dist
                overlap = self.diameter - dist

                # Soft positional correction — only push halfway to avoid overcorrection
                correction = axis * (overlap / 2) * 0.5
                p.position += correction
                other.position -= correction

                # Only bleed off velocity along the collision axis, don't add energy
                rel_vel = np.dot(p.velocity - other.velocity, axis)
                if rel_vel < 0:
                    impulse = axis * rel_vel * 0.3
                    p.velocity -= impulse
                    other.velocity += impulse

    # ─── Simulation Step ───────────────────────────────────────────────────────

    def step(self, gravity: np.ndarray):
        """
        Advance the simulation by one time step.

        :param gravity: 3D gravity vector from GravityVector.get()
                        e.g. np.array([0.0, 0.0, -9.8]) for straight down
        """
        spatial_hash = self._build_spatial_hash()

        for p in self.particles:
            self._apply_gravity(p, gravity)
            self._apply_viscosity(p)
            self._update_position(p)
            self._resolve_wall_collisions(p)
            neighbors = self._get_neighbors(p, spatial_hash)
            self._resolve_particle_collisions(p, neighbors)

        # Clamp all positions after collision resolution
        for p in self.particles:
            p.position = np.clip(p.position, 0.0, self.bounds)

    # ─── Rendering ─────────────────────────────────────────────────────────────

    def get_voxels(self) -> set:
        """
        Convert continuous particle positions to integer voxel coordinates.
        Returns a set of (x, y, z) tuples representing lit LEDs.
        Multiple particles in the same voxel count as one lit LED.
        """
        voxels = set()
        for p in self.particles:
            x = int(round(p.position[0]))
            y = int(round(p.position[1]))
            z = int(round(p.position[2]))
            x = np.clip(x, 0, self.size - 1)
            y = np.clip(y, 0, self.size - 1)
            z = np.clip(z, 0, self.size - 1)
            voxels.add((x, y, z))
        return voxels