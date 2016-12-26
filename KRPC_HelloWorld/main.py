import krpc
import time
import PID
import csv

if __name__ == "__main__":
    with open("output/data.csv", "w") as csvfile:
        conn = krpc.connect(name='Hello World')
        vessel = conn.space_center.active_vessel
        writer = csv.writer(csvfile)
        timestamp = 0.0

        # UI element for displaying a value in the game
        canvas = conn.ui.stock_canvas
        screen_size = canvas.rect_transform.size            # Get the size of the game window in pixels
        panel = canvas.add_panel()                          # Add a panel to contain the UI elements
        rect = panel.rect_transform                         # Position the panel on the left of the screen
        rect.size = (200, 100)
        rect.position = (110 - (screen_size[0] / 2), 0)
        text = panel.add_text("Val: 0")                     # Add some text displaying the total engine thrust
        # Position the panel on the left of the screen
        rect = panel.rect_transform
        rect.size = (200, 100)
        rect.position = (110 - (screen_size[0] / 2), 0)

        # Target velocity of the vessel
        target_vertical_speed = 200.0
        target_vertical_speed_reached = False
        print("Launching " + vessel.name + "to approach a stable velocity of -" + str(target_vertical_speed))

        # Write initial rows in CSV (header + first few rows)
        writer.writerow(['setpoint', 'speed', 'throttle'])
        for i in range(0, 20):
            writer.writerow(['0', '0.0', '0.0'])

        # PID controller initialization
        pid_controller = PID.PID(P=0.4, I=0.02, D=0.01)
        pid_controller.setSetpoint(1)                       # target_velocity / target_velocity
        pid_controller.update(feedback_value=0)
        pid_initial_output = pid_controller.output
        print("PID initial output - " + str(pid_initial_output))

        # Hold the pitch and heading at 90 degree (upwards)
        vessel.auto_pilot.target_pitch_and_heading(90, 90)
        vessel.auto_pilot.engage()

        # Full throttle
        vessel.control.throttle = 0.5

        # Lift-off!
        print("Lift-off!")
        vessel.control.activate_next_stage()                # Equivalent to pressing space, highest (lift-off) stage
        time.sleep(0.25)
        # Log
        writer.writerow(['1', str(vessel.flight(vessel.orbit.body.reference_frame).speed), str(vessel.control.throttle)])

        previous_feedback = 0
        current_feedback = 0

        while True:
            # Based on the current velocity, take corrective actions
            current_vertical_speed = vessel.flight(vessel.orbit.body.reference_frame).speed
            current_feedback = current_vertical_speed/target_vertical_speed
            pid_controller.update(feedback_value=current_feedback)

            # Fetch the output from the PID controller
            pid_current_output = pid_controller.output
            output = pid_current_output/pid_initial_output

            # Feed the output to the control interface of the vessel
            vessel.control.throttle = output

            # Log
            writer.writerow(['1',
                             str(vessel.flight(vessel.orbit.body.reference_frame).speed),
                             str(vessel.control.throttle)])

            # TODO: Include more robust algorithm to detect stability
            # If the speed is getting settled down, i.e. instantaneous differential of the feedback is close to 0
            instantaneous_diff = (current_feedback - previous_feedback)/0.001
            if abs(instantaneous_diff) < 0.001:
                print("Target velocity reached and settled.")
                target_vertical_speed_reached = True

            # Update the UI element
            text.content = 'Val: %f' % instantaneous_diff

            # Debug
            print("Vertical speed - %f, feedback - %f, output - %f, instantaneous diff - %f"
                  % (current_vertical_speed, current_feedback, output, instantaneous_diff))

            if vessel.flight().mean_altitude > 5000 and vessel.flight().mean_altitude < 8000 and target_vertical_speed_reached:
                # Shut down the engines
                vessel.control.throttle = 0

                print("Mk16 parachute test criteria satisfied, engines shut down. Staging to jettison liquid fuel tanks..")
                time.sleep(1.5)
                vessel.control.activate_next_stage()        # Tanks jettisoned

                print("Deploying Mk16 parachute..")
                time.sleep(0.5)
                vessel.control.activate_next_stage()        # Parachutes deployed
                break

            # Keep track of the feedback
            previous_feedback = current_feedback

            time.sleep(0.05)
