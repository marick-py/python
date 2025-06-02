from e2D.envs import *  # Import everything from e2D.envs, including rootEnv and utility classes like Vector2D, RootEnv, DefEnv
from e2D.def_colors import light_gray  # Import a predefined light gray color used for text rendering
from numba import njit, prange  # Import decorators from Numba to speed up numerical functions
import numpy as np  # Import NumPy for numerical array handling and math operations
from datetime import datetime  # Import time for timestamping screenshots

# ---------------------- TEXT AND FONT ---------------------- #
# Define the color and font used for on-screen text
TEXT_COLOR_1 = light_gray()
TEXT_FONT = NEW_FONT(20, "cascadiamonoregular")  # Create a font object with size 20 using Cascadia Mono Regular font

# ---------------------- SCREEN SETUP ---------------------- #
# Define screen size and conversions between screen and context (normalized) coordinates
SCREEN_SIZE = V2(1920, 400)  # Full HD screen dimensions as a Vector2D object
HALF_SCREEN_SIZE = SCREEN_SIZE.div(2)  # Used ato convert between context and pixel coordinates
SCREEN_SIZE_NP = np.array(SCREEN_SIZE(), dtype=np.float64)  # Same as above but as NumPy array for fast computation

# ---------------------- CHARGES DISTRIBUTION FUNCTION ---------------------- #
# A custom function that biases the random positions of charges to spawn with more frequency at 1/3 and 2/3 of the screen x and y
CHARGES_PROBABILITY_FUNC = lambda x, o=3, k=3, a=5, j=7: (o*(np.sign(2*x-1)*np.abs(2*x-1)**(1/k)+1)+a*((2*x-1)**j+1))/(2*(a+o))

# ---------------------- SIMULATION PARAMETERS ---------------------- #
# Number of point charges on the screen
CHARGES_COUNT = 4

# Number of starting points for electric field lines
ORIGINS_COUNT = 1500

# Maximum number of steps a field line will take
DEPTH = 500

# Step size for field line integration
STEP = 0.01

# Set values of the charges (positive or negative)
CHARGES_VALUES = np.array([-1.0, -1.0, 1.0, 1.0], dtype=np.float64)

# Generate random positions for charges using the probability function
a = np.array([1/3, 2/3, 1/3, 2/3]) #np.random.uniform(0, 1, CHARGES_COUNT)
CHARGES_POSITIONS_XS = CHARGES_PROBABILITY_FUNC(a) * 2 - 1  # Rescale from [0,1] to [-1,1]
a = np.array([1/3, 2/3, 2/3, 1/3]) #np.random.uniform(0, 1, CHARGES_COUNT)
CHARGES_POSITIONS_YS = CHARGES_PROBABILITY_FUNC(a) * 2 - 1

REAL_CHARGES_RADIUS = 25  # Radius (in pixels) to draw each charge
CUT_ON_EDGE = False  # Flag to stop drawing lines when they exit the visible screen

# Calculate radii used to determine interaction range in normalized space
REAL_RADIUS_SQRD = REAL_CHARGES_RADIUS ** 2
CONTEXT_RADIUS = REAL_CHARGES_RADIUS / HALF_SCREEN_SIZE  # Vector2D containing X and Y context radii
CONTEXT_RADIUS_X = CONTEXT_RADIUS.x
CONTEXT_RADIUS_Y = CONTEXT_RADIUS.y

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
    lines = np.empty((ORIGINS_COUNT, DEPTH, 2), dtype=np.float64)
    lengths = np.empty(ORIGINS_COUNT, dtype=np.int32)
    colors = np.empty((ORIGINS_COUNT, DEPTH, 3), dtype=np.uint8)
    min_norm = 1e-2

    for i in prange(ORIGINS_COUNT):
        px, py = origins_xs[i], origins_ys[i]
        polarity = origin_values[i]
        length = DEPTH

        for j in range(DEPTH):
            fx = fy = 0.0
            stop = False

            for c in range(CHARGES_COUNT):
                dx = px - charge_positions_xs[c]
                dy = py - charge_positions_ys[c]
                r2 = dx * dx + dy * dy + 1e-12
                r2_normalized = dx * dx / CONTEXT_RADIUS_X**2 + dy * dy / CONTEXT_RADIUS_Y**2

                if r2_normalized < 2 ** 2:
                    stop = True
                    break

                f = charge_magnitudes[c] / (r2 * np.sqrt(r2))
                fx += dx * f * polarity
                fy += dy * f * polarity

            norm = np.sqrt(fx * fx + fy * fy)
            if stop or norm < min_norm:
                length = j
                lines[i, j:, 0] = px
                lines[i, j:, 1] = py
                break

            px += fx / norm * STEP
            py += fy / norm * STEP
            lines[i, j, 0] = px
            lines[i, j, 1] = py

            if cut_on_edge and (px < -1 or px > 1 or py < -1 or py > 1):
                length = j
                lines[i, j:, 0] = px
                lines[i, j:, 1] = py
                break

        lengths[i] = length if length < DEPTH else DEPTH

        # Compute the fade colors based on actual length
        actual_length = lengths[i]
        for j in range(actual_length):
            di = 1 - j / actual_length
            if polarity > 0:
                colors[i, j, 0] = int(255 * di)          # Red
                colors[i, j, 1] = 0
                colors[i, j, 2] = int(255 * (1 - di))    # Blue
            else:
                colors[i, j, 0] = int(255 * (1 - di))    # Red
                colors[i, j, 1] = 0
                colors[i, j, 2] = int(255 * di)          # Blue

        # Optional: fill the rest of colors with last one or black
        for j in range(actual_length, DEPTH):
            colors[i, j, 0] = colors[i, actual_length - 1, 0]
            colors[i, j, 1] = colors[i, actual_length - 1, 1]
            colors[i, j, 2] = colors[i, actual_length - 1, 2]

    return lines * SCREEN_SIZE_NP / 2 + SCREEN_SIZE_NP / 2, lengths, colors

class Env(DefEnv):
    def __init__(self) -> None:
        """This is the constructor for the simulation environment.
        It sets up the initial variables and generates the first field lines."""
        # Prepare empty containers to store field line data (positions and lengths)
        self.lines = np.empty((ORIGINS_COUNT, DEPTH, 2), dtype=np.float64)
        self.line_lengths = np.empty(ORIGINS_COUNT, dtype=np.int32)

        self.origins_values = np.empty(ORIGINS_COUNT, dtype=np.int8)
        self.line_colors = np.empty((ORIGINS_COUNT, DEPTH, 3), dtype=np.float32)

        # Whether to stop field lines when they leave the screen
        self.cut_on_edge = CUT_ON_EDGE

        # Whether to show the list of keybinds on the screen
        self.show_keybinds = False

        self.last_origins_randomization = 1  # 0 for random, 1 for around positive charges

        # Initialize charges and field origins
        self.reset_charges(False)
        self.reset_origins(True)

    def reset_charges(self, update:bool=True) -> None:
        """Reset the charges to their original positions and values."""
        self.selected_charge_index = -1  # No charge is selected initially
        self.last_selected = -1  # Also, no previous selection

        # Restore the original charges' values and positions (copied so they can be edited safely)
        self.charges_values = CHARGES_VALUES.copy()
        self.charges_positions_xs = CHARGES_POSITIONS_XS.copy()
        self.charges_positions_ys = CHARGES_POSITIONS_YS.copy()

        # If requested, also reset the origins of the field lines
        if update:
            self.reset_origins(True)

    def reset_origins_random(self, update:bool=True) -> None:
        """Place field line origins randomly anywhere on the screen."""
        self.origins_xs = np.random.uniform(-1, 1, ORIGINS_COUNT)
        self.origins_ys = np.random.uniform(-1, 1, ORIGINS_COUNT)

        # positive count / total count
        positive_charges_ratio = np.sum(self.charges_values > 0) / CHARGES_COUNT
        self.origins_values = np.random.choice([1, -1], size=ORIGINS_COUNT, p=[positive_charges_ratio, 1 - positive_charges_ratio]).astype(np.int8)

        self.last_origins_randomization = 0  # Mark that origins were randomized

        # Update field lines based on these new origins
        if update:
            self.update_lines()

    def reset_origins(self, update: bool = True) -> None:
        """Distribute field line origins around all charges proportionally to their |value|.
        Each origin inherits the sign of the charge it is spawned near."""
        
        # Uniformly assign origins to all charges
        base_count = ORIGINS_COUNT // CHARGES_COUNT
        remainder = ORIGINS_COUNT % CHARGES_COUNT

        # Create array with base_count copies per charge
        indices = np.repeat(np.arange(CHARGES_COUNT), base_count)

        # Distribute remaining origins round-robin
        if remainder > 0:
            extra = np.arange(remainder)
            indices = np.concatenate((indices, extra))

        # Shuffle for non-clustered visual effect
        np.random.shuffle(indices)

        self.origins_attached_indices = indices

        # Sign of the charge each origin was assigned to (+1 or -1)
        self.origins_values = np.sign(self.charges_values[self.origins_attached_indices]).astype(np.int8)

        # Position of the associated charge
        charge_xs = self.charges_positions_xs[self.origins_attached_indices]
        charge_ys = self.charges_positions_ys[self.origins_attached_indices]

        # Generate small random offset around each charge
        angles = np.random.uniform(0, 2 * np.pi, ORIGINS_COUNT)
        radius = (np.cos(angles) * CONTEXT_RADIUS_X) ** 2 + (np.sin(angles) * CONTEXT_RADIUS_Y) ** 2
        radius **= 0.5
        radii = np.random.uniform(radius * 1.5, radius * 2, ORIGINS_COUNT)

        dx = np.cos(angles) * radii
        dy = np.sin(angles) * radii

        self.origins_xs = charge_xs + dx
        self.origins_ys = charge_ys + dy

        self.last_origins_randomization = 1

        if update:
            self.update_lines()

    def r2c(self, position: Vector2D) -> Vector2D:
        """Convert screen (real) coordinates to normalized context coordinates (-1 to 1)."""
        return (position - HALF_SCREEN_SIZE) / HALF_SCREEN_SIZE

    def c2r(self, position: Vector2D) -> Vector2D:
        """Convert normalized context coordinates (-1 to 1) back to screen coordinates."""
        return position * HALF_SCREEN_SIZE + HALF_SCREEN_SIZE

    def draw(self) -> None:
        """This function renders everything: field lines, charges, and text UI."""
        # Draw each field line
        for line, length, colors in zip(self.lines, self.line_lengths, self.line_colors):
            masked_line = line[:length]
            masked_colors = colors[:length]
            for i in range(1, len(masked_line)):
                pg.draw.aaline(rootEnv.screen, masked_colors[i], masked_line[i - 1], masked_line[i])

        # Draw each charge as a circle and its value as text
        for i, (value, pos_x, pos_y) in enumerate(zip(self.charges_values, self.charges_positions_xs, self.charges_positions_ys)):
            color = RED_COLOR_PYG if value > 0 else (BLUE_COLOR_PYG if value < 0 else WHITE_COLOR_PYG)
            pp = self.c2r(Vector2D(pos_x, pos_y))  # Convert to screen coordinates

            # Draw the outer circle of the charge
            pg.draw.circle(rootEnv.screen, color, pp(), REAL_CHARGES_RADIUS,
                           int(REAL_CHARGES_RADIUS / 5) if i == self.selected_charge_index else 0)

            # Draw an extra ring if this was the last charge clicked
            if i == self.last_selected:
                pg.draw.circle(rootEnv.screen, WHITE_COLOR_PYG, pp(), REAL_CHARGES_RADIUS / 3)

            # Draw the numeric value of the charge just below it
            rootEnv.print(str(value), pp - Vector2D(0, REAL_CHARGES_RADIUS * 1.25), pivot_position="bottom_center", font=TEXT_FONT)

        # Draw bottom-centered message about keybinds
        rootEnv.print("press Q to view keybinds", rootEnv.screen_size.mult(x=.5),
                      pivot_position="bottom_center", color=TEXT_COLOR_1,
                      margin=V2(0, 10), font=TEXT_FONT)

        # If keybinds are toggled on, show them in top-right corner
        if self.show_keybinds:
            labels = [
                "quit | X or alt+F4       ",
                "move selected charge | LEFT CLICK + DRAG ",
                "select charge | LEFT CLICK        ",
                "change selected charge value | UP/DOWN ARROW     ",
                "toggle keybinds | Q  ",
                "toggle cut line on screen edge | W  ",
                "reset field lines origins randomly | E  ",
                "reset field lines origins around positive charges | R  ",
                "reset charges to start positions | T  ",
                "reset charges to random positions | Y  ",
                "randomize charges values | U  ",
                "take screenshot | S  "
            ]
            for i, label in enumerate(labels):
                rootEnv.print(label,
                              rootEnv.screen_size.mult(y=0) + V2(0, 40 * i),
                              pivot_position="top_right",
                              color=WHITE_COLOR_PYG,
                              margin=V2(10, 10),
                              font=TEXT_FONT,
                              bg_color=BLACK_COLOR_PYG,
                              border_radius= 10)

    def update_lines(self) -> None:
        """Recompute all field lines based on current charge and origin state."""
        self.lines[:], self.line_lengths[:], self.line_colors = compute_field_lines(
            self.origins_xs,
            self.origins_ys,
            self.charges_positions_xs,
            self.charges_positions_ys,
            self.charges_values,
            self.origins_values,
            self.cut_on_edge
        )

    def update(self) -> None:
        """Handles user input (keyboard and mouse) and updates the simulation accordingly."""

        # Toggle visibility of keybinds
        if rootEnv.keyboard.get_key(pg.K_q, "just_pressed"):
            self.show_keybinds = not self.show_keybinds

        # Toggle edge-cutting behavior
        if rootEnv.keyboard.get_key(pg.K_w, "just_pressed"):
            self.cut_on_edge = not self.cut_on_edge
            self.update_lines()

        # Reset field line origins randomly
        if rootEnv.keyboard.get_key(pg.K_e, "just_pressed"):
            self.reset_origins_random()

        # Reset field line origins around positive charges
        if rootEnv.keyboard.get_key(pg.K_r, "just_pressed"):
            self.reset_origins()

        # Reset all charges to initial state
        if rootEnv.keyboard.get_key(pg.K_t, "just_pressed"):
            self.reset_charges()

        # Reset charges to random positions
        if rootEnv.keyboard.get_key(pg.K_y, "just_pressed"):
            # Randomize charge positions
            self.charges_positions_xs = CHARGES_PROBABILITY_FUNC(np.random.uniform(0, 1, CHARGES_COUNT)) * 2 - 1
            self.charges_positions_ys = CHARGES_PROBABILITY_FUNC(np.random.uniform(0, 1, CHARGES_COUNT)) * 2 - 1
            self.reset_origins()
        
        # Randomize charge values
        if rootEnv.keyboard.get_key(pg.K_u, "just_pressed"):
            # Randomize charge values between -10 and 10
            self.charges_values = np.random.uniform(-10, 10, CHARGES_COUNT)
            self.reset_origins()
        
        # Take a screenshot of the current simulation state
        if rootEnv.keyboard.get_key(pg.K_s, "just_pressed"):
            self.take_screenshot()

        # Select a charge with mouse click
        if rootEnv.mouse.get_key(0, "just_pressed"):
            for i, (charge_x, charge_y) in enumerate(zip(self.charges_positions_xs, self.charges_positions_ys)):
                if rootEnv.mouse.position.distance_to(self.c2r(Vector2D(charge_x, charge_y)), False) < REAL_RADIUS_SQRD:
                    self.last_selected = i
                    self.selected_charge_index = i
        elif rootEnv.mouse.get_key(0, "just_released"):
            self.selected_charge_index = -1  # Stop dragging

        # If a charge is selected, allow changing its value with UP/DOWN arrows
        if self.last_selected != -1:
            if rootEnv.keyboard.get_key(pg.K_UP, "pressed"):
                self.charges_values[self.last_selected] = round(self.charges_values[self.last_selected] + .1, 2)
                self.update_lines()
            elif rootEnv.keyboard.get_key(pg.K_DOWN, "pressed"):
                self.charges_values[self.last_selected] = round(self.charges_values[self.last_selected] - .1, 2)
                self.update_lines()

        # If a charge is being dragged with the mouse
        if self.selected_charge_index != -1:
            # Convert mouse position to context coordinates
            new_x = self.r2c(rootEnv.mouse.position).x
            new_y = self.r2c(rootEnv.mouse.position).y

            # Compute how much the position changed
            delta_x = new_x - self.charges_positions_xs[self.selected_charge_index]
            delta_y = new_y - self.charges_positions_ys[self.selected_charge_index]

            # Only update if there's actual movement
            if delta_x != 0 or delta_y != 0:
                self.charges_positions_xs[self.selected_charge_index] = new_x
                self.charges_positions_ys[self.selected_charge_index] = new_y

                # If the current origin setup is based on attached charges, move their origins
                if self.last_origins_randomization == 1 and hasattr(self, "origins_attached_indices"):
                    # Move all origins linked to this charge
                    mask = self.origins_attached_indices == self.selected_charge_index
                    self.origins_xs[mask] += delta_x
                    self.origins_ys[mask] += delta_y

                # Recompute the field lines after movement
                self.update_lines()
        
    def take_screenshot(self) -> None:
        """Capture a screenshot of the current simulation state."""
        # Save the current screen to a file
        # file_aaaa_mm_dd_hh_mm_ss.png
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        pg.image.save(rootEnv.screen, f"electric_field_screenshot_{timestamp}.png")

# ---------------------- SIMULATION LOOP ---------------------- #
# Create the root environment and start the rendering loop
(rootEnv := RootEnv(screen_size=SCREEN_SIZE, show_fps=False)).init(Env())
while not rootEnv.quit:
    rootEnv.frame()  # This updates the screen, checks input, and calls update/draw