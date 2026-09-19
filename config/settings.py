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

WORLD_CELL_SIZE = 8

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
PLANT_REPRODUCTION_COOLDOWN = 8.0
PLANT_REPRODUCTION_RANGE = 4
PLANT_REPRODUCTION_MATURITY = 0.55
PLANT_SEEDLING_GROWTH_MIN = 0.15
PLANT_SEEDLING_GROWTH_MAX = 0.30

# Hard cap so plants cannot overrun the world on very fast
# simulation speeds or long unattended runs.
PLANT_MAX_COUNT = 400

# ---------------------------------------------------------------------------
# Worms
# ---------------------------------------------------------------------------

# Number of worms placed into a newly generated world.
INITIAL_WORM_COUNT_MIN = 5
INITIAL_WORM_COUNT_MAX = 9

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
WORM_HUNGER_RATE = 0.004
WORM_THIRST_RATE = 0.016

# Consumption.
WORM_FOOD_AMOUNT = 0.55
WORM_WATER_AMOUNT = 0.70

# Growth.
WORM_GROWTH_RATE = 0.055
WORM_MATURE_SIZE = 1.0

# Reproduction.
WORM_REPRODUCTION_AGE = 25.0
WORM_REPRODUCTION_COOLDOWN = 45.0
WORM_REPRODUCTION_RANGE = 3.0

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

WORM_STARVATION_LIMIT = 60.0
WORM_DEHYDRATION_LIMIT = 50.0

# Corpse decomposition.
WORM_ROT_DURATION = 45.0

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------

SHOW_DEBUG_INFO = True