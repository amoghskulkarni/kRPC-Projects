import krpc
import time
import PID

data_dictionary_list = [{'filename': "output/data1.csv", 'pid_settings': (0.4, 0.02, 0.01)},
                        {'filename': "output/data2.csv", 'pid_settings': (4.0, 0.2, 0.1)},
                        {'filename': "output/data3.csv", 'pid_settings': (0.4, 0.1, 0.02)},
                        {'filename': "output/data4.csv", 'pid_settings': (0.4, 0.1, 0.1)},
                        ]
data_dictionary_list_index = 0

if __name__ == "__main__":
    conn = krpc.connect(name='Kerbin survey by airplane')
    vessel = conn.space_center.active_vessel
    wp_manager = conn.space_center.waypoint_manager

    # Target velocity of the vessel
    print("Launching " + vessel.name + " for a Kerbin survey of the site " + wp_manager.waypoints[1].name)

    # UI element for displaying text in the game (mostly for debugging purposes)
    canvas = conn.ui.stock_canvas
    screen_size = canvas.rect_transform.size                # Get the size of the game window in pixels
    panel = canvas.add_panel()                              # Add a panel to contain the UI elements
    rect = panel.rect_transform                             # Position the panel on the left of the screen
    rect.size = (300, 100)
    rect.position = (110 - (screen_size[0] / 2), 0)
    # Add some text displaying the name of the waypoint
    ingame_debug_text = panel.add_text("Waypoint: " + wp_manager.waypoints[1].name)
    # Position the panel on the left of the screen
    rect = panel.rect_transform
    rect.size = (300, 100)
    rect.position = (110 - (screen_size[0] / 2), 0)

    # # PID controller initialization
    pid_settings = data_dictionary_list[data_dictionary_list_index]['pid_settings']
    pid_controller = PID.PID(P=pid_settings[0], I=pid_settings[1], D=pid_settings[2])
    pid_controller.setSetpoint(1)                           # target_velocity / target_velocity
    pid_controller.update(feedback_value=0)
    pid_initial_output = pid_controller.output
    print("PID initial output - " + str(pid_initial_output))

    # Full throttle
    vessel.control.throttle = 1.0

    # Take-off!
    print("Take-off!")
    vessel.control.activate_next_stage()

    # At first couple stages, we can have SAS on and auto_pilot disengaged
    # As soon as we engage autopilot, SAS goes off
    vessel.control.sas = True

    # Get the flight object for the frame-of-reference of the planet
    # static_FOR = vessel.flight(vessel.orbit.body.reference_frame)
    static_FOR = vessel.flight(vessel.orbit.body.reference_frame)

    while True:
        if static_FOR.speed > 100.0:
            break

    time_now = int(time.time())
    ingame_debug_text.content = "pitch - 1"
    while int(time.time()) < time_now + 10:
        time.sleep(0.1)
        vessel.control.pitch = 1

    time_now = int(time.time())
    ingame_debug_text.content = "pitch - 0"
    while int(time.time()) < time_now + 1:
        time.sleep(0.1) 
        vessel.control.pitch = 0

    time.sleep(2)


    # previous_feedback = 0
    # current_feedback = 0
    #
    # # Now, we can engage the autopilot and point the ship according to desired pitch and heading
    # # vessel.auto_pilot.target_pitch_and_heading(75, 90)
    # # vessel.auto_pilot.engage()
    #
    # print("Liquid fuel engine ignited")
    # ingame_debug_text.content = "Liquid fuel engine ignited"
    # vessel.control.activate_next_stage()                    # Stage 4 liquid fuel engine ignition
    #
    # while True:
    #     # Based on the current velocity, take corrective actions
    #     current_vertical_speed = static_FOR.speed
    #     current_feedback = current_vertical_speed/target_vertical_speed
    #     pid_controller.update(feedback_value=current_feedback)
    #
    #     # Fetch the output from the PID controller
    #     pid_current_output = pid_controller.output
    #     output = pid_current_output/pid_initial_output
    #
    #     # Feed the output to the control interface of the vessel
    #     vessel.control.throttle = output
    #
    #     # TODO: Include more robust algorithm to detect stability
    #     # If the speed is getting settled down, i.e. instantaneous differential of the feedback is close to 0
    #     instantaneous_diff = (current_feedback - previous_feedback)/0.001
    #     if abs(instantaneous_diff) < 0.001:
    #         print("Vessel settled at target velocity of %f" % (target_vertical_speed))
    #         target_vertical_speed_reached = True
    #
    #     # Debug
    #     print("Vertical speed - %f, feedback - %f, output - %f, instantaneous diff - %f\r"
    #           % (current_vertical_speed, current_feedback, output, instantaneous_diff)),
    #
    #     if 51000 < vessel.flight().mean_altitude < 53000 and target_vertical_speed_reached:
    #         # Shut down the engines
    #         vessel.control.throttle = 0
    #
    #         vessel.auto_pilot.target_pitch_and_heading(0, 90)
    #         vessel.auto_pilot.engage()
    #
    #         print("Hammer SRB test criteria satisfied, engines shut down. Staging to jettison liquid fuel tanks..")
    #         time.sleep(1.5)
    #         vessel.control.activate_next_stage()            # Tanks jettisoned
    #
    #         print("Igniting Hammer SRB..")
    #         time.sleep(0.5)
    #         vessel.control.activate_next_stage()            # Hammer SRB ignited
    #         break
    #
    #     # Keep track of the feedback
    #     previous_feedback = current_feedback
    #
    #     time.sleep(0.05)
    #
    # while vessel.resources.amount('SolidFuel') > 0:       # The last SRB
    #     time.sleep(0.1)
    #
    # vessel.auto_pilot.target_pitch_and_heading(-90, 90)
    # time.sleep(5.0)
    # print("Separating the tested Hammer SRB..")
    # vessel.control.activate_next_stage()
    #
    # # TODO: Proper reentry routine
    # while True:
    #     if 1000 > vessel.flight().mean_altitude:
    #         print("Deploying parachutes..")
    #         vessel.control.activate_next_stage()
    #         break
    #     else:
    #         time.sleep(0.5)
