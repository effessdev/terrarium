"""Global application settings."""

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Terrarium"

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

TARGET_FPS = 60

# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

SIMULATION_HZ = 30
MAX_SIMULATION_STEPS_PER_FRAME = 5

DEFAULT_SIMULATION_SPEED = 1.0

SIMULATION_SPEEDS = (
    0.0,
    1.0,
    2.0,
    4.0,
    8.0,
    16.0,
)

# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------

# Zoom in the simulation by making each terrain cell and each object
# effectively larger. This shrinks the active world size and reduces the
# number of plants/worms that need to be simulated at once.
WORLD_CELL_SIZE = 16

WORLD_WIDTH = WINDOW_WIDTH // WORLD_CELL_SIZE
WORLD_HEIGHT = WINDOW_HEIGHT // WORLD_CELL_SIZE

# ---------------------------------------------------------------------------
# Day / night
# ---------------------------------------------------------------------------

DAY_LENGTH_SECONDS = 180.0

# ---------------------------------------------------------------------------
# Plants
# ---------------------------------------------------------------------------

# Reproduction.
# Speed up plant reproduction and seedling size so food recovers
# faster when worms overgraze.
PLANT_REPRODUCTION_COOLDOWN = 4.0
PLANT_REPRODUCTION_RANGE = 6
PLANT_REPRODUCTION_MATURITY = 0.55
PLANT_SEEDLING_GROWTH_MIN = 0.25
PLANT_SEEDLING_GROWTH_MAX = 0.50

# With the world zoomed in, keep the plant population lower so the scene
# stays sparse and fast while still feeling alive.
PLANT_MAX_COUNT = 400

# ---------------------------------------------------------------------------
# Worms
# ---------------------------------------------------------------------------

# Number of worms placed into a newly generated world.
# The larger world scale means fewer worms are needed to fill the scene.
INITIAL_WORM_COUNT_MIN = 3
INITIAL_WORM_COUNT_MAX = 6

# Worm movement.
WORM_MOVE_SPEED = 2.4
WORM_WANDER_INTERVAL = 3.0

# Need thresholds.
WORM_HUNGER_THRESHOLD = 0.42
WORM_THIRST_THRESHOLD = 0.48

# Need depletion.
#
# Slower than before so a single meal sustains a worm long
# enough for plants to regrow before it needs to eat again.
# Reduce hunger rate so worms can travel farther before needing food.
# This makes them less likely to starve while crossing the world.
WORM_HUNGER_RATE = 0.002
WORM_THIRST_RATE = 0.016

# Consumption.
WORM_FOOD_AMOUNT = 0.90
WORM_WATER_AMOUNT = 0.70

# Growth.
WORM_GROWTH_RATE = 0.055
WORM_MATURE_SIZE = 1.0

# Reproduction.
# Allow reproduction from a very young age to encourage rapid
# population growth and stronger competition for food.
WORM_REPRODUCTION_AGE = 0.1
WORM_REPRODUCTION_COOLDOWN = 8.0
WORM_REPRODUCTION_RANGE = 6.0

# Reproduction tuning: lower the growth threshold so worms can reproduce
# earlier and more frequently. These settings can be tuned to reach
# a food-vs-worms equilibrium.
WORM_REPRODUCTION_GROWTH_THRESHOLD = 0.60

# Crowding.
#
# A worm dies when too many other living worms are packed into
# its immediate neighbourhood. This caps density without needing
# a global population limit and without breaking reproduction,
# which relies on two worms being moderately close.
WORM_CROWDING_RADIUS = 1.0
WORM_CROWDING_LIMIT = 5

# Lifespan and death.
WORM_MIN_LIFESPAN = 180.0
WORM_MAX_LIFESPAN = 300.0

WORM_STARVATION_LIMIT = 120.0
WORM_DEHYDRATION_LIMIT = 100.0

# Corpse decomposition.
WORM_ROT_DURATION = 45.0

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------

SHOW_DEBUG_INFO = True