import krpc
import time
import PID
import csv

data_dictionary_list = [{'filename': "output/data1.csv", 'pid_settings': (0.4, 0.02, 0.01)},
                        {'filename': "output/data2.csv", 'pid_settings': (4.0, 0.2, 0.1)},
                        {'filename': "output/data3.csv", 'pid_settings': (0.4, 0.1, 0.02)},
                        {'filename': "output/data4.csv", 'pid_settings': (0.4, 0.1, 0.1)},
                        ]
data_dictionary_list_index = 0

if __name__ == "__main__":
    with open(data_dictionary_list[data_dictionary_list_index]['filename'], "w") as csvfile:
        conn = krpc.connect(name='Hammer test')
        vessel = conn.space_center.active_vessel
        writer = csv.writer(csvfile)

        # Target velocity of the vessel
        target_vertical_speed = 200.0
        target_vertical_speed_reached = False
        print("Launching " + vessel.name + "to approach a stable velocity of -" + str(target_vertical_speed)
              + "between 51000m to 54000m")

        # UI element for displaying text in the game (mostly for debugging purposes)
        canvas = conn.ui.stock_canvas
        screen_size = canvas.rect_transform.size                # Get the size of the game window in pixels
        panel = canvas.add_panel()                              # Add a panel to contain the UI elements
        rect = panel.rect_transform                             # Position the panel on the left of the screen
        rect.size = (200, 100)
        rect.position = (110 - (screen_size[0] / 2), 0)
        ingame_debug_text = panel.add_text("Debug: (No msg)")   # Add some text displaying the total engine thrust
        # Position the panel on the left of the screen
        rect = panel.rect_transform
        rect.size = (200, 100)
        rect.position = (110 - (screen_size[0] / 2), 0)

        # Write initial rows in CSV (header + first few rows)
        writer.writerow(['setpoint', 'speed', 'throttle'])
        for i in range(0, 20):
            writer.writerow(['0', '0.0', '0.0'])

        # PID controller initialization
        pid_settings = data_dictionary_list[data_dictionary_list_index]['pid_settings']
        pid_controller = PID.PID(P=pid_settings[0], I=pid_settings[1], D=pid_settings[2])
        pid_controller.setSetpoint(1)                           # target_velocity / target_velocity
        pid_controller.update(feedback_value=0)
        pid_initial_output = pid_controller.output
        print("PID initial output - " + str(pid_initial_output))

        # Hold the pitch and heading at 90 degree (upwards)
        # vessel.auto_pilot.target_pitch_and_heading(90, 90)
        # vessel.auto_pilot.engage()

        # At first couple stages, we can have SAS on and auto_pilot disengaged
        # As soon as we engage autopilot, SAS goes off
        vessel.control.sas = True

        # Little throttle
        vessel.control.throttle = 0.1

        # Get the flight object for the frame-of-reference of the planet
        static_FOR = vessel.flight(vessel.orbit.body.reference_frame)

        # Lift-off!
        print("Lift-off!")
        print("First Solid Rocket Boosters (SRBs) ignited")
        ingame_debug_text.content = "SRB1 ignition"
        vessel.control.activate_next_stage()                    # Stage 8 SRB ignition

        # Calculate solid fuel for every stage
        # There are 5 tanks (each having 375 fuel) and they are divided 2-2-1 in stages
        # So, total solid fuel = 375*5
        # In the first stage, fuel to be burnt = 375*2
        # In the second stage, fuel to be burnt = 375*2
        # In the third stage, fuel to be burnt = 375*2

        while vessel.resources.amount('SolidFuel') > 1125:      # 375*5 - 375*2 = 375*3 = 1125
            ingame_debug_text.content = "%f" % static_FOR.speed
            time.sleep(0.01)

        time.sleep(0.25)
        print("First Solid Rocket Boosters (SRBs) separated")
        ingame_debug_text.content = "SRB1 separation"
        vessel.control.activate_next_stage()                    # Stage 7 separators

        time.sleep(0.25)
        print("Second Solid Rocket Boosters (SRBs) ignited")
        ingame_debug_text.content = "SRB2 ignition"
        vessel.control.activate_next_stage()                    # Stage 6 SRB ignition

        while vessel.resources.amount('SolidFuel') > 375:       # 375*3 - 375*2 = 375
            ingame_debug_text.content = "%f" % static_FOR.speed
            time.sleep(0.01)

        time.sleep(0.25)
        print("Second Solid Rocket Boosters (SRBs) separated")
        ingame_debug_text.content = "SRB2 separation"
        vessel.control.activate_next_stage()                    # Stage 5 separators (radial)

        # Log
        writer.writerow(['1', str(static_FOR.speed), str(0.0)])

        previous_feedback = 0
        current_feedback = 0

        # Now, we can engage the autopilot and point the ship according to desired pitch and heading
        # vessel.auto_pilot.target_pitch_and_heading(75, 90)
        # vessel.auto_pilot.engage()

        print("Liquid fuel engine ignited")
        ingame_debug_text.content = "Liquid fuel engine ignited"
        vessel.control.activate_next_stage()                    # Stage 4 liquid fuel engine ignition

        while True:
            # Based on the current velocity, take corrective actions
            current_vertical_speed = static_FOR.speed
            current_feedback = current_vertical_speed/target_vertical_speed
            pid_controller.update(feedback_value=current_feedback)

            # Fetch the output from the PID controller
            pid_current_output = pid_controller.output
            output = pid_current_output/pid_initial_output

            # Feed the output to the control interface of the vessel
            vessel.control.throttle = output

            # Log
            writer.writerow(['1', str(static_FOR.speed), str(output)])

            # TODO: Include more robust algorithm to detect stability
            # If the speed is getting settled down, i.e. instantaneous differential of the feedback is close to 0
            instantaneous_diff = (current_feedback - previous_feedback)/0.001
            if abs(instantaneous_diff) < 0.001:
                print("Vessel settled at target velocity of %f" % (target_vertical_speed))
                target_vertical_speed_reached = True

            # Debug
            print("Vertical speed - %f, feedback - %f, output - %f, instantaneous diff - %f\r"
                  % (current_vertical_speed, current_feedback, output, instantaneous_diff)),

            if 51000 < vessel.flight().mean_altitude < 53000 and target_vertical_speed_reached:
                # Shut down the engines
                vessel.control.throttle = 0

                vessel.auto_pilot.target_pitch_and_heading(0, 90)
                vessel.auto_pilot.engage()

                print("Hammer SRB test criteria satisfied, engines shut down. Staging to jettison liquid fuel tanks..")
                time.sleep(1.5)
                vessel.control.activate_next_stage()            # Tanks jettisoned

                print("Igniting Hammer SRB..")
                time.sleep(0.5)
                vessel.control.activate_next_stage()            # Hammer SRB ignited
                break

            # Keep track of the feedback
            previous_feedback = current_feedback

            time.sleep(0.05)

        while vessel.resources.amount('SolidFuel') > 0:       # The last SRB
            time.sleep(0.1)

        vessel.auto_pilot.target_pitch_and_heading(-90, 90)
        time.sleep(5.0)
        print("Separating the tested Hammer SRB..")
        vessel.control.activate_next_stage()

        # TODO: Proper reentry routine
        while True:
            if 1000 > vessel.flight().mean_altitude:
                print("Deploying parachutes..")
                vessel.control.activate_next_stage()
                break
            else:
                time.sleep(0.5)
