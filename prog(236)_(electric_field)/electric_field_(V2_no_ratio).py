from e2D.envs import *  # Import everything from the e2D.envs module. This likely includes Vector2D (V2), RootEnv, DefEnv, and other utilities for 2D graphics and environment management.
from e2D.def_colors import light_gray, gray_asparagus  # Import predefined colors used for UI and rendering aesthetics.
from numba import njit, prange  # Import decorators for just-in-time (JIT) compilation and parallel execution from Numba.
import numpy as np  # Import NumPy for fast, vectorized numerical operations and array manipulation.
from datetime import datetime  # Import datetime for timestamping, e.g., for file naming in screenshots or logging.

# ---------------------- TEXT AND FONT CONFIGURATION ---------------------- #
TEXT_COLOR_1 = light_gray()  
# A light gray color used for on-screen text, improving readability on dark backgrounds.

TEXT_FONT = NEW_FONT(20, "cascadiamonoregular")
# Creates a font object with size 20 using the Cascadia Mono Regular typeface.
# This is useful for displaying debug text or data with a fixed-width font, preserving alignment.

# ---------------------- SCREEN GEOMETRY ---------------------- #
SCREEN_SIZE = V2(1920, 1080)  
# Vector2D object representing screen resolution. Using a vector here simplifies geometric operations later.

SCREEN_SIZE_X = SCREEN_SIZE.x  
# Extract X (width) component for convenience and clarity in later code.

SCREEN_SIZE_Y = SCREEN_SIZE.y  
# Extract Y (height) component similarly.

# ---------------------- CUSTOM DISTRIBUTION FUNCTION FOR CHARGES ---------------------- #
# Here im using my custom distribution function to skew the uniform distribution of charges.
# https://www.desmos.com/calculator/o96rfcqrgu
# This is the desmos link to my custom distribution functions which i use in most of my simulations.
CHARGES_PROBABILITY_FUNC = lambda x, o=4, k=1, a=2, j=99: (
    (o * (np.sign(2 * x - 1) * np.abs(2 * x - 1)**(1 / k) + 1) + 
     a * ((2 * x - 1)**j + 1)) / 
    (2 * (a + o))
)
# This lambda function modifies uniform distributions into custom ones that cluster values
# around x = 1/3 and x = 2/3. This helps position charges in interesting locations on screen.
# Parameters:
# - o: weight of the outer shaping term
# - k: curvature control for symmetric term
# - a: weight of asymmetric distortion
# - j: order of the polynomial distortion
# This function skews the distribution to create more visually/physically interesting setups.

# ---------------------- SIMULATION CONFIGURATION ---------------------- #
ORIGINS_COUNT = 1000
# Number of field line starting points (seeds), typically placed near charges or in grid.

DEPTH = 500  
# Maximum number of steps a field line can take; prevents infinite loops or overly long curves.

STEP = 0.005
# Length of each integration step used to trace the field line (affects resolution and performance).

ORBS_STEP = 5
# Number of steps to take for each orb in the simulation, controlling how often they are updated. (Ex => 10 steps per frame)
MAX_ORBS_LIFETIME = 10
# Maximum lifetime of an orb in seconds before it is removed from the simulation.

CHARGES_VALUES = np.array([-1.0, 1.0, -1.0], dtype=np.float64)  
# Array of point charge magnitudes (in arbitrary units).

CHARGES_COUNT = CHARGES_VALUES.size  # 3
# Total number of point charges in the simulation.

# ---------------------- CHARGE POSITIONING ---------------------- #
CHARGES_UNIT_POSITIONS_XS = np.array([1/5, 1/2, 4/5])
# Preferred normalized horizontal positions (between 0 and 1).

# CHARGES_UNIT_POSITIONS_XS = np.random.uniform(0, 1, CHARGES_COUNT)
# # Otherwise you can use a random distribution for charge positions.
# CHARGES_UNIT_POSITIONS_XS = CHARGES_PROBABILITY_FUNC(CHARGES_UNIT_POSITIONS_XS)
# # And pass them through the custom distribution function to skew them.

CHARGES_POSITIONS_XS = CHARGES_UNIT_POSITIONS_XS * SCREEN_SIZE.x  
# Then map these normalized positions to pixel coordinates for X-axis.

# Same thing for the Y-axis.

CHARGES_UNIT_POSITIONS_YS = np.array([1/5, 1/2, 4/5])  
# # Preferred normalized vertical positions.
# CHARGES_UNIT_POSITIONS_YS = np.random.uniform(0, 1, CHARGES_COUNT)
# # Random distribution for charge positions on Y-axis.
# CHARGES_UNIT_POSITIONS_YS = CHARGES_PROBABILITY_FUNC(CHARGES_UNIT_POSITIONS_YS)
# # Apply the custom distribution function to skew the Y positions.

CHARGES_POSITIONS_YS = CHARGES_UNIT_POSITIONS_YS * SCREEN_SIZE.y  
# Map to pixel coordinates for Y-axis.

# ---------------------- DRAWING AND COLLISION ---------------------- #
REAL_CHARGES_RADIUS = 25  
# Radius (in pixels) of the graphical representation of each charge. Also used for collision detection.
REAL_ORBS_RADIUS = 15
# Radius of the orbs in the simulation, used for rendering.

INITIAL_CUT_ON_EDGE = False  
# Whether to stop tracing field lines when they leave the screen. If False, lines wrap or continue off-screen.

REAL_RADIUS_SQRD = REAL_CHARGES_RADIUS ** 2  
# Precomputed square of the radius to avoid using expensive square roots in distance calculations.

REAL_RADIUS_SQRD_CONTEXT = (REAL_CHARGES_RADIUS / SCREEN_SIZE_X) ** 2  
# Normalized version of the squared radius, used when positions are normalized to [0, 1] coordinates.
# Helps in generalizing collision or proximity checks in a resolution-independent way.

FIELD_LINE_COLOR = gray_asparagus()  
# Color of the electric field lines when drawn using low spec mode. Visually neutral but distinct from background and charges.

# ---------------------- FIELD LINE COMPUTATION ---------------------- #
@njit(parallel=True, fastmath=True)
def compute_field_lines(origins_xs: np.ndarray,
                        origins_ys: np.ndarray,
                        charge_positions_xs: np.ndarray,
                        charge_positions_ys: np.ndarray,
                        charge_magnitudes: np.ndarray,
                        origin_values: np.ndarray,
                        cut_on_edge: bool
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes electric field lines for a set of origins, using a forward Euler integration scheme.
    Optimized using Numba for parallel computation and fast math.

    Parameters:
        - origins_xs, origins_ys: 1D arrays of normalized starting points for field lines (range [0,1])
        - charge_positions_xs, charge_positions_ys: 1D arrays of normalized coordinates of point charges
        - charge_magnitudes: 1D array of scalar charge magnitudes (signed)
        - origin_values: 1D array of +1 or -1 values indicating field line polarity (direction)
        - cut_on_edge: if True, stops field lines when they exit the screen boundary

    Returns:
        - lines: (ORIGINS_COUNT, DEPTH, 2) array containing the 2D trajectory of each field line
        - lengths: (ORIGINS_COUNT,) array with the actual computed length (number of steps) per line
        - colors: (ORIGINS_COUNT, DEPTH, 3) array of RGB colors for each segment, for fade/visual effect
    """

    # Allocate memory for the output arrays
    lines = np.empty((ORIGINS_COUNT, DEPTH, 2), dtype=np.float64)   # Stores coordinates of the field lines
    lengths = np.empty(ORIGINS_COUNT, dtype=np.int32)               # Stores the number of valid steps per line
    colors = np.empty((ORIGINS_COUNT, DEPTH, 3), dtype=np.uint8)    # Stores RGB color for visual fading

    # Minimum field magnitude below which the line is considered to have terminated (field too weak)
    min_norm = 1e-2

    # Loop over each starting point (field line origin) in parallel
    for i in prange(ORIGINS_COUNT):
        # Initialize particle position (normalized coordinates in [0,1])
        px, py = origins_xs[i], origins_ys[i]
        polarity = origin_values[i]  # +1 or -1, determines direction of integration
        length = DEPTH               # Default full length unless terminated earlier

        # Iterate over max steps allowed (DEPTH)
        for j in range(DEPTH):
            fx = fy = 0.0            # Accumulated field vector components
            stop = False             # Whether to terminate this line early (e.g., collision)

            # Accumulate electric field contribution from each charge
            for c in range(CHARGES_COUNT):
                dx = px - charge_positions_xs[c]
                dy = py - charge_positions_ys[c]
                r2 = dx * dx + dy * dy + 1e-12       # Add epsilon to avoid division by zero
                r2_normalized = dx * dx + dy * dy    # Normalized squared distance (no epsilon)

                # Terminate field line if it's inside a charge (within visible radius) and opposite polarity
                # This is a collision check: if the particle is within the charge radius and has opposite polarity
                if (r2_normalized < REAL_RADIUS_SQRD_CONTEXT) and (polarity * charge_magnitudes[c] < 0):
                    stop = True
                    break

                # Electric field magnitude using Coulomb’s law: k*q / r^2, but we normalize r^3 for direction
                f = charge_magnitudes[c] / (r2 * np.sqrt(r2))
                fx += dx * f * polarity  # Multiply by polarity to flip direction if needed
                fy += dy * f * polarity

            # Compute norm of the resulting electric field vector
            norm = np.sqrt(fx * fx + fy * fy)

            # Check if integration should stop (weak field or collision)
            if stop or norm < min_norm:
                length = j
                lines[i, j:, 0] = px  # Fill remaining points with the last known position
                lines[i, j:, 1] = py
                break

            # Move the particle a single step in the direction of the field (Euler step)
            px += fx / norm * STEP
            py += fy / norm * STEP

            # Store the new position
            lines[i, j, 0] = px
            lines[i, j, 1] = py

            # Optional early termination if the line exits the screen (in normalized coordinates)
            if cut_on_edge and (px < 0 or px > 1 or py < 0 or py > SCREEN_SIZE_Y / SCREEN_SIZE_X):
                length = j
                lines[i, j:, 0] = px
                lines[i, j:, 1] = py
                break

        # Store actual computed length for this line
        lengths[i] = length if length < DEPTH else DEPTH

        # Compute color fading along the field line for rendering
        # Red-to-blue gradient depending on polarity and distance from origin
        for j in range(lengths[i]):
            di = 1 - j / lengths[i]  # Linear interpolation factor (1 at start, 0 at end)

            if polarity > 0:
                # Fade from red (head) to blue (tail)
                colors[i, j, 0] = int(255 * di)           # Red
                colors[i, j, 1] = 0                       # Green
                colors[i, j, 2] = int(255 * (1 - di))     # Blue
            else:
                # Fade from blue (head) to red (tail)
                colors[i, j, 0] = int(255 * (1 - di))     # Red
                colors[i, j, 1] = 0                       # Green
                colors[i, j, 2] = int(255 * di)           # Blue

    # Return pixel-space coordinates (multiply by screen width), actual lengths, and color gradients
    return lines * SCREEN_SIZE_X, lengths, colors

class Env(DefEnv):
    def __init__(self) -> None:
        """Initialize the simulation environment and draw the first frame."""
        # Initialize empty arrays to store field lines and their lengths
        self.lines = np.empty((ORIGINS_COUNT, DEPTH, 2), dtype=np.float64)
        self.line_lengths = np.empty(ORIGINS_COUNT, dtype=np.int32)

        # Store the polarity (+1/-1) for each field line origin
        self.origins_values = np.empty(ORIGINS_COUNT, dtype=np.int8)

        # Store RGB color data for each point on every field line
        self.line_colors = np.empty((ORIGINS_COUNT, DEPTH, 3), dtype=np.float32)

        # Determines whether lines should be truncated at the screen edge
        self.cut_on_edge = INITIAL_CUT_ON_EDGE

        # Toggle display of control instructions on screen
        self.show_keybinds = False

        # Toggle between simple or advanced color styling for field lines
        self.advanced_lines_colors = True

        # Stores last mode used to place field line origins (0 = random, 1 = near charges)
        self.last_origins_randomization = 1

        # Create an off-screen surface for rendering the field
        self.surface = pg.Surface(rootEnv.screen_size())

        # Initialize charge data and field line origins
        self.reset_charges(False)
        self.reset_origins(True)

        # List of temporary orbs placed by user (position, sign, spawn time)
        self.orbs : list[tuple[Vector2D, Literal[1, -1], float]] = []

        # Create transparent surface for keybind instructions
        self.keybinds_surf = pg.Surface(rootEnv.screen_size(), pg.SRCALPHA, 32).convert_alpha()

        # List of control instructions displayed to user
        labels = [
            "quit | X or alt+F4       ",
            "move selected charge | LEFT CLICK + DRAG ",
            "select charge | LEFT CLICK        ",
            "change selected charge value by 0.1 | UP/DOWN ARROW     ",
            "change selected charge value by 1 | RIGHT/LEFT ARROW  ",
            "toggle keybinds | Q  ",
            "toggle cut line on screen edge | W  ",
            "reset field lines origins randomly | E  ",
            "reset field lines origins around positive charges | R  ",
            "reset charges to start positions | T  ",
            "reset charges to random positions | Y  ",
            "randomize charges values | A  ",
            "take screenshot | S  ",
            "toggle advanced line colors (LOW SPEC MODE)| D  ",
            "add positive charged orb at mouse position | F  ",
            "add negative charged orb at mouse position | G  ",
        ]

        # Render keybind labels to the surface
        for i, label in enumerate(labels):
            rootEnv.print(label,
                          rootEnv.screen_size.mult(y=0) + V2(0, 40 * i),
                          pivot_position="top_right",
                          color=WHITE_COLOR_PYG,
                          margin=V2(10, 10),
                          font=TEXT_FONT,
                          bg_color=BLACK_COLOR_PYG,
                          border_radius=10,
                          personalized_surface=self.keybinds_surf)

    def reset_charges(self, update: bool = True) -> None:
        """Reset charges to their default positions and values."""
        # Deselect any currently selected charge
        self.selected_charge_index = -1
        self.last_selected = -1

        # Copy default charge values and positions
        self.charges_values = CHARGES_VALUES.copy()
        self.charges_positions_xs = CHARGES_POSITIONS_XS.copy()
        self.charges_positions_ys = CHARGES_POSITIONS_YS.copy()

        # Optionally update field line origins as well
        if update:
            self.reset_origins(True)

    def reset_origins_random(self, update: bool = True) -> None:
        """Place field line origins randomly on screen with polarity based on charge ratios."""
        # Place origins at random (x, y) positions on screen
        self.origins_xs = np.random.uniform(-1, 1, ORIGINS_COUNT)
        self.origins_ys = np.random.uniform(-1, 1, ORIGINS_COUNT)

        # Assign polarity according to the ratio of positive charges
        positive_charges_ratio = np.sum(self.charges_values > 0) / CHARGES_COUNT
        self.origins_values = np.random.choice([1, -1], size=ORIGINS_COUNT, p=[positive_charges_ratio, 1 - positive_charges_ratio]).astype(np.int8)

        # Record the randomization mode used
        self.last_origins_randomization = 0

        # Optionally update field lines after randomization
        if update:
            self.update_lines()

    def reset_origins(self, update: bool = True) -> None:
        """Distribute field line origins near charges proportionally to their |magnitude|."""
        abs_mags = np.abs(self.charges_values)
        total = np.sum(abs_mags)
        
        if total == 0:
            # Fallback to uniform distribution if all charges are 0
            weights = np.ones(CHARGES_COUNT) / CHARGES_COUNT
        else:
            weights = abs_mags / total

        # Compute number of origins per charge based on weights
        origins_per_charge = np.floor(weights * ORIGINS_COUNT).astype(np.int32)
        assigned = np.sum(origins_per_charge)
        remainder = ORIGINS_COUNT - assigned

        # Distribute remaining origins to the charges with largest fractional parts
        if remainder > 0:
            fractional = (weights * ORIGINS_COUNT) - origins_per_charge
            top_indices = np.argsort(fractional)[-remainder:]
            origins_per_charge[top_indices] += 1

        # Create indices array with the charge index repeated accordingly
        indices = np.repeat(np.arange(CHARGES_COUNT), origins_per_charge)

        # Shuffle to avoid visible banding artifacts
        np.random.shuffle(indices)

        # Store indices of the associated charges
        self.origins_attached_indices = indices
        self.origins_values = np.sign(self.charges_values[indices]).astype(np.int8)

        # Spread the origins around each charge slightly randomly
        angles = np.random.uniform(0, 2 * np.pi, ORIGINS_COUNT)
        # radii = np.random.uniform(REAL_CHARGES_RADIUS * .9, REAL_CHARGES_RADIUS * 1.1, ORIGINS_COUNT)
        dx = np.cos(angles) * REAL_CHARGES_RADIUS * .75
        dy = np.sin(angles) * REAL_CHARGES_RADIUS * .75

        self.origins_xs = self.charges_positions_xs[indices] + dx
        self.origins_ys = self.charges_positions_ys[indices] + dy
        self.last_origins_randomization = 1

        if update:
            self.update_lines()

    def draw(self) -> None:
        """Render the environment on screen, including orbs and optionally keybinds."""
        # Blit simulation surface to screen
        rootEnv.screen.blit(self.surface, (0, 0))

        # Draw all active orbs with their time-to-live
        for orb_pos, orb_charge, orb_time in self.orbs:
            pg.draw.circle(rootEnv.screen,
                           RED_COLOR_PYG if orb_charge > 0 else BLUE_COLOR_PYG,
                           orb_pos(),
                           REAL_ORBS_RADIUS)
            pg.draw.circle(rootEnv.screen,
                           WHITE_COLOR_PYG,
                           orb_pos(),
                           REAL_ORBS_RADIUS,
                           int(REAL_ORBS_RADIUS / 5))
            rootEnv.print(
                f"{max(0, MAX_ORBS_LIFETIME - rootEnv.runtime_seconds + orb_time):.2f} s",
                orb_pos.sub(y=REAL_ORBS_RADIUS * 1.5),
                pivot_position="bottom_center",
                color=TEXT_COLOR_1,
                font=TEXT_FONT
            )

        # Optionally draw the keybinds UI
        if self.show_keybinds:
            rootEnv.screen.blit(self.keybinds_surf, (0, 0))

    def render(self) -> None: 
        self.surface.fill(BLACK_COLOR_PYG)  # Clear the surface with a black background
        """This function renders everything: field lines, charges, and UI text."""

        # Draw each electric field line
        for line, length, colors in zip(self.lines, self.line_lengths, self.line_colors):
            masked_line = line[:length]  # Trim the line to its actual drawn length

            if self.advanced_lines_colors:
                # If using color gradients, draw each segment with its corresponding color
                masked_colors = colors[:length]
                for i in range(1, len(masked_line)):
                    pg.draw.aaline(self.surface, masked_colors[i], masked_line[i - 1], masked_line[i])
            else:
                # Draw a single-colored polyline
                pg.draw.aalines(self.surface, FIELD_LINE_COLOR, False, masked_line)

        # Draw each point charge
        for i, (value, pos_x, pos_y) in enumerate(zip(self.charges_values, self.charges_positions_xs, self.charges_positions_ys)):
            # Determine color by sign: red for positive, blue for negative, white for zero
            color = RED_COLOR_PYG if value > 0 else (BLUE_COLOR_PYG if value < 0 else WHITE_COLOR_PYG)

            # Draw the main circle of the charge
            pg.draw.circle(self.surface, color, (pos_x, pos_y), REAL_CHARGES_RADIUS,
                        int(REAL_CHARGES_RADIUS / 5) if i == self.selected_charge_index else 0)

            # Highlight the charge with a white ring if it was the last one clicked
            if i == self.last_selected:
                pg.draw.circle(self.surface, WHITE_COLOR_PYG, (pos_x, pos_y), REAL_CHARGES_RADIUS / 5)

            # Display the numeric value of the charge below it
            rootEnv.print(str(round(value, 3)), V2(pos_x, pos_y - REAL_CHARGES_RADIUS * 1.25),
                        pivot_position="bottom_center", font=TEXT_FONT, personalized_surface=self.surface)

            # Draw an outer white border for visibility
            pg.draw.circle(self.surface, WHITE_COLOR_PYG, (pos_x, pos_y), REAL_CHARGES_RADIUS, int(REAL_CHARGES_RADIUS / 9))

        # Show a bottom-centered text with the keybind help message
        rootEnv.print("press Q to view keybinds", rootEnv.screen_size.mult(x=.5),
                    pivot_position="bottom_center", color=TEXT_COLOR_1,
                    margin=V2(0, 10), font=TEXT_FONT, personalized_surface=self.surface)

    def update_lines(self) -> None:
        """Recompute all electric field lines based on the current configuration."""
        self.lines[:], self.line_lengths[:], self.line_colors[:] = compute_field_lines(
            self.origins_xs / SCREEN_SIZE_X,
            self.origins_ys / SCREEN_SIZE_X,
            self.charges_positions_xs / SCREEN_SIZE_X,
            self.charges_positions_ys / SCREEN_SIZE_X,
            self.charges_values,
            self.origins_values,
            self.cut_on_edge
        )
        self.render()  # Update visual display

    def update(self) -> None:
        """Handle input from user and update simulation accordingly."""

        # Toggle keybind visibility
        if rootEnv.keyboard.get_key(pg.K_q, "just_pressed"):
            self.show_keybinds = not self.show_keybinds

        # Toggle edge-cutting for field lines
        if rootEnv.keyboard.get_key(pg.K_w, "just_pressed"):
            self.cut_on_edge = not self.cut_on_edge
            self.update_lines()

        # Reset origins to random positions
        if rootEnv.keyboard.get_key(pg.K_e, "just_pressed"):
            self.reset_origins_random()

        # Reset origins around positive charges
        if rootEnv.keyboard.get_key(pg.K_r, "just_pressed"):
            self.reset_origins()

        # Reset all charges to their default configuration
        if rootEnv.keyboard.get_key(pg.K_t, "just_pressed"):
            self.reset_charges()

        # Randomize charge positions using the distribution function
        if rootEnv.keyboard.get_key(pg.K_y, "just_pressed"):
            self.charges_positions_xs = CHARGES_PROBABILITY_FUNC(np.random.uniform(0, 1, CHARGES_COUNT)) * 2 - 1
            self.charges_positions_ys = CHARGES_PROBABILITY_FUNC(np.random.uniform(0, 1, CHARGES_COUNT)) * 2 - 1
            self.reset_origins()

        # Randomize charge values between -10 and 10
        if rootEnv.keyboard.get_key(pg.K_a, "just_pressed"):
            self.charges_values = np.random.uniform(-10, 10, CHARGES_COUNT)
            self.reset_origins()

        # Save screenshot of the current field
        if rootEnv.keyboard.get_key(pg.K_s, "just_pressed"):
            self.take_screenshot()

        # Toggle field line color gradient
        if rootEnv.keyboard.get_key(pg.K_d, "just_pressed"):
            self.advanced_lines_colors = not self.advanced_lines_colors
            self.render()

        # Add a positive charged orb at the mouse position
        if rootEnv.keyboard.get_key(pg.K_f, "just_pressed"):
            self.orbs.append((rootEnv.mouse.position, 1, rootEnv.runtime_seconds))

        # Add a negative charged orb at the mouse position
        if rootEnv.keyboard.get_key(pg.K_g, "just_pressed"):
            self.orbs.append((rootEnv.mouse.position, -1, rootEnv.runtime_seconds))

        # Select a charge with left mouse click
        if rootEnv.mouse.get_key(0, "just_pressed"):
            selected_one = False
            for i, (charge_x, charge_y) in enumerate(zip(self.charges_positions_xs, self.charges_positions_ys)):
                if rootEnv.mouse.position.distance_to(Vector2D(charge_x, charge_y), False) < REAL_RADIUS_SQRD:
                    selected_one = True
                    self.last_selected = i
                    self.selected_charge_index = i
                    break
            if not selected_one:
                self.selected_charge_index = -1
                self.render()
        elif rootEnv.mouse.get_key(0, "just_released"):
            self.selected_charge_index = -1  # Stop dragging

        # If a charge is selected, allow changing its value using arrows
        if self.last_selected != -1:
            last_selected_value_sign = np.sign(self.charges_values[self.last_selected])

            if rootEnv.keyboard.get_key(pg.K_UP, "pressed"):
                self.charges_values[self.last_selected] = round(self.charges_values[self.last_selected] + .1, 2)
                self.update_lines()

            if rootEnv.keyboard.get_key(pg.K_DOWN, "pressed"):
                self.charges_values[self.last_selected] = round(self.charges_values[self.last_selected] - .1, 2)
                self.update_lines()

            if rootEnv.keyboard.get_key(pg.K_RIGHT, "pressed"):
                self.charges_values[self.last_selected] = round(self.charges_values[self.last_selected] + 1, 2)
                self.update_lines()

            if rootEnv.keyboard.get_key(pg.K_LEFT, "pressed"):
                self.charges_values[self.last_selected] = round(self.charges_values[self.last_selected] - 1, 2)
                self.update_lines()

            if rootEnv.keyboard.get_key(pg.K_LEFT, "just_released") or rootEnv.keyboard.get_key(pg.K_RIGHT, "just_released") or \
               rootEnv.keyboard.get_key(pg.K_UP, "just_released") or rootEnv.keyboard.get_key(pg.K_DOWN, "just_released"):
                self.reset_origins()
                self.update_lines()

            # If the sign of the selected charge changed, update the corresponding origins
            if last_selected_value_sign != np.sign(self.charges_values[self.last_selected]):
                self.origins_values[self.origins_attached_indices == self.last_selected] = \
                    np.sign(self.charges_values[self.last_selected]).astype(np.int8)

        # Animate orbs over time by computing electric force steps
        for i, (orb_pos, orb_charge, orb_time) in enumerate(self.orbs):
            if rootEnv.runtime_seconds - orb_time > MAX_ORBS_LIFETIME:
                self.orbs.pop(i)  # Remove expired orb
            else:
                stop = False
                for orb_step in range(ORBS_STEP):
                    fx = fy = 0.0
                    for c in range(CHARGES_COUNT):
                        dx = (orb_pos.x - self.charges_positions_xs[c]) / SCREEN_SIZE_X
                        dy = (orb_pos.y - self.charges_positions_ys[c]) / SCREEN_SIZE_X
                        r2 = dx * dx + dy * dy + 1e-12
                        r2_normalized = dx * dx + dy * dy

                        if (r2_normalized < REAL_RADIUS_SQRD_CONTEXT) and (orb_charge * self.charges_values[c] < 0):
                            stop = True
                            break

                        f = self.charges_values[c] / (r2 * np.sqrt(r2))
                        fx += dx * f * orb_charge
                        fy += dy * f * orb_charge
                    
                    if stop:
                        break

                    norm = np.sqrt(fx * fx + fy * fy)
                    orb_pos.x += fx / norm
                    orb_pos.y += fy / norm
                
                if stop:
                    # If the orb was stopped by a charge, remove it
                    self.orbs.pop(i)

        # Drag selected charge with mouse
        if self.selected_charge_index != -1:
            new_x = rootEnv.mouse.position.x
            new_y = rootEnv.mouse.position.y

            delta_x = new_x - self.charges_positions_xs[self.selected_charge_index]
            delta_y = new_y - self.charges_positions_ys[self.selected_charge_index]

            # Only act if there's real movement
            if delta_x != 0 or delta_y != 0:
                self.charges_positions_xs[self.selected_charge_index] = new_x
                self.charges_positions_ys[self.selected_charge_index] = new_y

                if self.last_origins_randomization == 1:
                    mask = self.origins_attached_indices == self.selected_charge_index
                    self.origins_xs[mask] += delta_x
                    self.origins_ys[mask] += delta_y

                self.update_lines()  # Recompute field

    def take_screenshot(self) -> None:
        """Capture a screenshot of the current simulation state."""
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        pg.image.save(rootEnv.screen, f"electric_field_screenshot_{timestamp}.png")

# ---------------------- SIMULATION LOOP ---------------------- #
# Initialize the environment and begin simulation loop
(rootEnv := RootEnv(screen_size=SCREEN_SIZE, show_fps=False)).init(Env())
while not rootEnv.quit:
    rootEnv.frame()  # Advance frame: handles input, updates logic, and triggers rendering